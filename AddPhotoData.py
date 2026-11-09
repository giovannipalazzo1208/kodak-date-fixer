import glob
import os
import time
from PIL import Image, ImageDraw, ImageFont, ExifTags

print("=" * 50)
print(" ADD PHOTO DATE FROM EXIF SCRIPT")
print("=" * 50)

input_dir = input("\nEnter the full path of the folder with photos:\n> ").strip().strip('"')

if not os.path.exists(input_dir):
    print("Error: The specified folder does not exist!")
    input("Press Enter to exit...")
    exit()

output_dir = os.path.join(input_dir, "WithDate")
os.makedirs(output_dir, exist_ok=True)

extensions = ("*.jpg", "*.JPG", "*.jpeg", "*.JPEG")
files = []
for ext in extensions:
    files.extend(glob.glob(os.path.join(input_dir, ext)))
files = sorted(list(set(files)))
total = len(files)

if total == 0:
    print("No photos found in this folder.")
    input("Press Enter to exit...")
    exit()

print(f"\nFound {total} images. Processing...")

color = (255, 210, 10)  # Classic Kodak Orange/Yellow

for i, f in enumerate(files):
    try:
        with Image.open(f) as img:
            width, height = img.size
            
            # Dynamic font sizing based on image resolution
            font_size = max(24, int(height * 0.035))
            
            # System font resolution fallback
            font = None
            font_paths = [
                r"C:\Windows\Fonts\courbd.ttf",
                "/Library/Fonts/Courier New Bold.ttf",
                "/usr/share/fonts/truetype/msttcorefonts/courier_bold.ttf"
            ]
            for path in font_paths:
                if os.path.exists(path):
                    try:
                        font = ImageFont.truetype(path, font_size)
                        break
                    except Exception:
                        pass
            
            if font is None:
                font = ImageFont.load_default()

            # EXIF Date extraction
            exif = img.getexif()
            date_str = ""

            if exif:
                for tag, value in exif.items():
                    decoded = ExifTags.TAGS.get(tag, tag)
                    if decoded == "DateTimeOriginal":
                        date_parts = str(value).split(" ")[0].split(":")
                        if len(date_parts) == 3:
                            date_str = f"{date_parts[2]}/{date_parts[1]}/{date_parts[0]}"
                        break

            # Fallback to file modification date
            if not date_str:
                c_time = os.path.getmtime(f)
                t = time.localtime(c_time)
                date_str = time.strftime("%d/%m/%Y", t)

            draw = ImageDraw.Draw(img)
            bbox = draw.textbbox((0, 0), date_str, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # Dynamic padding based on font size
            margin_x = int(text_width * 0.15)
            margin_y = int(text_height * 0.5)

            x = width - text_width - margin_x
            y = height - text_height - margin_y

            draw.text((x, y), date_str, font=font, fill=color)

            exif_bytes = img.info.get("exif", b"")
            save_kwargs = {"quality": 95}
            if exif_bytes:
                save_kwargs["exif"] = exif_bytes

            img.save(os.path.join(output_dir, os.path.basename(f)), "JPEG", **save_kwargs)

    except Exception as e:
        print(f"Error processing {os.path.basename(f)}: {e}")

    if (i + 1) % 10 == 0 or (i + 1) == total:
        print(f"Processed {i+1}/{total}")

print(f"\nCompleted! Photos with date saved in: {output_dir}")