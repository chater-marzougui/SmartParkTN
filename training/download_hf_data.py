import os
import zipfile
import shutil
import json
from pathlib import Path
from huggingface_hub import hf_hub_download

# Define constants
REPO_ID = "keremberke/license-plate-object-detection"
DATA_DIR = Path("data")
LABELED_DIR = DATA_DIR / "labeled"
IMAGES_DIR = LABELED_DIR / "images"
LABELS_DIR = LABELED_DIR / "labels"

# Create target directories
for split in ["train", "val", "test"]:
    (IMAGES_DIR / split).mkdir(parents=True, exist_ok=True)
    (LABELS_DIR / split).mkdir(parents=True, exist_ok=True)

tmp_dir = DATA_DIR / "tmp"
tmp_dir.mkdir(parents=True, exist_ok=True)

splits = {
    "train": "data/train.zip",
    "val": "data/valid.zip",
    "test": "data/test.zip"
}

def coco_to_yolo(coco_json_path, split_name, img_dir):
    with open(coco_json_path, 'r') as f:
        coco = json.load(f)
        
    # Create mapping from image_id to filename and dimensions
    img_dict = {}
    for img in coco['images']:
        img_dict[img['id']] = {
            'file_name': img['file_name'],
            'width': img['width'],
            'height': img['height']
        }
        # Move image to final directory
        src_img = img_dir / img['file_name']
        dst_img = IMAGES_DIR / split_name / img['file_name']
        if src_img.exists():
            shutil.move(str(src_img), str(dst_img))
            
    # Process annotations
    # Group by image_id
    anno_dict = {}
    for ann in coco['annotations']:
        img_id = ann['image_id']
        if img_id not in anno_dict:
            anno_dict[img_id] = []
        anno_dict[img_id].append(ann)
        
    for img_id, img_info in img_dict.items():
        txt_name = Path(img_info['file_name']).stem + '.txt'
        txt_path = LABELS_DIR / split_name / txt_name
        
        with open(txt_path, 'w') as f:
            if img_id in anno_dict:
                for ann in anno_dict[img_id]:
                    # COCO bbox: [x_min, y_min, width, height]
                    x_min, y_min, w, h = ann['bbox']
                    # YOLO: x_center, y_center, width, height normalized
                    img_w = img_info['width']
                    img_h = img_info['height']
                    
                    x_center = (x_min + w / 2) / img_w
                    y_center = (y_min + h / 2) / img_h
                    norm_w = w / img_w
                    norm_h = h / img_h
                    
                    # Force class 0 
                    f.write(f"0 {x_center} {y_center} {norm_w} {norm_h}\n")
                    
def extract_and_convert(zip_path, split_name):
    print(f"Extracting {zip_path}...")
    
    # Empty tmp dir
    for item in tmp_dir.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()
            
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(tmp_dir)
        
    json_path = tmp_dir / "_annotations.coco.json"
    if json_path.exists():
        print(f"Converting COCO labels for {split_name}...")
        coco_to_yolo(json_path, split_name, tmp_dir)
    else:
        print(f"No _annotations.coco.json found in {split_name}")

print("Downloading and processing datasets from HuggingFace...")

for split_name, file_path in splits.items():
    print(f"\nDownloading {split_name} split...")
    downloaded_path = hf_hub_download(repo_id=REPO_ID, filename=file_path, repo_type="dataset")
    extract_and_convert(downloaded_path, split_name)

print("\nCleaning up...")
shutil.rmtree(tmp_dir)
print("Done formatting dataset!")
