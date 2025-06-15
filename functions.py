import shutil
import requests
import config
import datetime
import json
import os
import pytz
import re
import config
from firebaseConfig import db
from datetime import timedelta
from google.cloud.firestore import DELETE_FIELD
from google.cloud.firestore_v1 import DocumentSnapshot


# Get today's date in UTC
today = datetime.datetime.now(pytz.utc)
yesterday = today - datetime.timedelta(days=1)

def getDataFromJsonFilel(file_path):  
  with open(file_path, "r") as f:
    json_data = json.load(f)

  if isinstance(json_data, list):
    return json_data

  else:
    list_data = []
    for key in json_data:
      list_data.append(json_data[key])
    return list_data

def saveDataToJsonFile(data, filename):
    dataJson = json.dumps(data)
    file = 'data/' + filename + '_'+ today.strftime("%Y-%m-%d") + '.json'
    f = open(file, "w")
    f.write(dataJson)
    f.close()
    return file

def getNavigationDetails(brandID):
    # takes brandID as an input and returns the JSON navigation file for that brand
    file = config.navigationFile
    brandNavigationFile = ""
    navigationDetails = None

    with open(file, 'r') as f:
        brands = json.load(f)
        for b in brands:
            if b['brandID'] == brandID:
                # brandNavigationFile = config.navigationFolder + b['navigationFile']
                navigationDetails = b
                break
    return navigationDetails
def getRequest(url, requestType):
    user_agent = config.user_agent
    r = requests.get(url, headers=user_agent)
    statusCode = r.status_code

    if statusCode != 200:
        # Format timestamp safely
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        errorFilePath = f"errors/connection_{timestamp}.txt"

        # Ensure 'errors' directory exists
        os.makedirs('errors', exist_ok=True)

        # Write error details
        with open(errorFilePath, 'a') as exc:
            exc.write('\n\nWrong Status Code\n')
            exc.write(f'Status Code: {statusCode}\n')
            exc.write(f'URL: {url}\n')

    if requestType == 'text':
        return r.text
    elif requestType == 'json':
        return json.loads(r.text)
# def getRequest(url, requestType):
#     # print(requestType)
#     user_agent = config.user_agent
#     r = requests.get(url, headers=user_agent)
#     statusCode = r.status_code
#     # print(statusCode)

#     if (statusCode != 200):
#         errorFilePath = 'errors//connection_' + str(datetime.datetime.now()) + '.txt'
#         # Check if the file exists, create it if not
#         if not os.path.exists(errorFilePath):
#             with open(errorFilePath, 'w') as file:
#                 file.write('')

#         with open(errorFilePath, 'a') as exc:
#             exc.write('\n\nWrong Status Code \nStatus Code: ' +str(statusCode) + '\nURL: ' + url)

#     if requestType == 'text':
#         # print(r.text)
#         return r.text
#     elif requestType == 'json':
#         return json.loads(r.text)

# def renameDataFile(brandName):
#     # Get today's date in UTC
#     today = datetime.datetime.now(pytz.utc)
#     yesterday = today - datetime.timedelta(days=1)

#     existingFile = 'data/data_' + brandName + '_' + today.strftime("%Y-%m-%d") + '.json'
#     renamedFile = 'data/data_' + brandName + '_' + yesterday.strftime("%Y-%m-%d") + '.json'

#     if os.path.isfile(existingFile):
#         os.rename(existingFile, renamedFile)
#         return renamedFile

#     else:
#         return None


def renameDataFile(brandName):
    today = datetime.datetime.now(pytz.utc).strftime("%Y-%m-%d")
    base_name = f"data/data_{brandName}_{today}"
    ext = ".json"

    version = 1
    while True:
        candidate_name = f"{base_name}_{version}{ext}"
        if not os.path.isfile(candidate_name):
            break
        version += 1

    original_file = f"{base_name}{ext}"

    if os.path.isfile(original_file):
        os.rename(original_file, candidate_name)
        print(f"Renamed old file to: {candidate_name}")
        return candidate_name
    else:
        print(f"No original file found to rename: {original_file}")
        return None


