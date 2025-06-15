import os
import json
import datetime
from firebaseConfig import db
from firebase_admin import firestore

def get_latest_summary_file(brand):
    data_dir = "data"
    base_name = f"data_{brand}_"
    today = datetime.date.today()

    # Try today, then go back one day at a time
    for delta in range(10):  # Check up to 10 days back
        day = today - datetime.timedelta(days=delta)
        date_str = day.strftime("%Y-%m-%d")

        # Check without suffix first
        file_base = f"{base_name}{date_str}_summary.json"
        if os.path.exists(os.path.join(data_dir, file_base)):
            return os.path.join(data_dir, file_base)

        # Now try with numbered suffixes
        suffix = 1
        while True:
            file_name = f"{base_name}{date_str}_summary{suffix}.json"
            file_path = os.path.join(data_dir, file_name)
            if os.path.exists(file_path):
                suffix += 1
                latest_file = file_path
            else:
                break

        if 'latest_file' in locals():
            return latest_file

    return None
def get_latest_data_file(brand):
    data_dir = "data"
    brand_prefix = f"data_{brand}_"
    valid_files = [
        f for f in os.listdir(data_dir)
        if f.startswith(brand_prefix) and f.endswith(".json") and "_summary" not in f
    ]

    if not valid_files:
        return None

    # Sort files by last modified time, descending
    valid_files.sort(
        key=lambda f: os.path.getmtime(os.path.join(data_dir, f)),
        reverse=True
    )

    return os.path.join(data_dir, valid_files[0])

# def get_latest_data_file(brand):
#     # data_dir = "data"
#     # files = sorted([f for f in os.listdir(data_dir) if f.startswith(f"data_{brand}_") and f.endswith(".json") and "_summary" not in f], reverse=True)
#     # return os.path.join(data_dir, files[0]) if files else None
#     data_dir = "data"
#     base_name = f"data_{brand}_"
#     today = datetime.date.today()

#     # Try today, then go back one day at a time
#     for delta in range(10):  # Check up to 10 days back
#         day = today - datetime.timedelta(days=delta)
#         date_str = day.strftime("%Y-%m-%d")

#         # Check without suffix first
#         file_base = f"{base_name}{date_str}"
#         if os.path.exists(os.path.join(data_dir, file_base)):
#             return os.path.join(data_dir, file_base)

#         # Now try with numbered suffixes
#         suffix = 1
#         while True:
#             file_name = f"{base_name}{date_str}{suffix}.json"
#             file_path = os.path.join(data_dir, file_name)
#             if os.path.exists(file_path):
#                 suffix += 1
#                 latest_file = file_path
#             else:
#                 break

#         if 'latest_file' in locals():
#             return latest_file

#     return None

def upload_products_to_firebase(brandName):
    summary_file = get_latest_summary_file(brandName)
    data_file = get_latest_data_file(brandName)
    print("data_file:", data_file)
    print("summary_file:", summary_file)

    if not summary_file or not data_file:
        print("[Error] Summary or data file not found.")
        return

    with open(summary_file, 'r', encoding='utf-8') as f:
        summary = json.load(f)

    with open(data_file, 'r', encoding='utf-8') as f:
        products = json.load(f)
        if isinstance(products, dict):
            products = [products]

    product_map = {p['id']: p for p in products}
    firebase_timestamp = firestore.SERVER_TIMESTAMP

    new_ids = summary.get("New Products", {}).get("ids", [])
    inc_ids = summary.get("Price Increased", {}).get("ids", [])
    dec_ids = summary.get("Price Decreased", {}).get("ids", [])
    del_ids = summary.get("Deleted Products", {}).get("ids", [])

    print('new_ids:', new_ids)
    print('inc_ids:', inc_ids)
    print('dec_ids:', dec_ids)
    print('del_ids:', del_ids)

    for pid in new_ids:
        product = product_map.get(pid)
        
        # if product:
        #     product['id'] = str(pid)
        #     product['dateCreated'] = firebase_timestamp
        #     product['dateLastUpdate'] = firebase_timestamp
        #     product.pop('valid', None) 
        #     db.collection("products").document(str(pid)).set(product)
        #     print(f"[New] Added product {pid}")

        if product and product.get('valid', 1) != 0:  # Skip if valid == 0
                    product['id'] = str(pid)
                    product['dateCreated'] = firebase_timestamp
                    product['dateLastUpdate'] = firebase_timestamp
                    product.pop('valid', None)
                    db.collection("products").document(str(pid)).set(product)
                    print(f"[New] Added product {pid}")
        else:
            print(f"[Skip] Product {pid} is not valid and was skipped")

    for pid in inc_ids + dec_ids:
        product = product_map.get(pid)
        if product:
            db.collection("products").document(str(pid)).update({
                "newPrice": product.get("newPrice"),
                "oldPrice": product.get("oldPrice"),
                "discount": product.get("discount"),
                "dateLastUpdate": firebase_timestamp
            })
            print(f"[Update] Price change for product {pid}")

    for pid in del_ids:
        db.collection("products").document(str(pid)).update({
            "status": 0,
            "dateLastUpdate": firebase_timestamp
        })
        print(f"[Availability] Marked product {pid} as Unavailable.")

    print("Upload to Firebase complete.")

def upload():
    with open('data/data_AhmadRaza_2025-06-14_1.json', 'r', encoding='utf-8') as f:
        products = json.load(f)

    for i, product in enumerate(products):
        doc_id = f"{product.get('id', str(i))}"
        db.collection("products").document(doc_id).set(product)
