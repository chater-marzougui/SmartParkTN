import sys
import os
from datetime import datetime, timedelta, timezone
import random
import uuid

# Load environment before any other app imports
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent / ".env")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db import SessionLocal, engine, Base
from app.models.vehicle import Vehicle, VehicleCategory, VehicleType
from app.models.event import Event, EventType, DecisionType
from app.models.session import Session, PaymentStatus
from app.models.decision import Decision, DecisionOutcome
from app.models.tariff import Tariff
from app.models.rule import Rule
from app.models.alert import Alert, AlertType, AlertSeverity

def clear_data(db):
    print("Clearing existing data (except users)...")
    db.query(Session).delete()
    db.query(Decision).delete()
    db.query(Event).delete()
    db.query(Vehicle).delete()
    db.query(Alert).delete()
    db.query(Tariff).delete()
    db.query(Rule).delete()
    db.commit()

def load_seed_data():
    db = SessionLocal()
    try:
        clear_data(db)

        # 1. Rules
        rules = [
            Rule(key="grace_period_minutes", value={"minutes": 15}, description="Minutes before billing starts"),
            Rule(key="max_overstay_hours", value={"hours": 24}, description="Threshold for alerting overstays"),
            Rule(key="blacklist_action", value={"action": "deny"}, description="Action when blacklisted vehicle arrives")
        ]
        db.add_all(rules)

        # 2. Tariffs
        t_car = Tariff(name="Standard Car", vehicle_types=["car"], first_hour_tnd=2.0, extra_hour_tnd=1.0, daily_max_tnd=20.0)
        t_truck = Tariff(name="Standard Truck", vehicle_types=["truck"], first_hour_tnd=4.0, extra_hour_tnd=2.0, daily_max_tnd=40.0)
        t_moto = Tariff(name="Motorcycle", vehicle_types=["motorcycle"], first_hour_tnd=1.0, extra_hour_tnd=0.5, daily_max_tnd=10.0)
        db.add_all([t_car, t_truck, t_moto])
        db.commit()

        # 3. Vehicles
        now = datetime.now(timezone.utc)
        
        plates = [
            ("205 TN 1234", VehicleCategory.vip, VehicleType.car, "CEO (Mr. Flen)", None),
            ("198 TN 5555", VehicleCategory.subscriber, VehicleType.car, "Dr. Ahmed", now + timedelta(days=30)),
            ("200 TN 7777", VehicleCategory.subscriber, VehicleType.car, "Maha Ben Ali", now - timedelta(days=5)), # Expired
            ("155 TN 2222", VehicleCategory.blacklist, VehicleType.truck, "Unknown", None),
            ("210 TN 3333", VehicleCategory.blacklist, VehicleType.car, "Unknown", None),
        ]
        
        vehicles_dict = {}
        for p_norm, cat, v_type, owner, exp in plates:
            v = Vehicle(
                plate=p_norm,
                plate_normalized=p_norm.replace(" ", ""),
                category=cat,
                vehicle_type=v_type,
                owner_name=owner,
                subscription_expires=exp,
                notes="Seeded vehicle"
            )
            db.add(v)
            db.commit()
            db.refresh(v)
            vehicles_dict[p_norm] = v
            
        # Visitors (no pre-registration strictly required, but let's add some for historical reference)
        visitor_plates = [f"{random.randint(180, 240)} TN {random.randint(1000, 9999)}" for _ in range(15)]
        for p in visitor_plates:
            v = Vehicle(
                plate=p,
                plate_normalized=p.replace(" ", ""),
                category=VehicleCategory.visitor,
                vehicle_type=VehicleType.car
            )
            db.add(v)
            db.commit()
            db.refresh(v)
            vehicles_dict[p] = v

        # 4. Events, Sessions, Decisions
        print("Generating historical active/closed sessions and events...")
        gates_in = ["gate_main_in", "gate_back_in"]
        gates_out = ["gate_main_out", "gate_back_out"]
        
        all_plates = list(vehicles_dict.keys())
        
        # Historical Closed Sessions (Over the last 7 days)
        for _ in range(35):
            p = random.choice(all_plates)
            v = vehicles_dict[p]
            
            # Skip blacklist for normal entries
            if v.category == VehicleCategory.blacklist:
                continue
            
            # Entry 1 to 7 days ago
            entry_time = now - timedelta(days=random.randint(1, 7), hours=random.randint(0, 23), minutes=random.randint(0, 59))
            duration_mins = random.randint(15, 300) # 15 mins to 5 hours
            exit_time = entry_time + timedelta(minutes=duration_mins)
            
            # Create Entry Event
            ev_in = Event(
                plate=v.plate, vehicle_id=v.id, gate_id=random.choice(gates_in), 
                event_type=EventType.entry, ocr_confidence=random.uniform(0.88, 0.99), timestamp=entry_time
            )
            db.add(ev_in)
            db.commit()
            
            # Create Decision Allow
            dec_in = Decision(
                event_id=ev_in.id, plate=v.plate, outcome=DecisionOutcome.allow,
                reason_code=v.category.value.upper(), rule_ref="standard_access",
                timestamp=entry_time
            )
            db.add(dec_in)
            
            # Create Exit Event
            ev_out = Event(
                plate=v.plate, vehicle_id=v.id, gate_id=random.choice(gates_out), 
                event_type=EventType.exit, ocr_confidence=random.uniform(0.85, 0.99), timestamp=exit_time
            )
            db.add(ev_out)
            db.commit()
            
            # Calculate amount due (approx)
            amount = 0
            if v.category == VehicleCategory.visitor:
                hours = (duration_mins // 60) + 1
                amount = 2.0 + (hours - 1) * 1.0
            
            # Create closed session
            sess = Session(
                plate=v.plate, vehicle_id=v.id,
                entry_event_id=ev_in.id, exit_event_id=ev_out.id,
                entry_time=entry_time, exit_time=exit_time,
                duration_minutes=duration_mins,
                tariff_id=t_car.id,
                amount_due=amount,
                payment_status=PaymentStatus.paid if amount > 0 else PaymentStatus.waived,
                gate_entry=ev_in.gate_id, gate_exit=ev_out.gate_id
            )
            db.add(sess)
            db.commit()

        # Active Sessions (Parked right now)
        print("Generating active (currently parked) sessions...")
        active_parkers = random.sample(all_plates, 8)
        for p in active_parkers:
            v = vehicles_dict[p]
            if v.category == VehicleCategory.blacklist:
                continue
                
            entry_time = now - timedelta(hours=random.randint(0, 5), minutes=random.randint(5, 59))
            ev_in = Event(
                plate=v.plate, vehicle_id=v.id, gate_id=random.choice(gates_in), 
                event_type=EventType.entry, ocr_confidence=0.98, timestamp=entry_time
            )
            db.add(ev_in)
            db.commit()
            
            dec_in = Decision(
                event_id=ev_in.id, plate=v.plate, outcome=DecisionOutcome.allow,
                reason_code=v.category.value.upper(), rule_ref="standard_access",
                timestamp=entry_time
            )
            db.add(dec_in)
            
            sess = Session(
                plate=v.plate, vehicle_id=v.id,
                entry_event_id=ev_in.id,
                entry_time=entry_time,
                tariff_id=t_car.id if v.vehicle_type == VehicleType.car else t_truck.id,
                gate_entry=ev_in.gate_id,
                payment_status=PaymentStatus.pending
            )
            db.add(sess)
            db.commit()

        # 5. Alerts & Denied events
        print("Generating alerts and denied events...")
        # Blacklist tries to enter
        bl_v = vehicles_dict["155 TN 2222"]
        bl_time = now - timedelta(hours=2)
        ev_bl = Event(
            plate=bl_v.plate, vehicle_id=bl_v.id, gate_id=random.choice(gates_in), 
            event_type=EventType.entry, ocr_confidence=0.99, timestamp=bl_time
        )
        db.add(ev_bl)
        db.commit()
        
        dec_bl = Decision(
            event_id=ev_bl.id, plate=bl_v.plate, outcome=DecisionOutcome.deny,
            reason_code="BLACKLIST", rule_ref="security_policy_1",
            timestamp=bl_time, gate_action="close"
        )
        db.add(dec_bl)
        
        # Expired subscriber tries to enter
        exp_v = vehicles_dict["200 TN 7777"]
        exp_time = now - timedelta(hours=1)
        ev_exp = Event(
            plate=exp_v.plate, vehicle_id=exp_v.id, gate_id=random.choice(gates_in), 
            event_type=EventType.entry, ocr_confidence=0.95, timestamp=exp_time
        )
        db.add(ev_exp)
        db.commit()
        
        dec_exp = Decision(
            event_id=ev_exp.id, plate=exp_v.plate, outcome=DecisionOutcome.deny,
            reason_code="EXPIRED_SUBSCRIPTION", rule_ref="sub_policy_2",
            timestamp=exp_time, gate_action="close"
        )
        db.add(dec_exp)

        al1 = Alert(
            alert_type=AlertType.BLACKLIST, severity=AlertSeverity.critical,
            plate=bl_v.plate, gate_id=ev_bl.gate_id,
            message="Blacklisted vehicle attempted to enter.",
            created_at=bl_time
        )
        al2 = Alert(
            alert_type=AlertType.OVERSTAY, severity=AlertSeverity.medium,
            plate="Unknown", gate_id="gate_main_out",
            message="Possible abandoned vehicle in zone B.",
            created_at=now - timedelta(days=2)
        )
        al3 = Alert(
            alert_type=AlertType.PLATE_MISMATCH, severity=AlertSeverity.high,
            plate=exp_v.plate, gate_id=ev_exp.gate_id,
            message="Mismatched vehicle category confidence. Manual review required.",
            created_at=now - timedelta(hours=1)
        )
        db.add_all([al1, al2, al3])
        db.commit()

        print("=== Seed data populated successfully! ===")
        print("Included: Tariffs, Rules, Vehicles (Visitors, VIPs, Subs, Blacklist), historic sessions, active sessions, alerts.")

    except Exception as e:
        print("Error while seeding data:", e)
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    load_seed_data()