def extractInt(string):
    if isinstance(string, str):
        string = string.replace(' ', '')  # Remove spaces
        string = string.replace('PKR.', '')  # Remove 'PKR.'
        string = string.replace('Rs.', '')
        string = string.replace('USD', '')  # Remove 'USD'
        string = string.replace('$', '')  # Remove '$'
        parts = string.split('.')  # Split by '.'
        integer_part = parts[0] if len(parts) > 0 else ''  # Get the integer part
        # Check if the integer part is not empty before conversion
        if integer_part:
            return int(''.join(filter(str.isdigit, integer_part)))
        else:
            return 0  # Or another default value if appropriate
    elif isinstance(string, int):
        return string

def filterName(name, id):
    # Convert name to lowercase for initial processing
    # print("Beginging of filter Function ",name)
    name_lower = name.lower()
    
    # Remove any text within parentheses and replace the ID
    name_cleaned = re.sub(r'\(.*?\)', '', name_lower)
    name_cleaned = name_cleaned.replace(id.lower(), '')
    name_cleaned = name_cleaned.replace('-', ' ')
    name_cleaned = name_cleaned.replace('unstitched', '')
    name_cleaned = name_cleaned.replace('stitched', '')
    name_cleaned = ' '.join(name_cleaned.split()).strip()

    # Define replacement dictionary
    replacement_dict = {
        '1-Pc': ['1PC', '1 PC', '1 piece', '1 Piece', '1 PIECE', '1pcs','1Pcs','1-pcs'],
        '2-Pc': ['Co-Ord', 'Coord', 'Co-ord', 'Cor-ord', '2pcs','2- Piece','2 Pc', '2Pcs', '2-pcs','2 PIECE', '2-Piece', '2-piece', '2 piece', '2 Piece', '2Piece', '2PC', '2 piece', 'two piece', 'TWO PIECE', '2 PC', '2  PC','2 pc'],
        '3-Pc': ['3PC', '3 PC', '3 Piece', 'three piece', '3pcs','3-pc', '3 piece','3-pcs' ,'3Pcs','THREE PIECE', 'THREEPIECE', '3 PIECE', '3Pcs', '3 pc', '3 Pc']
    }
    
    # Perform replacements
    for replacement, phrases in replacement_dict.items():
        for phrase in phrases:
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            name_cleaned = pattern.sub(replacement, name_cleaned)

    # Capitalize all words but leave '1-Pc', '2-Pc', and '3-Pc' in their specific format
    words = name_cleaned.split()
    capitalized_words = []
    for word in words:
        if word in replacement_dict.keys():
            capitalized_words.append(word)  # Preserve specific format
        else:
            capitalized_words.append(word.capitalize())
    name_cleaned = ' '.join(capitalized_words)
    # print("Ending of filter Function ",name_cleaned)

    return name_cleaned


def saveDataToJsonFile(data, filename):
    dataJson = json.dumps(data)
    file = 'data/' + filename + '_'+ today.strftime("%Y-%m-%d") + '.json'
    f = open(file, "w")
    f.write(dataJson)
    f.close()
    return file

def fetchbrandName(brandName):
    filename = config.navigationFile
    with open(filename, 'r') as f:
        brands = json.load(f)

    for brand in brands:
        if brand["brandID"] == brandName:
            return brand["displayName"]
    return -1


