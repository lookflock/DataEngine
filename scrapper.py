import requests
import config
import datetime
import json
from bs4 import BeautifulSoup
import datetime
import functions
import os
from urllib.parse import urljoin


from lib.logger import log_info, log_error
import scrappers_pk.pk_AhmadRaza as AhmadRaza
import scrappers_pk.pk_AlKaram as Alkaram
import scrappers_pk.pk_Almirah as Almirah
import scrappers_pk.pk_AnamAkhlaq as AnamAkhlaq
import scrappers_pk.pk_BeechTree as BeechTree
import scrappers_pk.pk_BonanzaSatrangi as BonanzaSatrangi
import scrappers_pk.pk_Cambridge as Cambridge
import scrappers_pk.pk_Chinyere as Chinyere
import scrappers_pk.pk_CrossStitch as CrossStitch
import scrappers_pk.pk_Dhanak as Dhanak
import scrappers_pk.pk_Diners as Diners
import scrappers_pk.pk_GulAhmed as GulAhmed
import scrappers_pk.pk_Generation as Generation
import scrappers_pk.pk_JunaidJamshed as JunaidJamshed
import scrappers_pk.pk_EdenRobe as EdenRobe
import scrappers_pk.pk_Lakhanay as Lakhanay
import scrappers_pk.pk_GulAhmed as GulAhmed
import scrappers_pk.pk_Generation as Generation
import scrappers_pk.pk_CrossStitch as CrossStitch
import scrappers_pk.pk_Chinyere as Chinyere
import scrappers_pk.pk_Charcoal as Charcoal
import scrappers_pk.pk_Ego as Ego
import scrappers_pk.pk_LimeLight as LimeLight
import scrappers_pk.pk_Ethnic as Ethnic
import scrappers_pk.pk_FaizaRehman as FaizaRehman
import scrappers_pk.pk_FatimaKhan as FatimaKhan
import scrappers_pk.pk_NausheenWamiq as NausheenWamiq
import scrappers_pk.pk_NomiAnsari as NomiAnsari
import scrappers_pk.pk_Nureh as Nureh
import scrappers_pk.pk_HafsaMalik as HafsaMalik
import scrappers_pk.pk_Hijabi as Hijabi
import scrappers_pk.pk_Outfitters as Outfitters
import scrappers_pk.pk_Rasofficial as Rasofficial
# import scrappers_pk.pk_SMP as SMP

testEnvironment = False


