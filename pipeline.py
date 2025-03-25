from scrapper import *
import sys

if __name__ == "__main__":
    brandName = sys.argv[1]

    # Step 1: Scrap all the products for the given brand
    productsFile = scrapBrand(brandName)
    # productsFile = 'data/data_alkaram_2025-03-11.json'
    print('Product File Name: ' + productsFile)

    # Step 2: Remove duplicate products
    removeDuplicates(productsFile)

    # Step 3: Sort products into different categories
    categoriseProducts(brandName, productsFile)