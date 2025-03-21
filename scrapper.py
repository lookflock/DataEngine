import requests
import config
import datetime
import json
from bs4 import BeautifulSoup
import datetime
import functions

import scrappers_pk.pk_AlKaram as Alkaram
import scrappers_pk.pk_Almirah as Almirah
import scrappers_pk.pk_BeechTree as BeechTree
import scrappers_pk.pk_BonanzaSatrangi as BonanzaSatrangi

testEnvironment = False

def sortProducts(file):

    products = functions.getDataFromJsonFilel(file)
    
    lst_1Piece = ['1PC', '1 PC', 'Top','1 piece','1 Piece', '1 PIECE', "1-Pc", "1-pc"]
    lst_2Piece = ['Co-Ord', 'Coord', 'Co Ord', "2-Pc","2-pc",'Co-ord', 'Cor-ord', '2- Piece', '2 PIECE', '2-Piece', '2-piece', '2 piece', '2 Piece', '2Piece', '2PC', '2 piece', 'two piece','TWO PIECE', '2 PC','2  PC']
    lst_3Piece = ['3PC', '3 PC', "3-Pc","3-pc",'3 Piece','three piece','3 piece','THREE PIECE' ,'THREEPIECE', '3 PIECE', '3Pcs']
    lst_bottoms = ['trouser', 'tights', 'lehenga','shalwar', 'jeans','pant', 'peplum','pants', 'cullote','culottes', 'palazzos', 'denim', 'skirt', 'leg', 'sharara']
    lst_dresses = ['angarkhas', 'angarkha', 'maxi','angrakha', 'anarkali', 'kaftan', 'frock', 'gypsy', 'dress', 'gown' ]
    lst_tops = ['bolero', 'koti', 'kurta', 'kurti', 'shirt', 'tanktop','kimono','cardigan', 'jacket', 'waistcoat', 'kameez', 'tunic', 'drop shoulder', 'sweater']
    lst_stoles = ['dupatta', 'scarf', 'shawl', 'cape', 'dup']

    for p in products:
        if p['subSubCategory'] == 'None':
            name = p['name'].lower()
            if name in lst_1Piece:
                p['subSubCategory'] = '1-Pc'
                break
            if name in lst_2Piece:
                p['subSubCategory'] = '2-Pc'
                break
            if name in lst_3Piece:
                p['subSubCategory'] = '3-Pc'
                break    

            for cat in lst_1Piece + lst_2Piece + lst_3Piece + lst_dresses + lst_stoles:
                if cat in p['name'] and cat in lst_2Piece:
                    p['subSubCategory'] = '2-Pc'
                    break
                elif cat in p['name'] and cat in lst_3Piece:
                    p['subSubCategory'] = '3-Pc'
                    break
                elif cat in p['name'] and cat in lst_1Piece:
                    p['subSubCategory'] = 'Tops'
                    break
                elif cat in p['name'].lower() and cat in lst_dresses:
                    p['subSubCategory'] = 'Dresses'
                    break
                elif cat in p['name'].lower() and cat in lst_stoles:
                    p['subSubCategory'] = 'Stoles'
                    break

            
            if 'Saree' in p['name']:
                p['subSubCategory'] = 'Sarees'
        

            elif 'Sleepwear' in p['name']:
                p['subSubCategory'] = 'Sleepwear'
                
            elif 'suit' in p['name']:
                p['subSubCategory'] = 'Suits'

            else:
                matchCount = 0

                for cat in lst_bottoms + lst_dresses + lst_tops + lst_stoles:
                    if cat in name:
                        matchCount += 1

                if matchCount == 0 :
                    if name in lst_2Piece:
                        p['subSubCategory'] = '2-Pc'
                    elif name in lst_3Piece:
                        p['subSubCategory'] = '3-Pc'    
                    #elif 'suit' in name:
                    #    p['subSubCategory'] = 'Suit'

                elif matchCount == 1:
                    for cat in lst_bottoms + lst_dresses + lst_tops + lst_stoles:
                        if cat in name and cat in lst_bottoms:
                            p['subSubCategory'] = 'Bottoms'
                            
                        elif cat in name and cat in lst_dresses:
                            p['subSubCategory'] = 'Dresses'
                            
                        elif cat in name and cat in lst_tops:
                            p['subSubCategory'] = 'Tops'
                           

                    if name in lst_stoles:
                        p['subSubCategory'] = 'Stoles'
                        

                elif matchCount == 2 or name in lst_2Piece:
                    p['subSubCategory'] = '2-Pc'
                    

                elif matchCount == 3 or name in lst_3Piece:
                    p['subSubCategory'] = '3-Pc'

                   
    return products

