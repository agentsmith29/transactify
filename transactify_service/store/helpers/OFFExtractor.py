import requests
from bs4 import BeautifulSoup
from django.shortcuts import get_object_or_404
from store.webmodels.StoreProduct import StoreProduct
from transactify_service.settings import CONFIG
from django.conf import settings as django_settings
from store.helpers.WebImageDownloader import WebImageDownloader

import threading
import time
import logging

class OFFExtractor:
    def __init__(self, product: StoreProduct):
        self.product = product
        self.ean = self.product.ean
        self.logger = logging.getLogger(f"{CONFIG.webservice.SERVICE_NAME}.helpers.{self.__class__.__name__}")

        if not self.product:
            raise ValueError(f"Product with EAN {ean} not found.")

        self.api_url = f"https://world.openfoodfacts.org/api/v0/product/{self.ean}.json"
        self.web_url = f"https://world.openfoodfacts.org/product/{self.ean}"

    def fetch_from_api(self):
        """Fetch product information from the OpenFoodFacts API."""
        response = requests.get(self.api_url)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == 1:  # Product found
                return data["product"]
        return None

    def fetch_from_web(self):
        """Fetch product information by scraping the webpage."""
        response = requests.get(self.web_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            product_data = {}

            # Extract Nutri-Score
            nutri_score = soup.select_one(".nutri-score-grade")
            product_data["nutri_score"] = nutri_score.text.strip() if nutri_score else None

            # Extract Nutritional Information
            nutritional_table = soup.select_one(".nutrition_table")
            if nutritional_table:
                rows = nutritional_table.find_all("tr")
                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) >= 2:
                        key = cols[0].text.strip().lower()
                        value = cols[1].text.strip()
                        if "energy" in key and "kcal" in value:
                            product_data["energy_kcal"] = value
                        elif "energy" in key and "kJ" in value:
                            product_data["energy"] = value
                        elif "fat" in key:
                            product_data["fat"] = value
                        elif "carbohydrates" in key:
                            product_data["carbohydrates"] = value
                        elif "sugars" in key:
                            product_data["sugar"] = value
                        elif "fiber" in key:
                            product_data["fiber"] = value
                        elif "proteins" in key:
                            product_data["proteins"] = value
                        elif "salt" in key:
                            product_data["salt"] = value

            # Extract Image URL
            image = soup.select_one(".product-image")
            product_data["image_url"] = image["src"] if image else None

            return product_data
        return None

    def extract(self):
        """Extract the product information from API or fallback to the webpage."""
        data = self.fetch_from_api()
        if not data:
            print("Falling back to scraping the webpage.")
            data = self.fetch_from_web()
        if not data:
            raise ValueError(f"Product with EAN {self.ean} not found.")

        return {
            "Nutri-Score": data.get("nutriscore_grade", data.get("nutri_score")),
            "Energy (kcal)": data.get("nutriments", {}).get("energy-kcal_100g", data.get("energy_kcal")),
            "Energy (kJ)": data.get("nutriments", {}).get("energy-kj_100g", data.get("energy_kj")),
            "Fat": data.get("nutriments", {}).get("fat_100g", data.get("fat")),
            "Carbohydrates": data.get("nutriments", {}).get("carbohydrates_100g", data.get("carbohydrates")),
            "Sugar": data.get("nutriments", {}).get("sugars_100g", data.get("sugar")),
            "Fiber": data.get("nutriments", {}).get("fiber_100g", data.get("fiber")),
            "Proteins": data.get("nutriments", {}).get("proteins_100g", data.get("proteins")),
            "Salt": data.get("nutriments", {}).get("salt_100g", data.get("salt")),
            "Image URL": data.get("image_url") or data.get("image_front_url"),
        }

    @staticmethod
    def download_image(url, filename, logger):
        # check if url or matches {django_settings.STATIC_ROOT}images
        if (not url.startswith(django_settings.STATIC_URL) 
            and not url.startswith(django_settings.STATIC_ROOT)
            and (url.startswith("http") or url.startswith("https"))):
            try:
                logger.info(f"Downloading image from URL: {url}")
                response = requests.get(url)
                # get the type of the image (jpg, png, etc.)
                content_type = response.headers.get('content-type')
                if content_type and 'image' not in content_type:
                    logger.error(f"Invalid image content type: {content_type}")
                    raise ValueError("Invalid image content type.")
                else:
                    type = content_type.split('/')[1]
                    filename = f"{filename}.{type}"
 
                if response.status_code == 200:
                    with open(filename, 'wb') as file:
                        file.write(response.content)
                    return filename
            except Exception as e:
                logger.error(f"Error downloading image: {e}")
            
    

    def extract_and_save(self):
        """Extract the product information and save it to the database."""
        try:
            nutri_facts = self.extract()
            # Assign nutrition facts if available
            if nutri_facts:
                self.product.nutri_score = nutri_facts.get("Nutri-Score")
                self.product.energy_kcal = nutri_facts.get("Energy (kcal)")
                self.product.energy_kj = nutri_facts.get("Energy (kJ)")
                self.product.fat = nutri_facts.get("Fat")
                self.product.carbohydrates = nutri_facts.get("Carbohydrates")
                self.product.sugar = nutri_facts.get("Sugar")
                self.product.fiber = nutri_facts.get("Fiber")
                self.product.proteins = nutri_facts.get("Proteins")
                self.product.salt = nutri_facts.get("Salt")
                
                if self.product.image_source == "openfoodfacts":
                    url = nutri_facts.get("Image URL")
                    filename = f"{settings.STATIC_ROOT}/images/products/product_{self.product.ean}"
                    downloader = WebImageDownloader(url, filename)
                    filename, static_path = downloader.download()
                    self.product.image_url = static_path
                self.logger.info(f"Nutrition facts extracted for product with EAN {self.ean}.")
            self.product.save()

        except Exception as e:
            self.logger.error(f"Error during product creation: {e}")
       
    def update_product_async(self):
        """Update the product information asynchronously."""
        # run the extract method in a separate thread
        self.async_extractor = threading.Thread(target=self.extract_and_save, daemon=True)
        self.async_extractor.start()
        # detach the thread


# Example usage
if __name__ == "__main__":
    ean = "4014400927139"
    extractor = OFFExtractor(ean)
    product_info = extractor.extract()
    print(product_info)
