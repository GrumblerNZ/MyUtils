from PIL import Image
import piexif
import os
import argparse

# Enable HEIC support
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass


def copy_metadata(original_path: str, new_image_path: str, output_path: str = None):
    if not os.path.exists(original_path):
        print(f"Error: Original image not found → {original_path}")
        return
    if not os.path.exists(new_image_path):
        print(f"Error: New image not found → {new_image_path}")
        return

    if output_path is None:
        output_path = new_image_path

    try:
        # Open original and extract full EXIF
        original = Image.open(original_path)
        
        # Try to get raw EXIF bytes
        exif_bytes = original.info.get("exif")
        
        if not exif_bytes:
            print("No EXIF data found in the original image.")
            return

        # Load into piexif
        exif_dict = piexif.load(exif_bytes)

        print("Copying all available metadata (including GPS if present)...")

        # Open the new (edited) image
        new_img = Image.open(new_image_path)

        if new_img.mode in ("RGBA", "P"):
            new_img = new_img.convert("RGB")

        # Dump EXIF (including GPS)
        new_exif_bytes = piexif.dump(exif_dict)

        # Save with original metadata
        new_img.save(output_path, "jpeg", exif=new_exif_bytes, quality=95)
        
        print(f"\n✅ Metadata copy completed")
        print(f"   Saved to: {output_path}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Copy EXIF + GPS metadata")
    parser.add_argument("original", help="Original image (with GPS)")
    parser.add_argument("new_image", help="Edited image")
    parser.add_argument("-o", "--output", help="Output file (recommended)")
    args = parser.parse_args()

    copy_metadata(args.original, args.new_image, args.output)