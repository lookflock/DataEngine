import json
import os

def log_info(msg):
    print(msg)

def convertToCloudflareCDN(productsFile, brandName):
    try:
        CDN_PREFIX = "https://cache-image.lookflock.workers.dev/?url="

        # Read products
        with open(f'{productsFile}', 'r', encoding='utf-8') as f:
            products = json.load(f)

        # Prepare to collect only new image URLs
        originalImagesUrl = []

        # Load existing image records if the file exists
        original_urls_path = f'OriginalImagesURL/{brandName}.json'
        existing_ids = set()
        if os.path.exists(original_urls_path):
            with open(original_urls_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                existing_ids = {item['id'] for item in existing_data}
        else:
            existing_data = []

        for product in products:
            pid = product.get('id')
            originalUrl = product.get("imageUrl")
            secondaryImgs = product.get("secondaryImages", [])

            # Store original only if it's not in the existing file
            if pid not in existing_ids:
                originalImagesUrl.append({
                    'id': pid,
                    'imageURL': originalUrl,
                    'secondaryImages': secondaryImgs
                })

            # Convert main image URL (only if not already CDN-wrapped)
            if originalUrl and not originalUrl.startswith(CDN_PREFIX):
                product["imageUrl"] = f"{CDN_PREFIX}{originalUrl}"

            # Convert secondary images
            if isinstance(secondaryImgs, list):
                updated_secondary = []
                for img_url in secondaryImgs:
                    if img_url and not img_url.startswith(CDN_PREFIX):
                        img_url = f"{CDN_PREFIX}{img_url}"
                    updated_secondary.append(img_url)
                product['secondaryImages'] = updated_secondary

        # Save updated product list
        with open(f'{productsFile}', 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)

        # Merge and save only new image URLs
        if originalImagesUrl:
            os.makedirs("OriginalImagesURL", exist_ok=True)
            updated_data = existing_data + originalImagesUrl
            with open(original_urls_path, 'w', encoding='utf-8') as f:
                json.dump(updated_data, f, ensure_ascii=False, indent=2)

        log_info(f"Updated original image URLs in: {original_urls_path}")

    except Exception as e:
        log_info(f"Error in convertToCloudflareCDN: {e}")
