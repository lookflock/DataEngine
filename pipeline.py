from scrapper import *


brandName = 'alkaram'

# Step 1: Scrap all the products for the given brand
# productsFile = scrapBrand(brandName)
productsFile = 'data/data_alkaram_2025-03-11.json'
print('Product File Name: ' + productsFile)

# Step 2: Remove duplicate products
removeDuplicates(productsFile)

# Step 3: Sort products into different categories
categoriseProducts(brandName, productsFile)