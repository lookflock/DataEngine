import requests
import config
import json
from bs4 import BeautifulSoup
import functions
import os
from urllib.parse import urljoin
import pytz
import re
import importlib

import shutil
from datetime import datetime, timedelta


from lib.logger import log_info, log_error

import scrappers_pk.pk_AhmadRaza as AhmadRaza
import scrappers_pk.pk_Alkaram as Alkaram
import scrappers_pk.pk_Almirah as Almirah
import scrappers_pk.pk_AnamAkhlaq as AnamAkhlaq
import scrappers_pk.pk_BeechTree as BeechTree
import scrappers_pk.pk_BonanzaSatrangi as BonanzaSatrangi
import scrappers_pk.pk_Cambridge as Cambridge
import scrappers_pk.pk_Deepakperwani as Deepakperwani
import scrappers_pk.pk_Chinyere as Chinyere
import scrappers_pk.pk_Chicophicial as Chicophicial
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


def sortProducts(products):#sorting only new products
# def sortProducts(file): #if we send filename path to sort all products not just new
#     products = functions.getDataFromJsonFilel(file)
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
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        filename = f'data/unsorted_{brand}_{timestamp}.txt'
        unsorttedProducts = unsorttedProducts + '\n\n Total: ' + str(i)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(unsorttedProducts)   
    
    return [i, filename if i > 0 else None]


def categoriseAllProducts(brandName, fileName):
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

def find_latest_files(brandName):
    base_path = "data"
    max_days_back = 10
    for i in range(max_days_back):
        date_str = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        products_file = os.path.join(base_path, f"data_{brandName}_{date_str}.json")
        summary_file = os.path.join(base_path, f"data_{brandName}_{date_str}_summary.json")
        if os.path.exists(products_file) and os.path.exists(summary_file):
            return products_file, summary_file
    return None, None


def categoriseProducts(brandName):
    products_file, summary_file = find_latest_files(brandName)

    if not products_file or not summary_file:
        print(f"No recent product/summary file found for brand: {brandName}")
        return

    print(f"Using products file: {products_file}")
    print(f"Using summary file: {summary_file}")

    # Load summary file to get new product IDs
    with open(summary_file, 'r', encoding='utf-8') as f:
        summary = json.load(f)

    # new_ids = summary.get("New Products", [])[1] if "New Products" in summary else []
    new_ids = summary.get("New Products", {}).get("ids", [])
    if not new_ids:
        print("No new products to categorize.")
        return

    # Load products file
    with open(products_file, 'r', encoding='utf-8') as f:
        all_products = json.load(f)

    # Filter only new products
    id_set = set(new_ids)
    new_products = [p for p in all_products if p.get("id") in id_set]

    # Categorize new products
    categorized = sortProducts(new_products)

    # Replace updated ones in the full list
    categorized_map = {p['id']: p for p in categorized}
    updated_products = [
        categorized_map.get(p['id'], p)
        for p in all_products
    ]

    # Save updated full product list
    with open(products_file, 'w', encoding='utf-8') as f:
        json.dump(updated_products, f, ensure_ascii=False, indent=2)

    # Optional: Get unsorted stats
    unsortedData = getUnsortedProducts(categorized, brandName)
    print(f"Categorized and updated {len(categorized)} product(s).")
    print(f"Unsorted Products: {unsortedData}")

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
            product_id = product.get("id")
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
        "Deepakperwani":Deepakperwani,
        'Generation': Generation,
        "Cambridge":Cambridge,
        'CrossStitch': CrossStitch,
        'Chinyere': Chinyere,
        'Charcoal': Charcoal,
        'Chicophicial':Chicophicial,
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
    print(renamedFile)
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

                    page = 1
                    maxNumberOfPages = config.maxNumberOfPages if not testEnvironment else 2
                    paginationType = None  # Automatically detect pagination style
                    visitedUrls = set()
                    pageUrl = url  # Will be updated if number-based paging

                    while True:
                        # If number-based (default assumption), construct URL with page number
                        if paginationType != 'link':
                            pageUrl = url + navDetails['pagingVariable'] + str(page)

                        if pageUrl in visitedUrls:
                            print("Detected loop, this page was already visited.")
                            break
                        visitedUrls.add(pageUrl)

                        print(f"Page URL: {pageUrl}")
                        html = functions.getRequest(pageUrl, 'text')
                        soup = BeautifulSoup(html, 'html.parser')

                        tempProducts = scrapProducts(brandID, soup, category, subCategory, subSubCategory, piece, pageUrl)

                        if not tempProducts or tempProducts == previousProducts:
                            print("No new products or repeated results. Stopping pagination.")
                            break

                        previousProducts = tempProducts
                        products += tempProducts
                        productsFile = functions.saveDataToJsonFile(products, 'data_' + brandID)

                        # Auto-detect pagination type after first page
                        if paginationType is None:
                            next_link = soup.select_one('link[rel=next], a.pagination__item--next[href], a[rel="next"]')
                            if next_link:
                                paginationType = 'link'
                                print("Pagination style: LINK-based detected.")
                            else:
                                paginationType = 'number'
                                print("Pagination style: NUMBER-based detected.")

                        # Handle based on pagination type
                        if paginationType == 'link':
                            next_link = soup.select_one('link[rel=next], a.pagination__item--next[href], a[rel="next"]')
                            if not next_link:
                                print("No next link found. Ending.")
                                break
                            next_href = next_link.get('href') or next_link.get('src') or next_link['href']
                            pageUrl = next_href if next_href.startswith('http') else urljoin(url, next_href)
                        else:
                            page += 1
                            if page > maxNumberOfPages:
                                print("Reached max number of pages.")
                                break

    return productsFile


