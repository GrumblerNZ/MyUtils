from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import os
import argparse

# Register HEIC support
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    print("Warning: pillow-heif not installed. HEIC files will not work.")
    print("Install it with: pip install pillow-heif")

def get_decimal_from_dms(dms, ref):
    degrees = float(dms[0])
    minutes = float(dms[1]) / 60.0
    seconds = float(dms[2]) / 3600.0
    if ref in ['S', 'W']:
        degrees = -degrees
        minutes = -minutes
        seconds = -seconds
    return degrees + minutes + seconds

def get_gps_coordinates(exif_data):
    if not exif_data or 'GPSInfo' not in exif_data:
        return None, None

    gps_info = {}
    for key in exif_data['GPSInfo'].keys():
        decode = GPSTAGS.get(key, key)
        gps_info[decode] = exif_data['GPSInfo'][key]

    try:
        lat = get_decimal_from_dms(gps_info['GPSLatitude'], gps_info['GPSLatitudeRef'])
        lon = get_decimal_from_dms(gps_info['GPSLongitude'], gps_info['GPSLongitudeRef'])
        return lat, lon
    except (KeyError, TypeError, ZeroDivisionError):
        return None, None

def get_location_name(lat, lon):
    geolocator = Nominatim(user_agent="image_metadata_extractor")
    try:
        location = geolocator.reverse((lat, lon), language='en', timeout=10)
        return location.address if location else "Location not found"
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        return f"Geocoding error: {e}"

def extract_image_metadata(image_path):
    if not os.path.exists(image_path):
        print(f"Error: File not found → {image_path}")
        return

    try:
        with Image.open(image_path) as image:
            print(f"\n===== Basic Info =====")
            print(f"{'Filename':25}: {os.path.basename(image_path)}")
            print(f"{'Format':25}: {image.format}")
            print(f"{'Size (px)':25}: {image.size[0]} x {image.size[1]}")
            print(f"{'Mode':25}: {image.mode}")

            exif_data = image.getexif()   # better method than _getexif()

            print(f"\n===== EXIF Metadata =====")
            if not exif_data:
                print("No EXIF metadata found.")
                return

            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                if tag == "GPSInfo":
                    continue
                print(f"{tag:25}: {value}")

            # GPS
            lat, lon = get_gps_coordinates(exif_data)
            print(f"\n===== Location =====")
            if lat is not None and lon is not None:
                print(f"{'Latitude':25}: {lat}")
                print(f"{'Longitude':25}: {lon}")
                print(f"{'Location':25}: {get_location_name(lat, lon)}")
            else:
                print("No GPS coordinates found.")

    except Exception as e:
        print(f"Error reading image: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract image metadata and GPS location")
    parser.add_argument("image_path", help="Path to the image file")
    args = parser.parse_args()

    extract_image_metadata(args.image_path)