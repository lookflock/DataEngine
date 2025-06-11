import requests
import config
import datetime
import json
import os
import pytz
import re
import config
# from firebaseConfig import db
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
import os
import datetime
import pytz

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
        print(f"[🔁] Renamed old file to: {candidate_name}")
        return candidate_name
    else:
        print(f"[ℹ️] No original file found to rename: {original_file}")
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