def sortSizes(brandName, sizes):
    if len(sizes) == 0:
        return sizes
    
    # Write generalized sizes to file
    with open(f'{brandName}_sizes_sorted.txt', 'a') as file:
        file.write(str(sizes) + '\n')
        
    size_mapping = {
        'XXS': ['xxs', 'xx-s', 'xx-small', 'extra extra small', 'extra-extra-small', 'xxs slf', 'xxs rgf'],
        'XS': ['xs', 'x-s', 'x small', 'x-small', 'extra small', 'extra-small', 'xs slf', 'xs rgf'],
        'S': ['s', 'small', 's slf', 's rgf'],
        'M': ['m', 'medium', 'm rgf', 'm slf'],
        'L': ['l', 'large', 'l rgf', 'l slf'],
        'XL': ['xl', 'x large', 'x-l', 'x-large', 'xl rgf', 'xl slf', '3xl', '4xl', '5xl', '6xl'],
        'XXL': ['xxl', 'xx-l', 'xx large', 'xx-large', '2xl', '2x-l', '2x-large', 'xxl rgf']
    }

    # Add numerical sizes
    number_sizes = [str(i) for i in range(6, 64, 2)]

    reverse_mapping = {variant.lower(): key for key, variants in size_mapping.items() for variant in variants}
    
    generalized_sizes = []
    for size in sizes:
        size_lower = size.lower()
        if size_lower in reverse_mapping:
            generalized_sizes.append(reverse_mapping[size_lower])
        elif size in number_sizes:
            generalized_sizes.append(size)

    # Sort the sizes
    predefined_order = ["XXS", "XS", "S", "M", "L", "XL", "XXL"]
    
    def size_key(s):
        if s.isdigit():
            return (1, int(s))  # Sort numbers numerically
        return (0, predefined_order.index(s)) if s in predefined_order else (2, s)  # Sort predefined sizes and others alphabetically

    generalized_sizes_sorted = sorted(set(generalized_sizes), key=size_key)

    return generalized_sizes_sorted


def UploadProducts(brandName):

    file = open('data/data_' + brandName + '_' + today.strftime("%Y-%m-%d") + '.json')
    data = json.load(file)
    # for testing env we only upload a few data 
    #dataLen = len(data)//2
    #data = data[:dataLen]
    menCount= 0
    womenCount = 0
    menSubCategoryCount = {}
    womenSubCategoryCount = {}
    brand_Sizes = []
    product_Colors = set()


    brandId = brandName
    brandName = fetchbrandName(brandName)


    for d in data:
        supplier = brandId
        brandDisplayName = brandName
        productID = str(d.get('productID', ''))
        name = d.get('name', None)
        oldPrice = d.get('oldPrice', None)
        newPrice = d.get('newPrice', None)
        discount = int(d.get('discount', 0))
        category = d.get('category', None)
        subCategory = d.get('subCategory', None)
        subSubCategory = d.get('subSubCategory', None)
        url = d.get('url', None)
        imageUrl = d.get('imageUrl', None)
        keywords = d.get('keywords',None)
        views = d.get('views',None)
        likes = d.get('likes',None)
        shares = d.get('shares',None)
        favourites = d.get('favourites',None)
        colors = d.get('Colors',[])
        sizes = d.get('Sizes',[])
        description = d.get('Description',None)
        sizeColors = d.get('sizeColors',None)
        secondaryImages = d.get('secondaryImages',None)
        lst = d.get('list',None)
        piece = d.get('piece', None)
        views = 0
        likes = 0
        shares = 0
        favourites = 0
        lst = 0
        date = datetime.datetime.now()


        if sizes not in brand_Sizes:
            brand_Sizes.append(sizes)
        for color in colors:
            product_Colors.add(color)

        product = {
            'id':productID,
            'brandName':brandDisplayName,
            'name': str(name),
            'oldPrice': oldPrice,
            'newPrice': newPrice,
            'discount': discount,
            'category': category,
            'subCategory': subCategory,
            'subSubCategory': subSubCategory,
            'url': str(url),
            'imageUrl': imageUrl,
            'supplier': supplier,
            'status': 1,
            'views' : views,
            'likes' : likes,
            'shares' : shares,
            'favourites' : favourites,
            'list' : lst,
            'keywords' : keywords,
            'dateCreated': date,
            'dateLastUpdate': date,
            'description' : description,
            'colors' : colors,
            'sizes' : sizes,
            'sizeColors' :sizeColors,
            'secondaryImages':secondaryImages,
            'promoted' : False,
            'advertised': False,
            'piece':piece
        }


        try:
            db.collection('products').document(productID).set(product)
            
        except Exception as e:
            print(f"ERROR: Failed to add product {productID}: {str(e)}")

