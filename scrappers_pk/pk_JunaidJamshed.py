import json
from bs4 import BeautifulSoup
import re
import math
import os
import datetime
import functions
import config

def getProducts(soup, category, subCategory, subSubCategory, pageURL):
    products = []
    mainContainer = soup.find('div', {'class': 'products wrapper grid products-grid'})
    try:
        productsDiv = mainContainer.find_all('li', {'class': 'item product product-item'})
    
        for product in productsDiv:
            tmp_product = {
                'productID': '',
                'name': '',
                'oldPrice': '',
                'newPrice': '',
                'discount': '',
                'category': '',
                'subCategory': '',
                'subSubCategory': '',
                'url': '',
                'imageUrl': '',
                "pageUrl":pageURL,
                'views' : 0,
                'likes' : 0,
                'shares' : 0,
                'favourites' : 0,
                'list' : 0,
                'keywords': []
            }
            # with open("output3.html", "w", encoding="utf-8") as file:
            #     file.write(product.prettify())
            productID = product.find('a', {'class': 'product photo product-item-photo'})['data-product-id']

            try:
                temp = product.find('div', {'class': 'product details product-item-details'})
                name = temp.find('a', {'class': 'product-item-link'}).text.strip()
                name = name.split('|')[0]
                url = temp.find('a', {'class': 'product-item-link'})['href']
                imageUrl = product.find('a', {'class': 'product photo product-item-photo'}).find('img', {'class': 'product-image-photo lazy'})['data-original']
                try:
                    oldPrice = product.find('div', {'class': 'price-box price-final_price'}).find('span', {'class': 'price-wrapper', 'data-price-type': 'oldPrice'})['data-price-amount']
                    newPrice = product.find('div', {'class': 'price-box price-final_price'}).find('span', {'class': 'price-wrapper', 'data-price-type': 'finalPrice'})['data-price-amount']
                    discount = math.ceil((oldPrice - newPrice) / oldPrice * 100)  
                except:
                    newPrice = product.find('div', {'class': 'price-box price-final_price'}).find('span', {'class': 'price-wrapper', 'data-price-type': 'finalPrice'})['data-price-amount']
                    oldPrice = 0
                    discount = 0

                tmp_product['productID'] = productID
                tmp_product['name'] = functions.filterName(name,productID)
                tmp_product['oldPrice'] = functions.extractInt(oldPrice)
                tmp_product['newPrice'] = functions.extractInt(newPrice)
                tmp_product['discount'] = functions.extractInt(discount)
                tmp_product['url'] = url
                tmp_product['imageUrl'] =  imageUrl 
                tmp_product['category'] =  category
                tmp_product['subCategory'] = subCategory
                tmp_product['subSubCategory'] = subSubCategory
                products.append(tmp_product)

            except Exception as e:
                with open("errors/error_JunaidJamshed.json", "a") as f:
                    error_log = {
                    "datetime": datetime.datetime.now().isoformat(),
                    "product_name": str(name),
                    "exception_message": str(e),
                    "pageURL number": pageURL
                    }
                    json.dump(error_log, f)
    except:
        None

    return products



def getJunaidJamshedProductDetails(product): 
    try:
        html = functions.getRequest(product["url"], 'text')
        soup = BeautifulSoup(html, "html.parser")
        
        with open("output_JJ.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())

        
        availableSizes = []
        availableColors = []
        secondaryImages = []
        try:
            sizeElement = soup.find('div', {'class':'product-options-wrapper'})
            script = str(sizeElement.find('script'))

            json_data_match = re.search(r'({.*})', script, re.DOTALL)
            if json_data_match:
                json_data_str = json_data_match.group(1)
            else:
                raise ValueError("JSON data not found in the script")
            json_data = json.loads(json_data_str)
            availableSizes = [option['label'] for option in json_data['[data-role=swatch-options]']['Magento_Swatches/js/swatch-renderer']['jsonConfig']['attributes']['963']['options']]
        except:
            availableSizes = []

        try:
            colorElement = soup.find('div',{'class':'additional-attributes-wrapper'})
            td = colorElement.find('td').text.strip()
            availableColors.append(td)
        except:
            availableColors = []                

        productDescription = str(soup.find('div', {'class': "product attribute overview"})) + str(soup.find('table', {'class': "data table additional-attributes"}))

        mainContainer = soup.find('div',{'class':'MagicToolboxSelectorsContainer'})
        secondaryImagesDiv = mainContainer.find_all('a')
        
        for img in secondaryImagesDiv:
            if img is not None:
                if 'href' in img.attrs:
                    img_url = img["href"]
                    secondaryImages.append(img_url)

        secondaryImages= list(set(secondaryImages))
        # secondaryImages = [image for image in secondaryImages if image != product['imageUrl']]
        productDescription = functions.filterDescription(productDescription)
        availableSizes = functions.sortSizes('JunaidJamshed', availableSizes)
        availableColors = functions.sortColors('JunaidJamshed', availableColors)
        
        print(product["url"],productDescription,availableSizes,availableColors,secondaryImages[:4])


        product['Description'] = productDescription
        product['Sizes'] = availableSizes
        product['Colors'] = availableColors
        product['secondaryImages'] = secondaryImages[:4]
        product['sizeColors'] = functions.crossJoin(availableSizes,availableColors)




    except Exception as e:
        print ("An Error Occured While Getting The Product Details")
        print(product["url"],str(e))
        with open("errors/error_JunaidJamshed.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
                }
            json.dump(error_log, f)  
    return product              