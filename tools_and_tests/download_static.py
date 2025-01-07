import os
import requests
from urllib.parse import urlparse

# List of URLs to download
urls = {
    "bootstrap-css": "https://cdn.jsdelivr.net/npm/bootstrap@4.5.2/dist/css/bootstrap.min.css",
    "jquery": "https://code.jquery.com/jquery-3.5.1.min.js",
    "bootstrap-js": "https://cdn.jsdelivr.net/npm/bootstrap@4.5.2/dist/js/bootstrap.bundle.min.js",
    "docsearch-css": "https://cdn.jsdelivr.net/npm/@docsearch/css@3",  # Missing file extension,
    "color-mode-js": "https://cdn.jsdelivr.net/npm/color-mode@1.0.0/dist/color-mode.min.js",
}

# Base directory for static files
base_dir = os.path.join("static", "assets", "dist")

# Create necessary directories
os.makedirs(os.path.join(base_dir, "css"), exist_ok=True)
os.makedirs(os.path.join(base_dir, "js"), exist_ok=True)

# Download files
for name, url in urls.items():
    try:
        # Parse the URL to get the file extension or fallback to .css for docsearch
        parsed_url = urlparse(url)
        file_ext = ".css" if "docsearch" in url and not os.path.splitext(parsed_url.path)[1] else os.path.splitext(parsed_url.path)[1]
        sub_dir = "css" if file_ext == ".css" else "js"
        target_path = os.path.join(base_dir, sub_dir, f"{name}{file_ext}")

        # Download the file
        print(f"Downloading {url}...")
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise error for bad status codes

        # Write the file
        with open(target_path, "wb") as f:
            f.write(response.content)
        print(f"Saved: {target_path}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")