# from datetime import datetime, timedelta
def GetSummary(brandName, details=False):
    summary_file = None
    data_dir = "data"

    # Look for the most recent summary file
    today = datetime.datetime.today()
    for days_back in range(30):  # limit to search last 30 days
        check_date = (today - timedelta(days=days_back)).strftime("%Y-%m-%d")
        filename = f"data_{brandName}_{check_date}_summary.json"
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            summary_file = filepath
            break

    if not summary_file:
        print(f"[Info] No summary file found for brand '{brandName}' in the last 30 days.")
        return

    # Load and print summary
    with open(summary_file, 'r', encoding='utf-8') as f:
        summary = json.load(f)

    print("\nSummary")
    print(f"Total Products: {summary.get('Total Products', 0)}")
    print(f"New Products: {summary['New Products']['count']}")
    print(f"Updated Products: {summary['Price Increased']['count'] + summary['Price Decreased']['count']}")
    print(f"Deleted Products: {summary['Deleted Products']['count']}")

    if details:
        print("\nDetailed Summary")
        print(f"Total products : {summary.get('Total Products', 0)}")

        print(f"New products : {summary['New Products']['count']}")
        print(f"    {summary['New Products']['ids']}")

        updated_ids = summary['Price Increased']['ids'] + summary['Price Decreased']['ids']
        print(f"Updated Products : {len(updated_ids)}")
        print(f"    {updated_ids}")

        print(f"Deleted Products : {summary['Deleted Products']['count']}")
        print(f"    {summary['Deleted Products']['ids']}")