def getUnsortedProducts(products, brand):

    i = 0

    unsorttedProducts = ''
    for p in products:
        if p['subSubCategory'] == 'None':
            i += 1
            unsorttedProducts = unsorttedProducts + '\n' + p['name']

    if i > 0:

        unsorttedProducts = unsorttedProducts + '\n\n Total: ' + str(i)
        f = open('data/unsorted_' + brand + '.txt', 'w')
        f.write(unsorttedProducts)
        f.close()
    
    return [i, 'data/unsorted_' + brand + '.txt']


def categoriseProducts(brandName, fileName):
    # Set up logging
    #logfile = 'product_' + brandName + str(date.today()) + '.log'
    #logging.basicConfig(filename=logfile, level=logging.INFO)

    # Calls the sortProducts() function to sort unsorted products and generates a report
    # file_name = 'data/' + 'data_' + brandName + '_'+ today.strftime("%Y-%m-%d") + '.json'
    products = sortProducts(fileName)
    unsortedData = getUnsortedProducts(products, brandName)
    dataFile = functions.saveDataToJsonFile(products, 'data_' + brandName)

    # Log information
    print('Sorted Product Data: ', dataFile)
    print('Total Products: ', str(len(products)))
    print('Unsorted Products: ', str(unsortedData))

def removeDuplicates(fileName):
    # fileName = 'data/' + 'data_' + brandName + '_' + today.strftime("%Y-%m-%d") + '.json'
    try:
        # Read existing data
        uniqueProductCount=j=0
        with open(fileName, 'r') as file:
            data = json.load(file)

        unique_products = []
        seen_product_ids = set()

        for product in data:
            j = j+1
            product_id = product.get("productID")
            if product_id not in seen_product_ids:
                uniqueProductCount = uniqueProductCount+1
                seen_product_ids.add(product_id)
                unique_products.append(product)
            else:
                print(product_id)

        # Write the unique data back to the file
        with open(fileName, 'w') as file:
            json.dump(unique_products, file, indent=4)
        
        print('Total Scrapped Products: ', str(j))
        print('Unique Products: ', str(uniqueProductCount))

    #     logger.info('Total Scrapped Products: %s', str(j))

    #     logger.info('Unique Products: %s', str(i))
        
    # except FileNotFoundError:
    #     logger.error(f"File not found: {fileName}")
    # except json.JSONDecodeError:
    #     logger.error(f"Error decoding JSON from the file: {fileName}")
    # except Exception as e:
    #     logger.error(f"An error occurred: {str(e)}")
    except:
        None

def scrapProducts(brandID, soup, category, subCategory, subSubCategory, pageURL):
    # wrapper function to call brand specific scrapper
    products = []
    try:
        products = BonanzaSatrangi.getProducts(soup, category, subCategory, subSubCategory, pageURL)
    
    except:
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
        productsFile = ""
        for cat in navigation['categories']:
            #print(brandID + ' -> Category: ' + cat['name'])

            for subCat in cat['subCategories']:
                #print(brandID + ' -> Category: ' + cat['name'] + ' -> SubCategory: ' + subCat['name'])

                for subSubCat in subCat['subSubCategories']:
                    print('\n' + brandID + ' -> Category: ' + cat['name'] + ' -> SubCategory: ' + subCat['name'] + ' -> SubSubCategory: ' + subSubCat['name'])
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

                        html = functions.getRequest(pageUrl, 'text')
                        soup = BeautifulSoup(html, "html.parser")

                        with open("output.html", "w", encoding="utf-8") as f:
                            f.write(soup.prettify())

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
                            productsFile = functions.saveDataToJsonFile(products, 'data_' + brandID)
                            
                        else:
                            break
                        i+=1
    return productsFile


