"""
Seed script — create or reset the superadmin user.

Usage:
    python init_admin.py                        # creates admin/admin123 if not exists
    python init_admin.py --username boss --password secret123
    python init_admin.py --reset                # deletes existing admin and recreates it
"""
import argparse
import sys
from pathlib import Path

# Make sure .env is loaded before importing app modules
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

from app.db import SessionLocal
from app.models.user import User, UserRole
from app.auth import hash_password


def create_superadmin(username: str, password: str, email: str, full_name: str, reset: bool):
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == username).first()

        if existing:
            if not reset:
                print(f"[INFO] User '{username}' already exists (role={existing.role.value}, active={existing.active}).")
                print("       Use --reset to delete and recreate it.")
                return
            db.delete(existing)
            db.commit()
            print(f"[INFO] Existing user '{username}' deleted.")

        user = User(
            username=username,
            full_name=full_name,
            email=email,
            hashed_password=hash_password(password),
            role=UserRole.superadmin,
            active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        print("=" * 50)
        print("  Superadmin created successfully")
        print("=" * 50)
        print(f"  Username : {username}")
        print(f"  Password : {password}")
        print(f"  Email    : {email}")
        print(f"  Role     : superadmin")
        print(f"  ID       : {user.id}")
        print("=" * 50)
        print("  ⚠  Change the password after first login!")
        print("=" * 50)

    finally:
        db.close()


def list_users():
    db = SessionLocal()
    try:
        users = db.query(User).order_by(User.role).all()
        if not users:
            print("[INFO] No users found in the database.")
            return
        print(f"\n{'ID':<38}  {'Username':<20}  {'Role':<12}  {'Active'}")
        print("-" * 85)
        for u in users:
            print(f"{str(u.id):<38}  {u.username:<20}  {u.role.value:<12}  {u.active}")
        print(f"\nTotal: {len(users)} user(s)")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TunisPark admin user management")
    parser.add_argument("--username",  default="admin",               help="Username (default: admin)")
    parser.add_argument("--password",  default="admin123",            help="Password (default: admin123)")
    parser.add_argument("--email",     default="admin@tunispark.tn",  help="Email address")
    parser.add_argument("--name",      default="Administrator",       help="Full name")
    parser.add_argument("--reset",     action="store_true",           help="Delete existing user and recreate")
    parser.add_argument("--list",      action="store_true",           help="List all users and exit")
    args = parser.parse_args()

    if args.list:
        list_users()
        sys.exit(0)

    create_superadmin(
        username=args.username,
        password=args.password,
        email=args.email,
        full_name=args.name,
        reset=args.reset,
    )