def default_converter(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    return str(obj)

def fetch_and_save_products_by_brand(brandName):
    products_ref = db.collection('products').where(filter=('supplier', '==', brandName))
    docs = products_ref.stream()

    # Group products by brand name
    brand_products = {}
    for doc in docs:
        data = doc.to_dict()
        brand = data.get("supplier", ["UnknownBrand"])
        if isinstance(brand, list):
            brand = brand[0] if brand else "UnknownBrand"
        if brand not in brand_products:
            brand_products[brand] = []
        brand_products[brand].append(data)

    # Create output directory if it doesn't exist
    output_dir = "ProductionData"
    os.makedirs(output_dir, exist_ok=True)

    # Save each brand's products to a separate JSON file
    today = datetime.datetime.today().strftime("%Y-%m-%d")
    for brand, products in brand_products.items():
        sanitized_brand = brand.replace(" ", "_").replace("/", "_")
        filename = f"{output_dir}/data_{sanitized_brand}_{today}_from_firebase.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(products, f, indent=4, ensure_ascii=False, default=default_converter)
        print(f"Saved {len(products)} products for brand '{brand}' to {filename}")


def clean_firebase_json_file_fields(
    file_path='firestore/data_Ahmad_Raza_2025-06-12_from_firebase.json',
    fields_to_delete=None
):
    if fields_to_delete is None:
        fields_to_delete = ['promoted', 'advertised', 'sizeColors', 'brandName', 'colors']

    # Step 1: Load JSON file
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Step 2: Remove specified fields from each product
    for product in data:
        for field in fields_to_delete:
            product.pop(field, None)  # remove field if it exists

    # Step 3: Save updated JSON back to the same file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"Removed fields {fields_to_delete} from {len(data)} products in '{file_path}'.")



def delete_field_from_docs(field_name,brandName):
    # docs = db.collection('products').where(field_name, '!=', None).stream()
    docs = db.collection('products') \
         .where(filter=('supplier', '==', brandName)) \
         .where(filter=(field_name, '!=', None)) \
         .stream()

    count = 0
    batch = db.batch()

    for doc in docs:
        batch.update(doc.reference, {field_name: DELETE_FIELD})
        count += 1

        if count % 500 == 0:
            batch.commit()
            batch = db.batch()

    if count % 500 != 0:
        batch.commit()

    print(f"Cleaned '{field_name}' from {count} documents.")


def clean_product_fields_optimized(brandName):
    fields = ['advertised','promoted','sizeColors', 'brandName', 'colors']
    for field in fields:
        delete_field_from_docs(field,brandName)

def make_json_serializable(data):
    """Recursively convert Firestore timestamps to ISO format strings."""
    if isinstance(data, dict):
        return {k: make_json_serializable(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [make_json_serializable(v) for v in data]
    elif isinstance(data, datetime.datetime):
        return data.isoformat()
    else:
        return data

    
def fetch_brands_available_in(brandName):
    """
    Fetches 'availableIn' subcollections for all brand's products.
    Returns: dict { product_id: [availableIn_documents] }
    """
    query = db.collection('products').where(filter('supplier', '==', brandName))
    products = query.stream()

    result = {}
    product_count = 0
    available_count = 0

    for doc in products:
        product_id = doc.id
        available_ref = db.collection('products').document(product_id).collection('availableIn')
        available_docs = available_ref.stream()

        available_list = []
        for sub_doc in available_docs:
            sub_data = sub_doc.to_dict()
            sub_data['id'] = sub_doc.id
            available_list.append(make_json_serializable(sub_data))


        if available_list:
            result[product_id] = available_list
            available_count += len(available_list)

        product_count += 1

    print(f"[✔] {brandName} Products: {product_count}, 'availableIn' docs: {available_count}")
    return result

def fetch_available_in_for_all_products(brandName):
    data = fetch_brands_available_in(brandName)
    filename = f"AvailableIn/{brandName}_available_in_data.json"

    with open(filename, "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def delete_all_except(brandName):
    """
    Deletes all documents in the 'products' collection where supplier == 'AhmadRaza',
    except the ones whose document IDs are in doc_ids_to_keep.
    """
    filename = f"AvailableIn/{brandName}_available_in_data.json"
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extract all productIds
    product_ids = []

    for key, entries in data.items():
        for entry in entries:
            if 'productId' in entry:
                product_ids.append(entry['productId'])

    collection_ref = db.collection('products').where(filter=('supplier', '==', brandName))
    docs = collection_ref.stream()

    deleted_count = 0
    for doc in docs:
        if doc.id not in product_ids:
            doc.reference.delete()
            deleted_count += 1

    print(f"Deleted {deleted_count} documents from 'products', keeping only: {product_ids}")


def find_common_products(file1, file2):
    # Load products from both files
    with open(file1, 'r', encoding='utf-8') as f1:
        data1 = json.load(f1)

    with open(file2, 'r', encoding='utf-8') as f2:
        data2 = json.load(f2)

    # Convert product lists to dicts keyed by 'id'
    products1 = {product['name']: product for product in data1 if 'id' in product}
    products2 = {product['id']: product for product in data2 if 'id' in product}

    # Find common product IDs
    common_ids = set(products1.keys()) & set(products2.keys())

    # Collect matching products
    common_products = [products1[pid] for pid in common_ids]

    print(f"Found {len(common_products)} common products.")
    return common_products



def save_invalid_urls_file(brandName, invalids):
    from datetime import datetime
    date_str = datetime.now().strftime('%Y-%m-%d')
    invalids_dir = "InvalidURLs"
    base_name = f"invalidURLS_{brandName}_{date_str}"
    ext = ".json"

    latest_file = os.path.join(invalids_dir, base_name + ext)

    if os.path.exists(latest_file):
        suffix = 1
        while True:
            old_file_with_suffix = os.path.join(invalids_dir, f"{base_name}_{suffix}{ext}")
            if not os.path.exists(old_file_with_suffix):
                shutil.move(latest_file, old_file_with_suffix)
                print(f"[Info] Renamed old invalid Urls to: {old_file_with_suffix}")
                break
            suffix += 1

    with open(latest_file, 'w', encoding='utf-8') as f:
        json.dump(invalids, f, ensure_ascii=False, indent=2)

    print(f"[Invalid Urls] Saved to: {latest_file}")


def verify_image_url(url, timeout=5):
    """
    Returns True if the image URL is valid (status code 200), False otherwise.
    """
    try:
        response = requests.head(url, timeout=timeout)
        return response.status_code == 200
    except requests.RequestException:
        return False


def save_invalid_urls(brandName,productsFile):
    current_filename = os.path.basename(productsFile)

    all_files = os.listdir("data")
    brand_files = [
        f"data/{f}" for f in all_files
        if f.startswith(f"data_{brandName}_") and f.endswith(".json") and f != current_filename and "_summary" not in f and "_new_products" not in f
    ]
    from scrapper import extract_timestamp
    brand_files = sorted(
        brand_files,
        key=lambda f: extract_timestamp(f),
        reverse=True
    )

    # Load JSON data
    try:
        with open(productsFile, 'r', encoding='utf-8') as f:
            current_products = json.load(f)

    except Exception as e:
        print(f"[Error] Failed to load JSON in Save Invalid Urls: {e}")
        return None
    
    invalids = []
    count=0
    for product in current_products:
        url = product.get("imageUrl")
        print(f"Verifying Image URL for {product['id']}")
        if url and not verify_image_url(url):
            count+=1
            invalids.append({
                "id": product.get("id"),
                "invalidURL": url
            })
    print(f"Total {count} Invlid URLs found in {brandName}")

    # with open(output_file, 'w', encoding='utf-8') as f:
    #     json.dump(invalids, f, indent=2)
    save_invalid_urls_file(brandName,invalids)

import json
import requests

def verifyProducts(brandName):
    from scrapper import find_latest_files
    print(f"[verification] Verifying new products for: {brandName}")

    # Get latest product and summary file
    try:
        productsFile, summaryFile = find_latest_files(brandName)
        print(f"[verification] Using products file: {productsFile}")
        print(f"[verification] Using summary file: {summaryFile}")
    except Exception as e:
        print(f"[Error] {e}")
        return

    # Load full product list
    try:
        with open(productsFile, 'r', encoding='utf-8') as f:
            all_products = json.load(f)
    except Exception as e:
        print(f"[verification] Failed to read {productsFile}: {e}")
        return

    # Load new product IDs from summary
    try:
        with open(summaryFile, 'r', encoding='utf-8') as f:
            summary = json.load(f)
        new_ids = summary.get("New Products", {}).get("ids", [])
    except Exception as e:
        print(f"[verification] Failed to read {summaryFile}: {e}")
        return

    if not new_ids:
        print("[verification] No new products to verify.")
        return

    # Build lookup map of all products by productID
    product_map = {p["id"]: p for p in all_products}

    # Track modified state
    modified = False
    for pid in new_ids:
        product = product_map.get(pid)
        if not product:
            print(f"[verification] Product ID not found: {pid}")
            continue

        # Validate newPrice
        new_price = product.get("newPrice")
        if new_price is None:
            product["valid"] = 0
            print(f"[verification] newPrice is None for product ID {pid}")
            modified = True
        elif isinstance(new_price, str):
            product["valid"] = 0
            print(f"[verification] newPrice is a string for product ID {pid}")
            modified = True
        elif new_price == 0:
            product["valid"] = 0
            print(f"[verification] newPrice is 0 for product ID {pid}")
            modified = True

        # Validate oldPrice
        old_price = product.get("oldPrice")
        if old_price is None:
            product["valid"] = 0
            print(f"[verification] oldPrice is None for product ID {pid}")
            modified = True
        elif isinstance(old_price, str):
            product["valid"] = 0
            print(f"[verification] oldPrice is a string for product ID {pid}")
            modified = True
        # elif old_price == 0:
        #     product["valid"] = 0
        #     print(f"[verification] oldPrice is 0 for product ID {pid}")
        #     modified = True

        # Check name
        name = product.get("name")
        if not name or name.strip() == "":
            product["valid"] = 0
            print(f"[verification] Missing name for product ID {pid}")
            modified = True

        # Check imageUrl
        image_url = product.get("imageUrl")
        if image_url:
            try:
                response = requests.head(image_url, timeout=5)
                if response.status_code != 200:
                    print(f"[verification] Invalid image URL for product ID {pid}")
                    product["valid"] = 0
                    modified = True
            except Exception as e:
                product["valid"] = 0
                print(f"[verification] Error checking image URL for product ID {pid}: {e}")
                modified = True
        else:
            product["valid"] = 0
            print(f"[verification] Missing image URL for product ID {pid}")
            modified = True

    # Save updated products if modified
    if modified:
        try:
            with open(productsFile, 'w', encoding='utf-8') as f:
                json.dump(all_products, f, ensure_ascii=False, indent=2)
            print(f"[verification] Updated {productsFile} with verified results.")
        except Exception as e:
            print(f"[verification] Failed to write updated products: {e}")
    else:
        print("[verification] No changes needed. All products are valid.")