def sortProducts(file):
    products = functions.getDataFromJsonFilel(file)
     
    piece_mappings = {
        '1-Pc': {'1pc', '1 pc', 'top', '1 piece', '1-piece', '1-pc'},
        '2-Pc': {'2pc', '2 pc', '2-piece', '2 piece', 'two piece'},
        '3-Pc': {'3pc', '3 pc', '3-piece', '3 piece', 'three piece'}
    }

    category_mappings = {
        'KurtaSet': ['1PC', '1 PC', 'top', '1 piece', '1 Piece', '1 PIECE', "1-Pc", "1-pc", 
                     '3PC', '3 PC', "3-Pc", "3-pc", '3 Piece', 'three piece', '3 piece', 
                     'THREE PIECE', 'THREEPIECE', '3 PIECE', '3Pcs', '2- Piece', '2 PIECE', 
                     '2-Piece', '2-piece', '2 piece', '2 Piece', '2Piece', '2PC', '2 piece', 
                     'two piece', 'TWO PIECE', '2 PC', '2  PC','2-Pc','4pc'],
        'Coord': ['Co-Ord', 'Coord', 'co ord', 'Co-ord', 'Cor-ord', 'Co Ord'],
        'Kurta': ['kurta', 'kameez'],
        'Maxi': ['maxi'],
        'Tights': ['tights'],
        'Lehenga': ['lehenga'],
        'Shawl': ['shawl'],
        'Anarkali':['anarkali'],
        'Dupatta': ['dupatta', 'dup'],
        'Angrakha': ['angrakha', 'angarkhas', 'angarkha'],
        'Kaftan': ['kaftan'],
        'Frock': ['frock'],
        'Gown': ['gown'],
        'Sharara': ['sharara'],
        'Skirt': ['skirt'],
        'Pant': ['pant', 'pants'],
        'Jeans': ['jeans','denim'],
        'Sweater': ['sweater'],
        'DropShoulder': ['drop shoulder'],
        'Cullote': ['cullote', 'culottes'],
        'Scarf':['scarf'],
        'Cape':['cape'],
        'Tanktop':['tanktop','Tank Top'],
        'Shirt':['shirt','kimono','Tee'],
        'Tunic':['tunic'],
        'Dress':['dress','gypsy'],
        'Waistcoat':['waistcoat'],
        'Koti':['koti','bolero'],
        'Tights':['tights','leg'],
        'Trouser':['trouser','trousers'],
        'Shalwar':['shalwar','palazzos'],
        'Peplum':['peplum'],
        'Kaftan':['kaftan'],
        'Gown':['gown'],
        'Cardigan':['cardigan','Blazer'],
        'Sweater':['sweater'],
        'Jacket':['jacket'],
        'Kurti':['kurti'],
        'Saree':['saree','Sarees'],
        'Sleepwear':['Sleepwear'],
        'Suits':['Suits','Suit'],
        'Polos':['Polos','Polo'],
        'T-Shirts':['t-Shirt', 'Tee'],
        'Shorts':['shorts', 'Short'],
        'Gharara':['gharara'],
        'Sherwani':['Sherwani', 'sherwani'],
        'Athleisure':['Athleisure'],
        'Coat':['Prince Coat', 'Prince Suit'],
    }

    for p in products:
        if p['subSubCategory'] == 'None':
            name = p['name'].lower()
            matched_categories = set()

            for category, keywords in category_mappings.items():
                if any(keyword.lower() in name for keyword in keywords):
                    matched_categories.add(category)

            if matched_categories:
                p['subSubCategory'] = list(matched_categories)[0]  # Assign the first found category
                

                # If the assigned category is 'KurtaSet' and piece is not already set
                if p['subSubCategory'] == 'KurtaSet' and 'piece' not in p:
                    for piece_key, piece_values in piece_mappings.items():
                        if any(piece_value in name for piece_value in piece_values):
                            p['piece'] = piece_key
                            break

    return products

def getUnsortedProducts(products, brand):

    i = 0

    unsorttedProducts = ''
    for p in products:
        if p['subSubCategory'] == 'None':
            i += 1
            unsorttedProducts = unsorttedProducts + '\n' + p['name'] + '  ' + p['url']

    if i > 0:
        # Generate timestamp string
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        filename = f'data/unsorted_{brand}_{timestamp}.txt'
        unsorttedProducts = unsorttedProducts + '\n\n Total: ' + str(i)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(unsorttedProducts)   
    
    return [i, filename if i > 0 else None]


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