# import os
# import json
# import datetime
# import re

# def extract_timestamp(filename):
#     match = re.match(r"data_(.+)_(\d{4}-\d{2}-\d{2})(?:_(\d+))?\.json$", os.path.basename(filename))
#     if match:
#         _, date_str, suffix = match.groups()
#         dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
#         return dt, int(suffix) if suffix else 0
#     return None, None

# def compareWithPrevious(brandName, current_file_path):
#     current_filename = os.path.basename(current_file_path)

#     # Get all files for the same brand
#     all_files = os.listdir("data")
#     brand_files = [
#         f"data/{f}" for f in all_files
#         if f.startswith(f"data_{brandName}_") and f.endswith(".json") and f != current_filename
#     ]

#     # Sort files by timestamp and suffix
#     brand_files = sorted(
#         brand_files,
#         key=lambda f: extract_timestamp(f),
#         reverse=True
#     )

#     # Find most recent valid previous file
#     previous_file = None
#     for f in brand_files:
#         if os.path.basename(f) != os.path.basename(current_file_path):
#             previous_file = f
#             break

#     if not previous_file:
#         print(f"[Info] No previous file found for brand {brandName}.")
#         return None

#     print(f"[Info] Comparing against: {previous_file}")

#     # Load product lists
#     try:
#         with open(current_file_path, 'r', encoding='utf-8') as f:
#             current_products = json.load(f)

#         with open(previous_file, 'r', encoding='utf-8') as f:
#             previous_products = json.load(f)
#     except Exception as e:
#         print(f"[Error] Failed to load JSON: {e}")
#         return None

#     previous_ids = {p.get("productID") for p in previous_products}
#     new_products = [p for p in current_products if p.get("productID") not in previous_ids]

#     if not new_products:
#         print(f"No new products found for brand {brandName}.")
#         return None

#     # Auto-increment output file name
#     base_name = f"data/new_products_{brandName}_{datetime.datetime.now().strftime('%Y-%m-%d')}"
#     suffix = 0
#     output_file = f"{base_name}.json"
#     while os.path.exists(output_file):
#         suffix += 1
#         output_file = f"{base_name}_{suffix}.json"

#     # Save new products
#     with open(output_file, 'w', encoding='utf-8') as f:
#         json.dump(new_products, f, ensure_ascii=False, indent=2)

#     print(f"Found {len(new_products)} new product(s).")
#     print(f"New products file: {output_file}")
#     return output_file

def save_summary_file(brandName, summary):
    date_str = datetime.now().strftime('%Y-%m-%d')
    summary_dir = "data"
    base_name = f"data_{brandName}_{date_str}_summary"
    ext = ".json"

    latest_file = os.path.join(summary_dir, base_name + ext)

    # If a summary file already exists for today, rename it with a suffix
    if os.path.exists(latest_file):
        suffix = 1
        while True:
            old_file_with_suffix = os.path.join(summary_dir, f"{base_name}_{suffix}{ext}")
            if not os.path.exists(old_file_with_suffix):
                shutil.move(latest_file, old_file_with_suffix)
                print(f"[Info] Renamed old summary to: {old_file_with_suffix}")
                break
            suffix += 1

    # Now save the latest summary without suffix
    with open(latest_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"[Summary] Saved to: {latest_file}")

def extract_timestamp(filename):
    name = os.path.basename(filename)
    match = re.match(r".*_(\d{4}-\d{2}-\d{2})(?:_(\d+))?\.json$", name)
    if match:
        date_str = match.group(1)
        suffix = int(match.group(2)) if match.group(2) else 0
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return (date_obj, suffix)
        except ValueError:
            return (datetime.min, 0)
    return (datetime.min, 0)

