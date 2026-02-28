# Training Pipeline Overview and Next Steps

This directory contains the pipeline to fetch datasets from Hugging Face and train the YOLOv8 license plate detector model, followed by setup for the OCR model training. The Python environment is already created (`venv`) with `datasets`, `huggingface_hub`, `ultralytics`, `opencv-python`, and `pyyaml` installed.

## Current Goal

The goal is to automatically download a public Hugging Face dataset consisting of cars and their license plates (with bounding boxes), parse and restructure that dataset locally into a layout compatible with YOLO `plates.yaml`, and finally execute the training run.

## Next Steps for the AI Developer

### 1. Download & Format Dataset for YOLO
You need to write a Python script (e.g., `download_hf_data.py`) to systematically fetch a license plate detection dataset and convert it into the standard YOLO folder structure:
- Images in: `data/labeled/images/{train,val,test}`
- Labels in: `data/labeled/labels/{train,val,test}` (as `.txt` files containing: `class_id x_center y_center width height` normalized between `0.0` and `1.0`).

**Recommended Dataset:** Let's look for a valid dataset that has bounding boxes (e.g., `UniDataPro/license-plate-detection` or `charliexu07/license_plates_2`, ensure you verify their row schema first). Skip datasets requiring downloading remote scripts (`trust_remote_code`) if possible to prevent errors. Ensure the class mapping is `0: plate`.

### 2. Update Configuration (`plates.yaml`)
Ensure that the paths inside `plates.yaml` match the directories that your Python downloader script creates. The current `plates.yaml` expects:
```yaml
path: data          
train: labeled/images/train
val:   labeled/images/val
test:  labeled/images/test
nc: 1               
names:
  0: plate
```

### 3. Run the Detector Training
Once the dataset is properly structured in the `data/` folder, run the training script:
```bash
python train_detector.py --epochs 50 --batch 16 --imgsz 640
```
This script will leverage the YOLO framework (already in the script `train_detector.py`) to fine-tune `yolov8n.pt`. The best model checkpoints should automatically be moved to the `models/plate_detector.pt` directory when it wraps up.

### 4. OCR / Text Extraction Pipeline (Future Phase)
Once YOLO correctly detects regions cropping out the license plate, the secondary step is text extraction (Arabic + Digits), using EasyOCR or fine-tuning an OCR engine. The current setup is pending, and documentation on embeddings/LLMs will be set up later for the RAG component.

---
**Environment Note:** 
Always activate the virtual environment located at `training/venv/` before running python scripts in context.
```powershell
.\venv\Scripts\activate
```