import json

def log_info(msg):
    print(msg)

def convertToCloudflareCDN(productsFile):
    try:
        with open(productsFile, 'r', encoding='utf-8') as f:
            products = json.load(f)

        for product in products:
            originalUrl = product.get("imageUrl")
            if originalUrl:
                product["originalImageUrl"] = originalUrl
                product["imageUrl"] = f"https://cache-image.lookflock.workers.dev/?url={originalUrl}"

        with open(productsFile, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)

        log_info(f"Rewritten image URLs in: {productsFile}")
    except Exception as e:
        log_info(f"Error in rewriteImageUrls: {e}")