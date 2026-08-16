from PIL import Image
import piexif
import os
import argparse

# Register HEIC support (optional but recommended)
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass


def copy_metadata(original_path: str, new_image_path: str, output_path: str = None):
    """
    Copy EXIF metadata from the original image to the new image.
    
    Args:
        original_path: Path to the original image (with metadata)
        new_image_path: Path to the edited/new image
        output_path: Where to save the result (default: overwrites new_image_path)
    """
    if not os.path.exists(original_path):
        print(f"Error: Original image not found → {original_path}")
        return
    if not os.path.exists(new_image_path):
        print(f"Error: New image not found → {new_image_path}")
        return

    if output_path is None:
        output_path = new_image_path

    try:
        # --- Load original EXIF ---
        original = Image.open(original_path)
        exif_dict = piexif.load(original.info.get("exif", b""))

        # --- Load new image ---
        new_img = Image.open(new_image_path)

        # Convert to RGB if needed (important for some formats)
        if new_img.mode in ("RGBA", "P"):
            new_img = new_img.convert("RGB")

        # --- Inject the original EXIF into the new image ---
        exif_bytes = piexif.dump(exif_dict)

        # Save
        new_img.save(output_path, exif=exif_bytes, quality=95)
        print(f"✅ Metadata successfully copied!")
        print(f"   Original : {os.path.basename(original_path)}")
        print(f"   New image: {os.path.basename(new_image_path)}")
        print(f"   Saved to : {output_path}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Copy EXIF metadata from original image to a new image")
    parser.add_argument("original", help="Path to the original image (with metadata)")
    parser.add_argument("new_image", help="Path to the new/edited image")
    parser.add_argument("-o", "--output", help="Output path (optional). If not given, overwrites the new image")
    args = parser.parse_args()

    copy_metadata(args.original, args.new_image, args.output)