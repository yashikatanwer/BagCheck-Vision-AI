from collections import Counter
import glob

class_names = {
    0: "Phone",
    1: "Water Bottle",
    2: "Charger",
    3: "Earbuds",
    4: "Keys",
    5: "Lip Gloss",
    6: "Notebook",
    7: "Pen",
    8: "Sanitizer",
    9: "Sunglasses",
    10: "Wallet",
    11: "Tiffin",
    12: "Tissue Paper",
    13: "Towel"
}

counts = Counter()
skipped = []

for file in glob.glob("dataset/labels/train/*.txt"):
    with open(file, "r") as f:
        for line in f:
            parts = line.split()

            if not parts:
                continue

            try:
                class_id = int(parts[0])
                counts[class_id] += 1
            except ValueError:
                skipped.append((file, parts[0]))

print("\nTRAINING DATASET COUNTS\n")

for class_id, name in class_names.items():
    print(f"{name}: {counts[class_id]}")

if skipped:
    print("\nSkipped non-numeric labels:")
    for file, value in skipped:
        print(f"{file} -> {value}")