import json
from bs4 import BeautifulSoup
import math
import os
import datetime
import re
import config
import functions
import random

def getProducts(soup, category, subCategory, subSubCategory, pageURL):
    
    products = []
    mainContainer = soup.find('div', {'class':'product-collection'})
    productsDiv = mainContainer.find_all('div', {'class':'grid-item'})
    
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
                'page': pageURL,
                'views' : 0,
                'likes' : 0,
                'shares' : 0,
                'favourites' : 0,
                'list' : 0,
                'keywords': []
            }
        name = product.find('a',{'class','product-title'}).text.strip()
        try:
            productItem = product.find('div', {'class','product-item'})
            productJson =  json.loads(productItem['data-json-product'])
            productID = productJson['id']
            imageDiv = product.find('a',{'class':'product-grid-image'})
            url = imageDiv['href']
            imageUrl = imageDiv.find('img', {'class','images-one'})['data-srcset'].split(' ')[0]
            imageUrl = imageUrl.replace('165x', '900x')
            priceBox = product.find('div', {'class':'price-box'})
            # Completed till here
            try:
                oldPrice = priceBox.find('span', {'class':'old-price'}).text.strip()
                oldPrice = functions.extractInt(oldPrice)
                newPrice = priceBox.find('span', {'class':'special-price'}).text.strip()
                newPrice = functions.extractInt(newPrice)
                discount = math.ceil((oldPrice - newPrice) / oldPrice * 100)
            except:
                newPrice = product.find('div', {'class':'price-regular'}).text.strip()
                newPrice = functions.extractInt(newPrice)
                oldPrice = 0
                discount = 0

            tmp_product['productID'] = productID
            tmp_product['name'] = name
            tmp_product['oldPrice'] = int(oldPrice)
            tmp_product['newPrice'] = int(newPrice)
            tmp_product['discount'] = int(discount)
            tmp_product['url'] = 'https://www.ahmadraza.com.pk'+  url
            tmp_product['imageUrl'] = 'https:' + imageUrl 
            tmp_product['category'] =  category
            tmp_product['subCategory'] = subCategory
            tmp_product['subSubCategory'] = subSubCategory

            products.append(tmp_product) 

        except Exception as e:
                # with open(f"./AhmadRaza/{product['productID']}.html", "w", encoding="utf-8") as file:
                #     file.write(product.prettify())
                # print(product.prettify())
                print("ERRORRR", json.dumps(tmp_product, indent=4 ,ensure_ascii=False))
                with open("errors/error_AhmadRaza.json", "a") as f:
                    error_log = {
                    "datetime": datetime.datetime.now().isoformat(),
                    "product_name": str(name),
                    "exception_message": str(e),
                    "pageURL number": pageURL
                    }
                    json.dump(error_log, f)        
                return

         

    return products

def getAhmadRazaProductDetails(product):
    try:
        html = functions.getRequest(product["url"], 'text')
        soup = BeautifulSoup(html, "html.parser")

        availableSizes = product.get("Sizes", [])
        availableColors = []
        secondaryImages = []
        productDescription = ""
        
        productDescription = str(soup.find('div', {'class': 'tab-popup-content'}).find('p'))

        for img in soup.find('div', {'class': 'productView-thumbnail-wrapper'}).find_all('img'):
            # img_tag = img.find('img')
            if  'src' in img.attrs:
                # img_url = img['src'].replace('60x', '1000x')
                secondaryImages.append('https:' + img['src'])

        secondaryImages = list(set(secondaryImages))
        # productDescription = functions.filterDescription(productDescription)
        availableColors = functions.sortColors("AhmedRaza", availableColors)

        product['Description'] = productDescription
        product['Colors'] = availableColors
        product['secondaryImages'] = secondaryImages[:4]
        product['sizeColors'] = functions.crossJoin(availableSizes, availableColors)

        # print(productDescription)
    except Exception as e:
        print("An Error Occurred While Getting The Product Details")
        print(str(e))
        
        with open("errors/error_AhmadRaza.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
            }
            json.dump(error_log, f)
            f.write(',')
    return product
