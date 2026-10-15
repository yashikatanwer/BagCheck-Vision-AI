import os
import shutil
import random

random.seed(42)

base = "dataset"

images_train = os.path.join(base, "images", "train")
images_val = os.path.join(base, "images", "val")

labels_train = os.path.join(base, "labels", "train")
labels_val = os.path.join(base, "labels", "val")

os.makedirs(images_val, exist_ok=True)
os.makedirs(labels_val, exist_ok=True)

images = [
    f for f in os.listdir(images_train)
    if f.lower().endswith((".jpg", ".jpeg", ".png"))
]

random.shuffle(images)

val_count = int(len(images) * 0.20)

val_images = images[:val_count]

for image in val_images:

    image_path = os.path.join(images_train, image)

    label_name = os.path.splitext(image)[0] + ".txt"
    label_path = os.path.join(labels_train, label_name)

    if not os.path.exists(label_path):
        print("Missing label:", image)
        continue

    shutil.move(
        image_path,
        os.path.join(images_val, image)
    )

    shutil.move(
        label_path,
        os.path.join(labels_val, label_name)
    )

print(f"Total images: {len(images)}")
print(f"Moved to validation: {len(val_images)}")
print("Dataset split complete!")