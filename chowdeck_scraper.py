import requests
import pandas as pd

# Always be polite with headers
headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

# Example: a few vendors (replace with your full vendor dict with names)
vendors = {
    "https://api.chowdeck.com/customer/vendor/117067/menu": "KFC",
    "https://api.chowdeck.com/customer/vendor/120564/menu": "Just Taste",
    "https://api.chowdeck.com/customer/vendor/116436/menu": "Bliss on Plate",
    "https://api.chowdeck.com/customer/vendor/118542/menu": "Pizzaman Chickenman",
    "https://api.chowdeck.com/customer/vendor/119220/menu": "Pious Fast Food",
    "https://api.chowdeck.com/customer/vendor/117306/menu": "Papaye",
    "https://api.chowdeck.com/customer/vendor/119326/menu": "Pizza Hut",
    "https://api.chowdeck.com/customer/vendor/117051/menu": "Papa’s Pizza",
    "https://api.chowdeck.com/customer/vendor/124955/menu": "Faridish",
    "https://api.chowdeck.com/customer/vendor/124548/menu": "Dowu’s Kitchen",
    "https://api.chowdeck.com/customer/vendor/124476/menu": "Hotdog Avenue",
    "https://api.chowdeck.com/customer/vendor/124117/menu": "Floka Eatery",
    "https://api.chowdeck.com/customer/vendor/123014/menu": "Cups and Cones",
    "https://api.chowdeck.com/customer/vendor/119442/menu": "Pinkberry",
    "https://api.chowdeck.com/customer/vendor/120768/menu": "Jollof Express by Yes Chef",
    "https://api.chowdeck.com/customer/vendor/120534/menu": "Yendidi",
    "https://api.chowdeck.com/customer/vendor/120429/menu": "Fasee Pork Joint",
    "https://api.chowdeck.com/customer/vendor/120060/menu": "Delibeli Restaurant and Bar",
    "https://api.chowdeck.com/customer/vendor/120051/menu": "10:10 Joint",
    "https://api.chowdeck.com/customer/vendor/119880/menu": "Kiss Burger and Wraps Bar",
    "https://api.chowdeck.com/customer/vendor/119441/menu": "Cherry’s Mini Pizza",
    "https://api.chowdeck.com/customer/vendor/119074/menu": "JarToGo Smart-food Hub",
    "https://api.chowdeck.com/customer/vendor/121757/menu": "Cheezzy Pizza",
    "https://api.chowdeck.com/customer/vendor/117105/menu": "HM Eatery",
    "https://api.chowdeck.com/customer/vendor/117102/menu": "Munchy’s Ring Road",
    "https://api.chowdeck.com/customer/vendor/117094/menu": "Asanka Restaurant",
    "https://api.chowdeck.com/customer/vendor/117092/menu": "The Gold Coast Restaurant",
    "https://api.chowdeck.com/customer/vendor/117082/menu": "Wonder Wings",
    "https://api.chowdeck.com/customer/vendor/117073/menu": "Ninano Restaurant Osu",
    "https://api.chowdeck.com/customer/vendor/117065/menu": "Yah Restaurant",
    "https://api.chowdeck.com/customer/vendor/117063/menu": "Pinocchio Osu",
    "https://api.chowdeck.com/customer/vendor/116945/menu": "Sikada",
    "https://api.chowdeck.com/customer/vendor/119269/menu": "PS Banku and Tilapia",
    "https://api.chowdeck.com/customer/vendor/118197/menu": "The Rumson Restaurant",
    "https://api.chowdeck.com/customer/vendor/120670/menu": "Yehowada",
    "https://api.chowdeck.com/customer/vendor/120421/menu": "Hi-tech Fast Foods",
    "https://api.chowdeck.com/customer/vendor/119305/menu": "Express Noodles",
    "https://api.chowdeck.com/customer/vendor/119384/menu": "Burkina Waakye",
    "https://api.chowdeck.com/customer/vendor/116641/menu": "The Burger Booth",
    "https://api.chowdeck.com/customer/vendor/119382/menu": "Burkina Banku and Kenkey",
    "https://api.chowdeck.com/customer/vendor/119772/menu": "Pinkie’s Bistro",
    "https://api.chowdeck.com/customer/vendor/121417/menu": "Yes Chef Osu",
    "https://api.chowdeck.com/customer/vendor/120221/menu": "Junkies Burger",
    "https://api.chowdeck.com/customer/vendor/119272/menu": "Awo Aduane",
    "https://api.chowdeck.com/customer/vendor/119380/menu": "Burkina Tasty Fries",
    "https://api.chowdeck.com/customer/vendor/120106/menu": "Licks Eatery",
    "https://api.chowdeck.com/customer/vendor/116540/menu": "Waakye Phobia",
    "https://api.chowdeck.com/customer/vendor/126144/menu": "Ikie Catfish Joint",
    "https://api.chowdeck.com/customer/vendor/126144/menu": "Burkina Red Red",
    "https://api.chowdeck.com/customer/vendor/117072/menu": "Peter Pan Osu",
    "https://api.chowdeck.com/customer/vendor/120230/menu": "Golden Shawarma Palace",
    "https://api.chowdeck.com/customer/vendor/120056/menu": "Deli Locals",
    "https://api.chowdeck.com/customer/vendor/116853/menu": "Wok Boyz Osu",
    "https://api.chowdeck.com/customer/vendor/116452/menu": "Chickie’s Restaurant",
    "https://api.chowdeck.com/customer/vendor/117080/menu": "Champs and Pataase Restaurant",
    "https://api.chowdeck.com/customer/vendor/122964/menu": "Garden District Kitchen"
}


all_rows = []

for url, restaurant_name in vendors.items():
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        data_json = response.json()
    except Exception as e:
        print(f"⚠️ Error fetching {restaurant_name}: {e}")
        continue

    for dish in data_json.get("data", []):
        dish_copy = dish.copy()
        dish_copy["restaurant"] = restaurant_name
        dish_copy["source_url"] = url
        all_rows.append(dish_copy)

df = pd.DataFrame(all_rows)
df.to_csv("chowdeck_full_dump.csv", index=False)
print(f"✅ Saved {len(df)} rows with ALL fields into chowdeck_full_dump.csv")