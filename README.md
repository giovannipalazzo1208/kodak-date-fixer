# Kodak EasyShare C1013 – Photo Date Fix (EXIF Date Overlay)

Python scripts to work around a hardware/firmware limitation of the **Kodak EasyShare C1013**: the camera's internal clock/calendar does not accept dates past **2025**, so the date automatically burned into photos (bottom-right corner, in yellow/orange) gets stuck and no longer matches the actual shooting date.

These two scripts let you:
1. **Remove** the wrong date burned into the photo by the camera (`RemovePhotoData.py`).
2. **Add** a new, correct date in the same style, read from the file's EXIF metadata (`AddPhotoData.py`).

## Why this project exists

The C1013 burns the date directly into the image pixels (not just into metadata), using the typical yellow/orange "Kodak" color seen on 2000s-era digital cameras. Since the camera's clock can't be set past 2025, every photo taken after that point ends up with an incorrect date stamped on it.

The workflow adopted:
1. Manually fix the date in the photo's EXIF metadata from a PC.
2. Remove the wrong date burned into the photo by the camera (`RemovePhotoData.py`).
3. Re-draw the correct date, in the same style/position, read from the EXIF data just corrected (`AddPhotoData.py`).

## Requirements

- Python 3.8+
- Libraries:
  ```bash
  pip install opencv-python numpy pillow
  ```
- An EXIF editor to manually fix the "Date taken" field (e.g. ExifTool, Adobe Bridge, or a GUI tool like ExifToolGUI / FastStone Image Viewer on Windows). This step is **not** automated by these scripts.
- A bold monospace font installed on the system for a result closer to the original style (the script already has fallbacks, see below):
  - Windows: `Courier New Bold` (`courbd.ttf`)
  - macOS: `Courier New Bold.ttf`
  - Linux: `msttcorefonts` package (`courier_bold`)

## Full workflow

1. **Manually fix the EXIF date from your PC**
   Open the photo with an EXIF editor and correct the "Date taken" field with the actual shooting date (the one the camera failed to set correctly).

2. **Remove the date burned into the photo** → run `RemovePhotoData.py`
   - Asks for the path of the folder containing the photos to clean.
   - Scans the bottom-right corner of each image (last 15% of height, last 30% of width) looking for pixels in the Kodak yellow/orange color range (HSV `H:22–33, S:180–255, V:180–255`).
   - If enough matching pixels are found (threshold: more than 5 pixels), it dilates the mask and uses `cv2.inpaint` (Navier-Stokes algorithm) to reconstruct that area without the burned-in text.
   - Saves the processed images into a new **`Cleaned`** subfolder, preserving the original file's EXIF data.

3. **Add the correct date to the photo** → run `AddPhotoData.py`
   - Asks for the path of the folder containing the photos (typically the `Cleaned` folder from the previous step).
   - Reads the `DateTimeOriginal` EXIF tag of each image (the one manually corrected in step 1) and formats it as `DD/MM/YYYY`.
   - If the EXIF data doesn't contain that tag, falls back to the file's last-modified date.
   - Draws the date text in the bottom-right corner, with font size proportional to the image height (3.5% of height, minimum 24px) and Kodak-style yellow/orange color (`RGB 255, 210, 10`) to match the camera's original look.
   - Saves the resulting images into a new **`WithDate`** subfolder, preserving EXIF data.

## Technical details per script

### `RemovePhotoData.py` — burned-in date removal
- Supported formats: `.jpg`, `.JPG`, `.jpeg`, `.JPEG`.
- Only works on a region of interest (ROI) in the bottom-right corner, not the whole image, for speed and to avoid false positives elsewhere in the photo.
- If not enough yellow pixels are detected, the image is left unchanged (useful for photos where the date isn't visible or falls outside the expected color range).
- JPEG save quality: 95.
- Output: `Cleaned` subfolder inside the input folder.

### `AddPhotoData.py` — EXIF date overlay
- Same supported formats.
- Looks up system fonts from a list of predefined paths (Windows/macOS/Linux); if none is found, falls back to Pillow's default font (`ImageFont.load_default()`), which is smaller and less close to the original Kodak style — installing one of the listed fonts is recommended for better results.
- Padding around the text is calculated proportionally to the text size itself.
- JPEG save quality: 95.
- Output: `WithDate` subfolder inside the input folder.

## Known limitations

- Color-based detection of the burned-in date can fail on photos with a lot of natural yellow/orange in the bottom-right corner (e.g. sunsets, warm lighting), causing false positives or missed removal.
- The EXIF correction (step 1) is manual: these scripts don't touch metadata, only image pixels.
- The date-overlay script assumes the `DD/MM/YYYY` format; if you prefer `MM/DD/YYYY` or another format, edit the formatting line in the code.
- Both scripts only process JPG files; other formats (PNG, RAW/DNG...) are not handled.

## License

Add your preferred license here (e.g. MIT) before publishing.