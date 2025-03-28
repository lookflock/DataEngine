import requests
import config
import datetime
import json
from bs4 import BeautifulSoup
import datetime
import functions


import scrappers_pk.pk_AhmadRaza as AhmadRaza
import scrappers_pk.pk_AlKaram as Alkaram
import scrappers_pk.pk_Almirah as Almirah
import scrappers_pk.pk_AnamAkhlaq as AnamAkhlaq
import scrappers_pk.pk_BeechTree as BeechTree
import scrappers_pk.pk_BonanzaSatrangi as BonanzaSatrangi
import scrappers_pk.pk_Cambridge as Cambridge
# import scrappers_pk.pk_Chinyere as Chinyere
# import scrappers_pk.pk_CrossStitch as CrossStitch
import scrappers_pk.pk_Dhanak as Dhanak
import scrappers_pk.pk_Diners as Diners
# import scrappers_pk.pk_GulAhmed as GulAhmed
# import scrappers_pk.pk_Generation as Generation
import scrappers_pk.pk_JunaidJamshed as JunaidJamshed
import scrappers_pk.pk_EdenRobe as EdenRobe
import scrappers_pk.pk_Lakhanay as Lakhanay

testEnvironment = False

def sortProducts(file):
    products = functions.getDataFromJsonFilel(file)
     
    category_mappings = {
        'kurtaSet': ['1PC', '1 PC', 'top', '1 piece', '1 Piece', '1 PIECE', "1-Pc", "1-pc", 
                     '3PC', '3 PC', "3-Pc", "3-pc", '3 Piece', 'three piece', '3 piece', 
                     'THREE PIECE', 'THREEPIECE', '3 PIECE', '3Pcs', '2- Piece', '2 PIECE', 
                     '2-Piece', '2-piece', '2 piece', '2 Piece', '2Piece', '2PC', '2 piece', 
                     'two piece', 'TWO PIECE', '2 PC', '2  PC', '2-Pc', '2-pcs'],
        'coord': ['Co-Ord', 'Coord', 'co ord', 'Co-ord', 'Cor-ord'],
        'kurta': ['kurta', 'kameez'],
        'maxi': ['maxi'],
        'pajama': ['pajama', 'Pajama'],
        'tights': ['tights'],
        'lehenga': ['lehenga'],
        'shawl': ['shawl', 'Stole'],
        'anarkali':['anarkali'],
        'dupatta': ['dupatta', 'dup'],
        'angrakha': ['angrakha', 'angarkhas', 'angarkha'],
        'kaftan': ['kaftan'],
        'frock': ['frock'],
        'gown': ['gown'],
        'sharara': ['sharara'],
        'skirt': ['skirt'],
        'pant': ['jeans', 'pant', 'pants', 'denim', "Chino"],
        'sweater': ['sweater'],
        'dropShoulder': ['drop shoulder'],
        'cullote': ['cullote', 'culottes'],
        'scarf':['scarf'],
        'cape':['cape'],
        'tanktop':['tanktop'],
        'shirt':['shirt','kimono',"Crew"],
        'tunic':['tunic'],
        'dress':['dress','gypsy'],
        'waistcoat':['waistcoat'],
        'koti':['koti','bolero'],
        'tights':['tights','leg', 'tight'],
        'trouser':['trouser'],
        'shalwar':['shalwar','palazzos'],
        'peplum':['peplum'],
        'kaftan':['kaftan'],
        'gown':['gown'],
        'cardigan':['cardigan'],
        'sweater':['sweater'],
        'jacket':['jacket'],
        'kurti':['kurti'],
        'saree':['saree','Sarees'],
        'Sleepwear':['Sleepwear'],
        'polo':['Polos', 'Polo'],
        'shorts':['Shorts', 'Short'],
        'sherwani':['Sherwani', 'sherwani'],
        'blazer':['Blazer'],
        'athleisure':['Athleisure'],
        'Suits':['Suits'],
        'coat':['Prince Coat', 'Prince Suit'],
        't-shirt':['T-Shirt', 'Tee']
    }

    for p in products:
        if p['subSubCategory'] == 'None':
            name = p['name'].lower()
            # Check for matches in category mappings
            for category, keywords in category_mappings.items():
                for keyword in keywords:
                    if keyword.lower() in name:
                        p['subSubCategory'] = category
                        break
                else:
                    continue
                break

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
        if (brandID == 'Alkaram'):
            products = Alkaram.getProducts(soup, category, subCategory, subSubCategory, pageURL)
        elif (brandID == 'AhmadRaza'):
            products = AhmadRaza.getProducts(soup, category, subCategory, subSubCategory, pageURL)
        elif (brandID == 'Almirah'):
            products = Almirah.getProducts(soup, category, subCategory, subSubCategory, pageURL)
        elif (brandID == 'AnamAkhlaq'):
            products = AnamAkhlaq.getProducts(soup, category, subCategory, subSubCategory, pageURL)
        elif (brandID == 'BeechTree'):
            products = BeechTree.getProducts(soup, category, subCategory, subSubCategory, pageURL)
        elif (brandID == 'BonanzaSatrangi'):
            products = BonanzaSatrangi.getProducts(soup, category, subCategory, subSubCategory, pageURL)
        elif (brandID == 'Cambridge'):
            products = Cambridge.getProducts(soup, category, subCategory, subSubCategory, pageURL)
        # elif (brandID == 'CrossStitch'):
        #     products = CrossStitch.getProducts(soup, category, subCategory, subSubCategory, pageURL)
        # elif (brandID == 'Chinyere'):
        #     products = Chinyere.getProducts(soup, category, subCategory, subSubCategory, pageURL)
        elif (brandID == 'Dhanak'):
            products = Dhanak.getProducts(soup, category, subCategory, subSubCategory, pageURL)    
        elif (brandID == 'Diners'):
            products = Diners.getProducts(soup, category, subCategory, subSubCategory, pageURL)
        # elif (brandID == 'GulAhmed'):
        #     products = GulAhmed.getProducts(soup, category, subCategory, subSubCategory, pageURL)
        # elif (brandID == 'Generation'):
        #     products = Generation.getProducts(soup, category, subCategory, subSubCategory, pageURL)
        elif (brandID == 'JunaidJamshed'):
            products = JunaidJamshed.getProducts(soup, category, subCategory, subSubCategory, pageURL)
        elif (brandID == 'EdenRobe'):
            products = EdenRobe.getProducts(soup, category, subCategory, subSubCategory, pageURL)
        elif (brandID == 'Lakhanay'):
            products = Lakhanay.getProducts(soup, category, subCategory, subSubCategory, pageURL)
    
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


