# Place labeled YOLO dataset images here.
# Directory structure expected:
#   data/labeled/images/train/  ← training images (.jpg/.png)
#   data/labeled/images/val/    ← validation images
#   data/labeled/images/test/   ← test images
#   data/labeled/labels/train/  ← YOLO format .txt labels (one per image)
#   data/labeled/labels/val/
#   data/labeled/labels/test/
#
# Each label file: one line per bounding box
#   <class_id> <cx> <cy> <width> <height>   (all normalized 0-1)
#   Example:  0 0.512 0.437 0.280 0.095
