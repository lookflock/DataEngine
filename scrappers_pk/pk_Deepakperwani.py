import json
from bs4 import BeautifulSoup
import datetime
import math
import os
import random
import functions


# def getProducts(soup, category, subCategory, subSubCategory, page):
# def getProducts(soup, category, subCategory, subSubCategory,piece, pageURL):

#     products = []
#     try:
#         mainContainer = soup.find('div', {'class': 'item-grid'})
#         productsDiv = mainContainer.find_all('div',{'class': 'item-box'})

#     except:
#         return products

#     with open("output.html", "w", encoding="utf-8") as f:
#            f.write(soup.prettify())
    
#     for i in productsDiv:
#         tmp_product = {
#                 'productID': '',
#                 'name': '',
#                 'oldPrice': '',
#                 'newPrice': '',
#                 'discount': '',
#                 'category': '',
#                 'subCategory': '',
#                 'subSubCategory': '',
#                 'url': '',
#                 'imageUrl': '',
#                 'views' : 0,
#                 'likes' : 0,
#                 'shares' : 0,
#                 'favourites' : 0,
#                 'list' : 0,
#                 'keywords': [],
#                 'piece': ''
#             }
        
        
#         nameDiv = i.find('div', {'class': 'picture'})
#         name = i.find('h2',{'class','product-title'}).text.strip()
#         try:    
#             url = nameDiv.find('a')['href']
#             productID = url.split("/")[-1]
#             imageUrl = nameDiv.find('img',{'class','lazyload'})['data-src']
#             # imageUrl = i.find('div', {'class': 'grid_img wow zoomIn lazyload primary'})['data-bgset'].split(" ")[0]
#             imageUrl = imageUrl.replace('600.', '1000.')
#             try:
#                 oldPrice = i.find('span', class_='price actual-price').text.strip()
#                 oldPrice = functions.extractInt(oldPrice)
#                 newPrice = i.find('span', class_='price sale-price').text.strip()
#                 newPrice = functions.extractInt(newPrice)
#                 discount = math.ceil((oldPrice - newPrice) / oldPrice * 100)
#             except:
#                 newPrice = i.find('span', class_='price').text.strip()
#                 newPrice = functions.extractInt(newPrice)
#                 oldPrice = 0
#                 discount = 0
            
#             tmp_product['productID'] = productID
#             # tmp_product['name'] = name
#             tmp_product['name'] = functions.filterName(name,productID)
#             tmp_product['oldPrice'] = int(oldPrice)
#             tmp_product['newPrice'] = int(newPrice)
#             tmp_product['discount'] = int(discount)
#             tmp_product['url'] =  'https://deepakperwani.com' + url
#             tmp_product['imageUrl'] = imageUrl 
#             tmp_product['category'] =  category
#             tmp_product['subCategory'] = subCategory
#             tmp_product['subSubCategory'] = subSubCategory
#             # print(tmp_product)
#             products.append(tmp_product)    

#         except Exception as e:
#             with open("errors/error_Deepakperwani.json", "a") as f:
#                 error_log = {
#                     "datetime": datetime.datetime.now().isoformat(),
#                     "product_name": str(name),
#                     "exception_message": str(e),
#                     "page number": page
#                     }
#                 json.dump(error_log, f)
       
#     return products

import math
import json
import datetime
from bs4 import BeautifulSoup