def scrapProducts(brandID, soup, category, subCategory, subSubCategory,piece, pageURL):
    # wrapper function to call brand specific scrapper
    products = []

    SCRAPER_MAP = {
        'Alkaram': Alkaram,
        'AhmadRaza': AhmadRaza,
        'Almirah': Almirah,
        "AnamAkhlaq":AnamAkhlaq,
        'GulAhmed': GulAhmed,
        "BeechTree":BeechTree,
        "BonanzaSatrangi":BonanzaSatrangi,
        'Generation': Generation,
        "Cambridge":Cambridge,
        'CrossStitch': CrossStitch,
        'Chinyere': Chinyere,
        'Charcoal': Charcoal,
        "Dhanak":Dhanak,
        "Diners":Diners,
        "EdenRobe":EdenRobe,
        'Ego': Ego,
        'LimeLight': LimeLight,
        'Ethnic': Ethnic,
        'FaizaRehman': FaizaRehman,
        'FatimaKhan': FatimaKhan,
        'NausheenWamiq': NausheenWamiq,
        'NomiAnsari': NomiAnsari,
        'Nureh': Nureh,
        'HafsaMalik': HafsaMalik,
        'Hijabi': Hijabi,
        'Outfitters': Outfitters,
        "JunaidJamshed":JunaidJamshed,
        "Lakhanay":Lakhanay,
        "Rasofficial":Rasofficial,
        # "SMP":SMP
    }
    
    # Get the appropriate scraper module
    scraper_module = SCRAPER_MAP.get(brandID)
    
    if not scraper_module:
        print(f'No scrapper available for the given brand: {brandID}')
        return []
    
    try:
        # Call the getProducts function from the appropriate module
        return scraper_module.getProducts(
            soup=soup,
            category=category,
            subCategory=subCategory,
            subSubCategory=subSubCategory,
            piece=piece,
            pageURL=pageURL
        )
    except AttributeError:
        print(f'Scraper module {brandID} is missing required getProducts function')
        return []
    except Exception as e:
        print(f'Error in {brandID} scraper: {str(e)}')
        return []

    # print('Product count: ' + str(len(products)) + ' products \n\n')    
    return products


def scrapBrand(brandID):
    print('Brand Name: ' + brandID)
    renamedFile = functions.renameDataFile(brandID)

    products = []
    navDetails = functions.getNavigationDetails(brandID)

    try:
        navFile = config.navigationFolder + '/' + navDetails['navigationFile']
        print(navFile)
    except:
        navFile = ''

    if navFile == '':
        print('Navigation file does not exist for: ' + brandID)
        return products

    productsFile = None

    with open(navFile, 'r') as f:
        navigation = json.load(f)

        for cat in navigation['categories']:
            for subCat in cat['subCategories']:
                for subSubCat in subCat['subSubCategories']:
                    print(f"\n{brandID} -> Category: {cat['name']} -> SubCategory: {subCat['name']} -> SubSubCategory: {subSubCat['name']}")

                    url = subSubCat['url']
                    category = cat['name']
                    subCategory = subCat['name']
                    subSubCategory = subSubCat['name']
                    piece = subSubCat.get('piece', '')
                    previousProducts = []
                    visitedUrls = set()

                    page = 1
                    maxNumberOfPages = config.maxNumberOfPages
                    if testEnvironment:
                        maxNumberOfPages = 2

                    pageUrl = url
                    while True:
                        # Standard brands use pagingVariable
                        if brandID.lower() != "almirah":
                            pageUrl = url + navDetails['pagingVariable'] + str(page)

                        if pageUrl in visitedUrls:
                            print("Repeated page URL detected. Stopping to prevent infinite loop.")
                            break
                        visitedUrls.add(pageUrl)

                        print(f"Page URL: {pageUrl}")
                        html = functions.getRequest(pageUrl, 'text')
                        soup = BeautifulSoup(html, 'html.parser')

                        tempProducts = scrapProducts(brandID, soup, category, subCategory, subSubCategory, piece, pageUrl)

                        if not tempProducts or tempProducts == previousProducts:
                            print("No new products or duplicate page detected. Breaking loop.")
                            break

                        previousProducts = tempProducts
                        products += tempProducts
                        productsFile = functions.saveDataToJsonFile(products, 'data_' + brandID)

                        # For Almirah (Shopify-based pagination)
                        if brandID.lower() == "almirah":
                            next_link = soup.select_one('link[rel=next], a.pagination__item--next[href], a[rel="next"]')
                            if not next_link:
                                print("No next page link found. Ending pagination.")
                                break
                            next_href = next_link.get('href') or next_link.get('src') or next_link['href']
                            pageUrl = next_href if next_href.startswith('http') else urljoin(url, next_href)
                        else:
                            page += 1
                            if page > maxNumberOfPages:
                                break

    return productsFile
