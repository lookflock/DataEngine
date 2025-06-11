from scrapper import *
import sys

if __name__ == "__main__":
    brandName = sys.argv[1]

# Step 1: Scrap all the products for the given brand
productsFile = scrapBrand(brandName)
# productsFile = 'data/data_alkaram_2025-03-11.json'
if productsFile:
    print(f"Products saved to: {productsFile}")
else:
    print("No products were scraped or an error occurred.")

# Step 2: Remove duplicate products
removeDuplicates(productsFile)

# Step 3: Compare current and previous files to find new products
compareWithPrevious(productsFile)

# Step 4: Sort products into different categories
categoriseProducts(brandName, productsFile)