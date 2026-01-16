import os
import shutil
import random

SOURCE_DIR = "C:/Users/Admin/Downloads/archive/Train"   # thư mục train ban đầu
DEST_DIR = "C:/Users/Admin/Downloads/dataset"                       # nơi lưu train + val
VAL_RATIO = 0.2                                                # tỉ lệ validation

os.makedirs(DEST_DIR, exist_ok=True)
train_dir = os.path.join(DEST_DIR, "train")
val_dir = os.path.join(DEST_DIR, "val")
os.makedirs(train_dir, exist_ok=True)
os.makedirs(val_dir, exist_ok=True)

for class_name in sorted(os.listdir(SOURCE_DIR)):
    class_path = os.path.join(SOURCE_DIR, class_name)
    if not os.path.isdir(class_path):
        continue

    images = os.listdir(class_path)
    random.shuffle(images)

    split_idx = int(len(images) * (1 - VAL_RATIO))
    train_images = images[:split_idx]
    val_images = images[split_idx:]

    train_class_dir = os.path.join(train_dir, class_name)
    val_class_dir = os.path.join(val_dir, class_name)
    os.makedirs(train_class_dir, exist_ok=True)
    os.makedirs(val_class_dir, exist_ok=True)

    for img in train_images:
        shutil.copy(os.path.join(class_path, img), os.path.join(train_class_dir, img))

    for img in val_images:
        shutil.copy(os.path.join(class_path, img), os.path.join(val_class_dir, img))

print("Done! Dataset đã được chia thành train/val.")
