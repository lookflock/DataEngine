from scrapper import *
from firebase_admin import firestore, initialize_app,credentials
import firebase_admin
from functions import UploadProducts
from firebaseConfig import db
from convertToCloudflareCDN import convertToCloudflareCDN 

def log_info(msg):
    print(msg)

def main():
    try:
        # Step 0: Get all brand IDs from Firebase where status == 1
        brands_ref = db.collection('brands').where(filter=firestore.FieldFilter('status', '==', 1))
        active_brands = brands_ref.stream()

        for brand_doc in active_brands:
            brandId = brand_doc.id
            log_info(f"\n--- Starting process for brand: {brandId} ---")

            # Step 1: Scrap products
            productsFile = scrapBrand(brandId)

            if productsFile:
                log_info(f"Products saved to: {productsFile}")
            else:
                log_info("No products were scraped or an error occurred.")
                continue  # Skip to next brand if nothing was scraped

            # Step 2: Remove duplicate products
            removeDuplicates(brandId)
            
            #  Rewrite image URLs with Cloudflare CDN
            convertToCloudflareCDN(productsFile)

            # Step 3: Sort and categorize products
            categoriseProducts(brandId, productsFile)
            
            UploadProducts(brandId)

            log_info(f"--- Finished processing brand: {brandId} ---\n")

    except Exception as e:
        log_info(f"An error occurred during execution: {str(e)}")

if __name__ == "__main__":
    main()
