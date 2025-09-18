import requests
from bs4 import BeautifulSoup
import pandas as pd

restaurants = {
    # Format: url : (restaurant name, parser type)
    "https://pizarea.com/restaurant/dnr.pizarea.com/restaurant-menu/dnr-east-legon-accra": ("DNR", "pizarea"),
    "https://www.ghanamenu.com/business.php?term=&id=137": ("Bistro 22", "ghanamenu"),
    "https://chrismaison.app/menu?category=ALL": ("Chris Maison", "generic"),
    "https://qrmenu.com/menus/green-pepper-restaurant/hot-appetizers/": ("Green Pepper", "qrmenu"),
    "https://qrmenu.com/menus/green-pepper-restaurant/soups/": ("Green Pepper", "qrmenu"),
    "https://sites.google.com/view/bawse-shawarma-and-salads/menu": ("Bawse Shawarma", "generic"),
    "https://pizarea.com/restaurant/frankies.pizarea.com/restaurant-menu/frankie-s": ("Frankies", "pizarea"),
    "https://basilissagh.com/#menu": ("Basilissa", "generic"),
    "https://wirecake.com/buka-restaurant-menu-prices/": ("Buka", "generic"),
    "https://www.ghanamenu.com/restaurant/the-honeysuckle-pub-restaurant/186": ("Honeysuckle", "ghanamenu"),
    "https://zengardengh.com/menu/": ("Zen Garden", "generic"),
}

rows = []

# ------------------------------
# Define parser functions BELOW
# ------------------------------

def parse_pizarea(url, restaurant_name):
    """Scraper for Pizarea menu structure"""
    data = []
    res = requests.get(url, timeout=15)
    soup = BeautifulSoup(res.text, "lxml")

    items = soup.find_all("div", class_="menu-item")
    for item in items:
        name = item.find("h4").get_text(strip=True) if item.find("h4") else "N/A"
        price = item.find("span", class_="menu_price").get_text(strip=True) if item.find("span", class_="menu_price") else "N/A"
        desc = item.find("p").get_text(strip=True) if item.find("p") else ""
        data.append({
            "restaurant": restaurant_name,
            "food": name,
            "price": price,
            "taste": "N/A",
            "location": "Accra",
            "portion_size": "N/A",
            "dish_category": "Uncategorized",
            "description": desc,
            "source_url": url
        })
    return data


def parse_ghanamenu(url, restaurant_name):
    """Scraper for GhanaMenu.com listing pages"""
    data = []
    res = requests.get(url, timeout=15)
    soup = BeautifulSoup(res.text, "lxml")

    items = soup.find_all("div", class_="menu-listing")
    for item in items:
        name = item.find("span", class_="name").get_text(strip=True) if item.find("span", class_="name") else "N/A"
        price = item.find("span", class_="price").get_text(strip=True) if item.find("span", class_="price") else "N/A"
        desc = item.find("span", class_="description").get_text(strip=True) if item.find("span", class_="description") else ""
        data.append({
            "restaurant": restaurant_name,
            "food": name,
            "price": price,
            "taste": "N/A",
            "location": "Accra",
            "portion_size": "N/A",
            "dish_category": "Uncategorized",
            "description": desc,
            "source_url": url
        })
    return data


def parse_qrmenu(url, restaurant_name):
    """Scraper for QRMenu pages"""
    data = []
    res = requests.get(url, timeout=15)
    soup = BeautifulSoup(res.text, "lxml")

    items = soup.find_all("div", class_="qm-menu-item")
    for item in items:
        name = item.find("h3").get_text(strip=True) if item.find("h3") else "N/A"
        price = item.find("div", class_="qm-item-price").get_text(strip=True) if item.find("div", class_="qm-item-price") else "N/A"
        desc = item.find("div", class_="qm-item-description").get_text(strip=True) if item.find("div", class_="qm-item-description") else ""
        data.append({
            "restaurant": restaurant_name,
            "food": name,
            "price": price,
            "taste": "N/A",
            "location": "Accra",
            "portion_size": "N/A",
            "dish_category": "Uncategorized",
            "description": desc,
            "source_url": url
        })
    return data


def parse_generic(url, restaurant_name):
    """Fallback: try to grab all <li>, <h4>, <span class=price> etc."""
    data = []
    res = requests.get(url, timeout=15)
    soup = BeautifulSoup(res.text, "lxml")

    items = soup.find_all(["h4","li"])  # Very loose
    for item in items:
        text = item.get_text(" ", strip=True)
        if "₵" in text or "GHS" in text:
            data.append({
                "restaurant": restaurant_name,
                "food": text,
                "price": text,
                "taste": "N/A",
                "location": "Accra",
                "portion_size": "N/A",
                "dish_category": "Uncategorized",
                "description": "",
                "source_url": url
            })
    return data


# ----------------------
# Dispatcher
# ----------------------
parsers = {
    "pizarea": parse_pizarea,
    "ghanamenu": parse_ghanamenu,
    "qrmenu": parse_qrmenu,
    "generic": parse_generic
}

for url, (name, parser_key) in restaurants.items():
    print(f"Fetching {name} from {url}")
    parser = parsers.get(parser_key, parse_generic)
    try:
        rows.extend(parser(url, name))
    except Exception as e:
        print(f"⚠️ Failed on {name}: {e}")

# Save everything into CSV
df = pd.DataFrame(rows)
df.to_csv("ghana_restaurant_menus.csv", index=False, encoding="utf-8")
print(f"✅ Saved {len(df)} dishes from {len(restaurants)} restaurants into ghana_restaurant_menus.csv")