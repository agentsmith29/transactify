import os
import zipfile
import requests
from PIL import Image
from io import BytesIO
from cairosvg import svg2png


# get current working directory
base_dir = "."
save_dir = os.path.join(base_dir, "static", "icons")
# Define directories
SVG_DIR = f"{save_dir}/svg"
PNG_DIRS = {
    16: f"{save_dir}/png_16",
    24: f"{save_dir}/png_24",
    48: f"{save_dir}/png_48",
    64: f"{save_dir}/png_64",
    128: f"{save_dir}/png_128",
    256: f"{save_dir}/png_256",
    512: f"{save_dir}/png_512",
}

# Ensure directories exist
def ensure_directories():
    os.makedirs(SVG_DIR, exist_ok=True)
    for dir_path in PNG_DIRS.values():
        os.makedirs(dir_path, exist_ok=True)

# Download the zip file
def download_zip(url, destination):
    print("Downloading zip file...")
    response = requests.get(url)
    if response.status_code == 200:
        with open(destination, "wb") as file:
            file.write(response.content)
        print("Download complete.")
    else:
        raise Exception(f"Failed to download file: {response.status_code}")

# Extract SVGs and process PNGs
def process_zip(file_path):
    print("Processing zip file...")
    with zipfile.ZipFile(file_path, "r") as zip_ref:
        for file_name in zip_ref.namelist():
            # Extract SVG files
            if file_name.endswith(".svg"):
                svg_filename = extract_svg(zip_ref, file_name)
                process_png(svg_filename, file_name)
               
    print("Processing complete.")

# Extract SVG files
def extract_svg(zip_ref, file_name):
    print(f"Extracting SVG: {file_name}")
    with open(os.path.join(SVG_DIR, os.path.basename(file_name)), "wb") as svg_file:
        svg_file.write(zip_ref.read(file_name))
    return file_name

# Process PNG files
def process_png(ref, file_name):
    print(f"Processing PNG: {file_name.replace('.svg', '.png')}")
    with open(ref, "rb") as file:
        # convert the svg file to png
        for size, dir_path in PNG_DIRS.items():
            png_filename = os.path.join(dir_path, os.path.basename(file_name))
            #, format="PNG"
            svg2png(file_obj = file, write_to=png_filename, background_color="white", output_height=size)
            #resized_image = image.resize((size, size), Image.ANTIALIAS)
            #resized_image.save(
            #    os.path.join(dir_path, os.path.basename(file_name)), format="PNG"
            #)

# Main script
def main():
    ensure_directories()
    zip_url = "https://github.com/twbs/icons/releases/download/v1.11.3/bootstrap-icons-1.11.3.zip"
    zip_path = "bootstrap-icons.zip"
    try:
        download_zip(zip_url, zip_path)
        process_zip(zip_path)
    finally:
        if os.path.exists(zip_path):
            os.remove(zip_path)

if __name__ == "__main__":
    main()
