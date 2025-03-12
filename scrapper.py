import requests
import config
import datetime
import json
from bs4 import BeautifulSoup
import datetime
import functions

import scrappers_pk.pk_AlKaram as alkaram

testEnvironment = True

def scrapProducts(brandID, soup, category, subCategory, subSubCategory, pageURL):
    # wrapper function to call brand specific scrapper
    products = []
    if (brandID == 'alkaram'):
        products = alkaram.getProducts(soup, category, subCategory, subSubCategory, pageURL)                
    
    else:
        print('No scrapper available for the given brand: ' + brandID)

    # print('Product count: ' + str(len(products)) + ' products \n\n')    
    return products

def scrapBrand(brandID):
    print('Brand Name: ' + brandID)
    renamedFile = functions.renameDataFile(brandID) # rename the previously scrapped data file if it exists

    products = []
    navDetails =functions.getNavigationDetails(brandID)
    
    try:
        navFile = config.navigationFolder + '/' + navDetails['navigationFile']
        print(navFile)
    except:
        navFile = ''
    
    # countProducts = 0
    if navFile == '':
        print('Navigation file does not exist for: ' + brandID)
        return products

    with open(navFile, 'r') as f:
        navigation = json.load(f)

        for cat in navigation['categories']:
            #print(brandID + ' -> Category: ' + cat['name'])

            for subCat in cat['subCategories']:
                #print(brandID + ' -> Category: ' + cat['name'] + ' -> SubCategory: ' + subCat['name'])

                for subSubCat in subCat['subSubCategories']:
                    print(brandID + ' -> Category: ' + cat['name'] + ' -> SubCategory: ' + subCat['name'] + ' -> SubSubCategory: ' + subSubCat['name'])
                    url = subSubCat['url']
                    category = cat['name']
                    subCategory = subCat['name']
                    subSubCategory = subSubCat['name']
                    previousProducts = []
                    
                    maxNumberOfPages = config.maxNumberOfPages
                    i = 1

                    if testEnvironment:
                        i = 1
                        maxNumberOfPages = i + 1;

                    while (i <= maxNumberOfPages):
                        page = i
                        pageUrl = url + navDetails['pagingVariable'] + str(i)
                        print(pageUrl)
                        # print(countProducts)
                        # if countProducts >= 24:             
                        #         print("Exiting 25 products Scrapped")
                        #         break
                        html = functions.getRequest(pageUrl, 'text')
                        soup = BeautifulSoup(html, "html.parser")
                        tempProducts = scrapProducts(brandID, soup, category, subCategory, subSubCategory, pageUrl)
                        # countProducts += len(tempProducts)
                        if tempProducts != previousProducts:  #compares the currenct scrapped with the previous scrapped products if they are same we break loop
                            previousProducts = tempProducts
                        else:
                            break

                        if(len(tempProducts) == 0):
                            break
                        elif(len(tempProducts) > 0):
                            products = products + tempProducts
                            functions.saveDataToJsonFile(products, 'data_' + brandID)
                            
                        else:
                            break
                        i+=1


scrapBrand('alkaram')