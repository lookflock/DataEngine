from convertToCloudflareCDN import convertToCloudflareCDN
from scrapper import *
import sys
from firebase import upload_products_to_firebase
from functions import verifyProducts
if __name__ == "__main__":
    brandName = sys.argv[1]

# Step 1: Scrap all the products for the given brand
productsFile = scrapBrand(brandName)
# productsFile = 'data/data_AhmadRaza_2025-06-14.json'
if productsFile:
    print(f"Products saved to: {productsFile}")
else:
    print("No products were scraped or an error occurred.")

# Step 2: Remove duplicate products
removeDuplicates(productsFile)

# Step 3: Compare current and previous files to find new products
compareWithPrevious(brandName,productsFile)

# Step 4: Sort products into different categories
categoriseProducts(brandName)
# categoriseAllProducts(brandName,productsFile)

# Step 5: Scrap the details of new products
# scrapDetails(brandName)

# Step 6: verification of Product for name, price and imageUrl,
verifyProducts(brandName)

# Step 7: convertToCloudflareCDN
convertToCloudflareCDN(productsFile,brandName)

# Step 8: Upload to Firebase
uploadOrNot = input("Do you want to upload the scraped products to Firebase? (yes/no): ").strip().lower()

if uploadOrNot in ['yes', 'y']:
    upload_products_to_firebase(brandName)
    print("Products uploaded to Firebase.")
else:
    print("Upload skipped.")
