import requests
from bs4 import BeautifulSoup

class OFFExtractor:
    def __init__(self, ean):
        self.ean = ean
        self.api_url = f"https://world.openfoodfacts.org/api/v0/product/{ean}.json"
        self.web_url = f"https://world.openfoodfacts.org/product/{ean}"

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

# Example usage
if __name__ == "__main__":
    ean = "4014400927139"
    extractor = OFFExtractor(ean)
    product_info = extractor.extract()
    print(product_info)
