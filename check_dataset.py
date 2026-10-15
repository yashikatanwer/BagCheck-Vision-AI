import os

base = "dataset"

for split in ["train", "val"]:
    image_dir = os.path.join(base, "images", split)
    label_dir = os.path.join(base, "labels", split)

    images = [
        f for f in os.listdir(image_dir)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    missing = []

    for image in images:
        label = os.path.splitext(image)[0] + ".txt"
        if not os.path.exists(os.path.join(label_dir, label)):
            missing.append(image)

    print(f"\n{split.upper()}")
    print(f"Images: {len(images)}")
    print(f"Missing labels: {len(missing)}")

    if missing:
        for item in missing:
            print(" -", item)

print("\nDataset check complete!")