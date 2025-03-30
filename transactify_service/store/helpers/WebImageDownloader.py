import os
import mimetypes
import threading
import requests
from urllib.parse import urlparse
from django.conf import settings
#class settings:
#    STATIC_ROOT = './'
#   STATIC_URL = './'

from PIL import Image, UnidentifiedImageError
import logging

# Ensure WebP is recognized by mimetypes (not included by default)
mimetypes.add_type('image/webp', '.webp')

class WebImageDownloader:
    def __init__(self, url: str, filename: str):
        self.logger = logging.getLogger(__name__)
        self.url = url
        self.filename = os.path.abspath(filename)

        if not (self.url.startswith("http://") or self.url.startswith("https://")):
            raise ValueError("Invalid URL: Must start with http:// or https://")

        if not self.filename.startswith(os.path.abspath(settings.STATIC_ROOT)):
            raise ValueError(
                f"Image path '{self.filename}' must be within STATIC_ROOT {os.path.abspath(settings.STATIC_ROOT)}"
            )

        # Ensure directory exists
        directory = os.path.dirname(self.filename)
        os.makedirs(directory, exist_ok=True)

        # Static path (served via nginx)
        self.static_path = self.filename.replace(
            os.path.abspath(settings.STATIC_ROOT),
            settings.STATIC_URL.rstrip("/")
        ).replace(os.sep, "/")

    def _validate_image_file(self):
        if not os.path.exists(self.filename):
            raise FileNotFoundError(f"File not found: {self.filename}")

        try:
            with Image.open(self.filename) as img:
                img.verify()  # Verifies image integrity
        except UnidentifiedImageError:
            raise ValueError("Downloaded file is not a valid image.")

    def _get_actual_format(self):
        try:
            with Image.open(self.filename) as img:
                return img.format.lower()  # e.g., 'jpeg', 'png', 'webp'
        except UnidentifiedImageError:
            return None

    def _fix_extension(self, content_type=None):
        actual_format = self._get_actual_format()
        if not actual_format:
            raise ValueError("Could not determine image format for extension fix.")

        # Manual fallback for known formats
        if actual_format == 'webp':
            expected_ext = '.webp'
        else:
            expected_ext = mimetypes.guess_extension(f'image/{actual_format}')

        if not expected_ext:
            raise ValueError(f"Unsupported image format: {actual_format}. No known extension.")

        current_ext = os.path.splitext(self.filename)[1]
        if current_ext.lower() != expected_ext.lower():
            corrected = os.path.splitext(self.filename)[0] + expected_ext
            os.rename(self.filename, corrected)
            self.filename = corrected
            self.static_path = self.filename.replace(
                os.path.abspath(settings.STATIC_ROOT),
                settings.STATIC_URL.rstrip("/")
            ).replace(os.sep, "/")

    def download(self):
        response = requests.get(self.url, stream=True)
        if response.status_code != 200:
            raise IOError(f"Failed to download image: {response.status_code}")

        with open(self.filename, "wb") as out_file:
            for chunk in response.iter_content(chunk_size=8192):
                out_file.write(chunk)

        self._validate_image_file()
        self._fix_extension(response.headers.get("Content-Type", ""))

        return self.filename, self.static_path

    def download_in_background(self, callback=None):
        def _thread_target():
            try:
                filepath, static_path = self.download()
                if callback:
                    callback(success=True, filepath=filepath, static_path=static_path)
            except Exception as e:
                if callback:
                    callback(success=False, error=e)

        thread = threading.Thread(target=_thread_target)
        thread.start()
        return thread
    
if __name__ == '__main__':
    url = "https://imgproxy-retcat.assets.schwarz/JhPmQSrUG2C-J9W1k5ob5-dZ9nXzPWKNVX4BEqtXlhw/sm:1/w:427/h:320/cz/M6Ly9wcm9kLWNhd/GFsb2ctbWVkaWEvZGUvMS85MzEyNzk1NDQ3MDA5ODlFMkQ4QkRCMzU/4NkUzNUNGMjRCNUJENkRDMEFBRDg3QzQ5RjM5NTg3OTdDQzQzNUMwLmpwZw.jpg"
    filename = f"{settings.STATIC_ROOT}/images/products/product_11123"
    downloader = WebImageDownloader(url, filename)
    filename, static_path = downloader.download()
    print(f"Downloaded image to {filename}, static path: {static_path}")