def compareWithPrevious(brandName, current_file_path):
    current_filename = os.path.basename(current_file_path)

    all_files = os.listdir("data")
    brand_files = [
        f"data/{f}" for f in all_files
        if f.startswith(f"data_{brandName}_") and f.endswith(".json") and f != current_filename and "_summary" not in f and "_new_products" not in f
    ]

    brand_files = sorted(
        brand_files,
        key=lambda f: extract_timestamp(f),
        reverse=True
    )

    previous_file = None
    for f in brand_files:
        if os.path.basename(f) != current_filename:
            previous_file = f
            break

    if not previous_file:
        print(f"[Info] No previous file found for brand {brandName}.")
        return None

    print(f"[Info] Comparing against: {previous_file}")

    # Load JSON data
    try:
        with open(current_file_path, 'r', encoding='utf-8') as f:
            current_products = json.load(f)

        with open(previous_file, 'r', encoding='utf-8') as f:
            previous_products = json.load(f)
    except Exception as e:
        print(f"[Error] Failed to load JSON: {e}")
        return None

    current_map = {p["id"]: p for p in current_products}
    previous_map = {p["id"]: p for p in previous_products}

    new_products = []
    price_increased = []
    price_decreased = []
    deleted_products = []

    # Find new and changed products
    for pid, product in current_map.items():
        if pid not in previous_map:
            new_products.append(pid)
        else:
            old_price = float(previous_map[pid].get("newPrice", 0))
            new_price = float(product.get("newPrice", 0))
            if new_price > old_price:
                price_increased.append(pid)
            elif new_price < old_price:
                price_decreased.append(pid)

    # Find deleted products
    for pid, product in previous_map.items():
        if pid not in current_map:
            deleted = product.copy()
            deleted["status"] = 0
            current_products.append(deleted)
            deleted_products.append(pid)

    # Save updated current products with deleted ones added
    with open(current_file_path, 'w', encoding='utf-8') as f:
        json.dump(current_products, f, ensure_ascii=False, indent=2)

    # Prepare summary with additional "Total Products"
    summary = {
        "Total Products": len(current_products),
        "New Products": {
            "count": len(new_products),
            "ids": new_products
        },
        "Price Increased": {
            "count": len(price_increased),
            "ids": price_increased
        },
        "Price Decreased": {
            "count": len(price_decreased),
            "ids": price_decreased
        },
        "Deleted Products": {
            "count": len(deleted_products),
            "ids": deleted_products
        },
    }

    save_summary_file(brandName, summary)


def scrapDetails(brandName):
    print(f"Enriching new product details for: {brandName}")

    # Get latest product and summary file
    try:
        productsFile, summaryFile = find_latest_files(brandName)
        print(f"Using products file: {productsFile}")
        print(f"Using summary file: {summaryFile}")
    except Exception as e:
        print(f"[Error] {e}")
        return

    # Load full product list
    try:
        with open(productsFile, 'r', encoding='utf-8') as f:
            all_products = json.load(f)
    except Exception as e:
        print(f"Failed to read {productsFile}: {e}")
        return

    # Load new product IDs from summary
    try:
        with open(summaryFile, 'r', encoding='utf-8') as f:
            summary = json.load(f)
        new_ids = summary.get("New Products", {}).get("ids", [])
    except Exception as e:
        print(f"Failed to read {summaryFile}: {e}")
        return

    if not new_ids:
        print("No new products to enrich.")
        return

    # Build lookup map of all products by productID
    product_map = {p["id"]: p for p in all_products}

    # Fetch full product objects using new_ids
    detailed_products = []
    for pid in new_ids:
        product = product_map.get(pid)
        if product:
            detailed_products.append(product)
        else:
            print(f"Product ID not found in full list: {pid}")

    if not detailed_products:
        print("No matching products found to enrich.")
        return

    # Dynamically import brand scraper
    module_name = f"scrappers_pk.pk_{brandName}"
    try:
        brand_module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        print(f"Brand scraper not found: {module_name}")
        return

    func_name = f"get{brandName}ProductDetails"
    if not hasattr(brand_module, func_name):
        print(f"Function {func_name} not found in {module_name}")
        return

    getProductDetails = getattr(brand_module, func_name)

    # Enrich each new product
    enriched_products = []
    for product in detailed_products:
        enriched = getProductDetails(product)
        enriched_products.append(enriched)

    # Replace old entries with enriched ones in full product list
    enriched_ids = {p["id"] for p in enriched_products}
    updated_products = [
        p if p["id"] not in enriched_ids else next(ep for ep in enriched_products if ep["id"] == p["id"])
        for p in all_products
    ]

    # Overwrite the original scraped file with updated data
    try:
        with open(productsFile, 'w', encoding='utf-8') as f:
            json.dump(updated_products, f, ensure_ascii=False, indent=2)
        print(f"[Success] Enriched products updated in: {productsFile}")
    except Exception as e:
        print(f"[Error] Failed to update enriched data in file: {e}")
