import glob
import os
import cv2
import numpy as np
from PIL import Image

print("=" * 50)
print(" PHOTO DATE REMOVAL SCRIPT (YELLOW/ORANGE)")
print("=" * 50)

input_dir = input("\nEnter the full path of the folder with photos to clean:\n> ").strip().strip('"')

if not os.path.exists(input_dir):
    print("Error: The specified folder does not exist!")
    input("Press Enter to exit...")
    exit()

output_dir = os.path.join(input_dir, "Cleaned")
os.makedirs(output_dir, exist_ok=True)

extensions = ("*.jpg", "*.JPG", "*.jpeg", "*.JPEG")
files = []
for ext in extensions:
    files.extend(glob.glob(os.path.join(input_dir, ext)))
files = sorted(list(set(files)))
total = len(files)

if total == 0:
    print("No JPG photos found in this folder.")
    input("Press Enter to exit...")
    exit()

print(f"\nFound {total} images to process.")

lower_bound = np.array([22, 180, 180])
upper_bound = np.array([33, 255, 255])
kernel = np.ones((5, 5), np.uint8)

for i, f in enumerate(files):
    img = cv2.imread(f)
    if img is None:
        continue

    h, w = img.shape[:2]
    roi_h_start, roi_w_start = int(h * 0.85), int(w * 0.70)

    roi = img[roi_h_start:h, roi_w_start:w]
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    if np.count_nonzero(mask) > 5:
        mask = cv2.dilate(mask, kernel, iterations=1)
        inpainted_roi = cv2.inpaint(roi, mask, 3, cv2.INPAINT_NS)
        img[roi_h_start:h, roi_w_start:w] = inpainted_roi

    filename = os.path.basename(f)
    
    # Read EXIF data directly with Pillow
    exif_bytes = b""
    try:
        with Image.open(f) as original_pil:
            exif_bytes = original_pil.info.get("exif", b"")
    except Exception:
        pass

    # Save output preserving EXIF
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img_rgb)
    
    save_kwargs = {"quality": 95}
    if exif_bytes:
        save_kwargs["exif"] = exif_bytes

    pil_img.save(os.path.join(output_dir, filename), "JPEG", **save_kwargs)

    if (i + 1) % 10 == 0 or (i + 1) == total:
        print(f"Processed {i+1}/{total}")

print(f"\nProcessing completed! Cleaned photos saved in: {output_dir}")