def getProducts(soup, category, subCategory, subSubCategory, piece, pageURL):
    products = []
    
    try:
        mainContainer = soup.find('div', {'class': 'item-grid'})
        productsDiv = mainContainer.find_all('div', {'class': 'item-box'})
    except:
        return products

    for i in productsDiv:
        tmp_product = {
            'productID': '',
            'name': '',
            'oldPrice': '',
            'newPrice': '',
            'discount': '',
            'category': category,
            'subCategory': subCategory,
            'subSubCategory': subSubCategory,
            'url': '',
            'imageUrl': '',
            'views': 0,
            'likes': 0,
            'shares': 0,
            'favourites': 0,
            'availability' : 1,
            'list': 0,
            'keywords': [],
            'piece': piece
        }

        try:
            nameDiv = i.find('div', {'class': 'picture'})
            detailsDiv = i.find('div', {'class': 'details'})

            name = detailsDiv.find('h2', {'class': 'product-title'}).text.strip()
            url = nameDiv.find('a')['href']
            productID = i.find('div', {'class': 'product-item'})['data-productid']

            # Use main image (not hover)
            imageUrl = nameDiv.find('img', {'class': 'lazyload'})['data-src']
            imageUrl = imageUrl.replace('600.', '1000.')
            
            # Pricing logic
            try:
                oldPrice = detailsDiv.find('span', class_='price actual-price').text.strip()
                oldPrice = functions.extractInt(oldPrice)
                newPriceEl = detailsDiv.find('span', class_='price sale-price')
                if newPriceEl:
                    newPrice = functions.extractInt(newPriceEl.text.strip())
                else:
                    newPrice = oldPrice
                discount = math.ceil((oldPrice - newPrice) / oldPrice * 100) if oldPrice > newPrice else 0
            except:
                priceText = detailsDiv.find('span', class_='price').text.strip()
                newPrice = functions.extractInt(priceText)
                oldPrice = 0
                discount = 0

            tmp_product['productID'] = productID
            tmp_product['name'] = functions.filterName(name, productID)
            tmp_product['oldPrice'] = oldPrice
            tmp_product['newPrice'] = newPrice
            tmp_product['discount'] = discount
            tmp_product['url'] = 'https://www.deepakperwani.com' + url
            tmp_product['imageUrl'] = imageUrl if imageUrl.startswith('http') else 'https:' + imageUrl
            # tmp_product=getDeepakperwaniProductDetails(tmp_product)
            products.append(tmp_product)

        except Exception as e:
            with open("errors/error_DeepakPerwani.json", "a") as f:
                error_log = {
                    "datetime": datetime.datetime.now().isoformat(),
                    "product_name": str(name) if 'name' in locals() else 'N/A',
                    "exception_message": str(e),
                    "pageURL": pageURL
                }
                json.dump(error_log, f)
                f.write(",\n")  # append comma for valid JSON array format

    return products


def getDeepakperwaniProductDetails(product):
    try:
        html = functions.getRequest(product["url"], 'text')
        soup = BeautifulSoup(html, "html.parser")
        
        # with open("output_generate.html", "w", encoding="utf-8") as f:
        #      f.write(soup.prettify())
        
        availableSizes = []
        secondaryImages = []

        # -----------------------
        # Get Sizes
        # -----------------------
        try:
            sizeElements = soup.find('ul',{'class','option-list'}).find_all('li')
            for element in sizeElements:
                availableSizes.append(element.text.strip())
        except:
            availableSizes = []

        # Get Secondary Images
        # -----------------------
        mainContainer = soup.find('div',{'class','thumb-holder'})
        secondaryImagesDiv = mainContainer.find_all('img')
        # print(secondaryImagesDiv)
        for img in secondaryImagesDiv:
            # img = img.find('a')
            # print(img)
            if 'data-src' in img.attrs:
                    # print(img["data-src"])
                    img_url = img["data-src"]
                    img_url = img_url.replace('_200','_1000')
                    secondaryImages.append(img_url)
       
        # Remove duplicates and limit to 4
        secondaryImages = list(dict.fromkeys(secondaryImages))[:4]

        product['secondaryImages'] = secondaryImages
        product['sizes'] = availableSizes

    except Exception as e:
        print("An Error Occurred While Getting The Product Details")
        print(str(e))

        with open("errors/error_DeepakPerwani.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
            }
            json.dump(error_log, f)
            f.write(',')

    return product
