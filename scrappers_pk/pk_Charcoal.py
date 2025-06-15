import json
from bs4 import BeautifulSoup
import datetime
import math
import os
import random
import functions


def getProducts(soup, category, subCategory, subSubCategory,piece, pageURL):
    products = []
    with open("output.html", "w", encoding="utf-8") as f:
           f.write(soup.prettify())
    
    mainContainer = soup.find('product-list', {'class': 'product-list'})
    productsDiv = mainContainer.find_all('product-card',{'class': 'product-card'})
    
    for i in productsDiv:
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
                'views' : 0,
                'likes' : 0,
                'shares' : 0,
                'favourites' : 0,
                'availability' : 1,
                'list' : 0,
                'keywords': [],
                'piece': ''
            }
        
        
        nameDiv = i.find('img', {'class': 'product-card__image'})
        name = nameDiv['alt']
        try:    
            
            url = i.find('span',{'class':'product-card__title'}).find('a')['href']
            productID = url.split('/')[-1]
            imageUrl = nameDiv['src']
            try:
                oldPrice = i.find('compare-at-price', class_='text-subdued line-through').text.strip()
                oldPrice = functions.extractInt(oldPrice)
                newPrice = i.find('sale-price', class_='text-on-sale').text.strip()
                newPrice = functions.extractInt(newPrice)
                discount = math.ceil((oldPrice - newPrice) / oldPrice * 100)
            except:
                newPrice = i.find('sale-price', class_='text-subdued').text.strip()
                newPrice = functions.extractInt(newPrice)
                oldPrice = 0
                discount = 0
            
            tmp_product['productID'] = productID
            # tmp_product['name'] = name
            tmp_product['name'] = functions.filterName(name,productID)
            tmp_product['oldPrice'] = int(oldPrice)
            tmp_product['newPrice'] = int(newPrice)
            tmp_product['discount'] = int(discount)
            tmp_product['url'] =  'https://charcoal.com.pk' + url
            tmp_product['imageUrl'] = 'https:' + imageUrl 
            tmp_product['category'] =  category
            tmp_product['subCategory'] = subCategory
            tmp_product['subSubCategory'] = subSubCategory
            tmp_product['piece'] = piece
            tmp_product=getCharcoalProductDetails(tmp_product)
            products.append(tmp_product)    

        except Exception as e:
            with open("errors/error_Almirah.json", "a") as f:
                error_log = {
                    "datetime": datetime.datetime.now().isoformat(),
                    "product_name": str(name),
                    "exception_message": str(e),
                    "pageURL": pageURL
                    }
                json.dump(error_log, f)
       
    return products


def getCharcoalProductDetails(product):
    try:
        html = functions.getRequest(product["url"], 'text')
        soup = BeautifulSoup(html, "html.parser")
        
        with open("output_generate.html", "w", encoding="utf-8") as f:
             f.write(soup.prettify())
        
        availableSizes = []
        secondaryImages = []

        # -----------------------
        # Get Sizes
        # -----------------------
        sizeElements = soup.find('fieldset',{'class','variant-picker__option'}).find_all('label',{'class','block-swatch'})
        for element in sizeElements:
            availableSizes.append(element.text.strip())

        # Get Secondary Images
        # -----------------------
        for img in soup.select('div.product-gallery__media img[src]'):
            img_url = img['src']
            if img_url.startswith('//'):
                img_url = 'https:' + img_url
            # Remove width parameter and keep base URL
            clean_url = img_url.split('?')[0]
            if clean_url not in secondaryImages:
                secondaryImages.append(clean_url)
       
        # Remove duplicates and limit to 4
        secondaryImages = list(dict.fromkeys(secondaryImages))[:4]
        product['secondaryImages'] = secondaryImages
        product['sizes'] = availableSizes

    except Exception as e:
        print("An Error Occurred While Getting The Product Details")
        print(str(e))

        with open("errors/error_Charcoal.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
            }
            json.dump(error_log, f)
            f.write(',')

    return product

