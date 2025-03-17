import requests
import config
import datetime
import json
import os
import pytz
import re

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
    # print(requestType)
    user_agent = config.user_agent
    r = requests.get(url, headers=user_agent)
    statusCode = r.status_code
    # print(statusCode)

    if (statusCode != 200):
        errorFilePath = 'errors//connection_' + str(datetime.datetime.now()) + '.txt'
        # Check if the file exists, create it if not
        if not os.path.exists(errorFilePath):
            with open(errorFilePath, 'w') as file:
                file.write('')

        with open(errorFilePath, 'a') as exc:
            exc.write('\n\nWrong Status Code \nStatus Code: ' +str(statusCode) + '\nURL: ' + url)

    if requestType == 'text':
        # print(r.text)
        return r.text
    elif requestType == 'json':
        return json.loads(r.text)

def renameDataFile(brandName):
    # Get today's date in UTC
    today = datetime.datetime.now(pytz.utc)
    yesterday = today - datetime.timedelta(days=1)

    existingFile = 'data/data_' + brandName + '_' + today.strftime("%Y-%m-%d") + '.json'
    renamedFile = 'data/data_' + brandName + '_' + yesterday.strftime("%Y-%m-%d") + '.json'

    if os.path.isfile(existingFile):
        os.rename(existingFile, renamedFile)
        return renamedFile
    else:
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

