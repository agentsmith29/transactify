import os
import zipfile
import requests
from PIL import Image
from io import BytesIO
from cairosvg import svg2png
import sys


# get current working directory
base_dir = ".."
save_dir = os.path.join(base_dir, "icons")




# Process PNG files
def process_png(ref, path_out, sizes = [12, 16, 24, 32, 48]):
    file_name = str(os.path.basename(ref)).replace('.svg', '.png')
   
    with open(ref, "rb") as file:
        # convert the svg file to png
        for size in sizes:
            path_out_ = f"{path_out}_{size}"
            # check if the directory exists, if not create it
            if not os.path.exists(path_out_):
                os.makedirs(path_out_)
            png_filename = os.path.join(f"{path_out_}", file_name)
            print(f"Processing PNG: {ref} -> {png_filename}")
            #, format="PNG"
            svg2png(file_obj=file, write_to=png_filename, background_color="white", output_height=size)
            #resized_image = image.resize((size, size), Image.ANTIALIAS)
            #resized_image.save(
            #    os.path.join(dir_path, os.path.basename(file_name)), format="PNG"
            #)

# Main script
def main():
    svg_base_dir = '/app/static/icons/svg/'
    svg_convert = [
       "lock.svg",
       "cart-check-fill.svg",
       "cart-dash-fill.svg",
       "coin.svg",
       "bootstrap-reboot.svg",
       "person-bounding-box.svg",
       "cart4.svg",
       "cash-stack.svg",
       "person-fill-x.svg",
       "gear-fill.svg",
       "NFC_logo.svg",
       "check-square.svg",
       'x-circle-fill.svg',
    ]
    png_base_dir = '/app/static/icons/png'

    try:
        for svg_in in svg_convert:
            process_png(f"{svg_base_dir}{svg_in}", png_base_dir)
    except Exception as e:
        print(f"Failed to process PNG: {e}")
        print(f"Skipping file: {svg_in}")

if __name__ == "__main__":
    main()
