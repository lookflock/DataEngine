from scrapper import *


brandName = 'GulAhmed'

# Step 1: Scrap all the products for the given brand
productsFile = scrapBrand(brandName)
# productsFile = 'data/data_alkaram_2025-03-11.json'
if productsFile:
    print(f"Products saved to: {productsFile}")
else:
    print("No products were scraped or an error occurred.")

# Step 2: Remove duplicate products
removeDuplicates(productsFile)

# Step 3: Sort products into different categories
categoriseProducts(brandName, productsFile)