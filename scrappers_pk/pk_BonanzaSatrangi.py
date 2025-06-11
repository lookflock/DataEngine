import json
from bs4 import BeautifulSoup
import math
import os
import datetime
import re
import config
import functions
import random

def getProducts(soup, category, subCategory, subSubCategory, piece, pageURL):
    
    products = []
    mainContainer = soup.find('div', {'class':'sr4-products'})
    try:
        productsDiv = mainContainer.find_all('div', {'class':'sr4-product'})
    except:
        return products

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
                'pageUrl': pageURL,
                'views' : 0,
                'likes' : 0,
                'shares' : 0,
                'favourites' : 0,
                'list' : 0,
                'keywords': [],
                'piece': ''
            }
        with open("output3.html", "w", encoding="utf-8") as f:
            f.write(i.prettify())

        name = i.find('h3',{'class':'sr4-product-title'}).text.strip()
        try:
            url = i.find('h3',{'class':'sr4-product-title'}).find('a')['href']
            Product_id = re.findall( r'\((.*?)\)', name)[0]
            imageUrl = i.find('img', {'class':'sr4-product-main-img lazyloadsr4'})['data-src'].split('?')[0].split('//')[1]

            # imageUrl = imageUrl.replace('{width}', '1000')
            try:
                price = i.find('div',{'class':'sr4-product-price'})
                oldPrice = price.find_all('span',{'class':'money'})[0].text.strip()
                oldPrice = functions.extractInt(oldPrice)
                newPrice = price.find_all('span',{'class':'money'})[1].text.strip()
                newPrice =functions.extractInt(newPrice)
                discount = math.ceil((oldPrice - newPrice) / oldPrice * 100)
            except:
                newPrice = i.find('div',{'class':'details'}).find('span', class_='product-price__price').text.strip()
                newPrice = functions.extractInt(newPrice)
                oldPrice = 0
                discount = 0
            
            
            tmp_product['productID'] = Product_id
            tmp_product['name'] = functions.filterName(name,Product_id)
            tmp_product['oldPrice'] = oldPrice
            tmp_product['newPrice'] = newPrice
            tmp_product['discount'] = discount
            tmp_product['url'] = 'https://bonanzasatrangi.com'+  url
            tmp_product['imageUrl'] = 'https:' + imageUrl 
            tmp_product['category'] =  category
            tmp_product['subCategory'] = subCategory
            tmp_product['subSubCategory'] = subSubCategory
            tmp_product['piece'] = piece
            tmp_product=getBonanzaSatrangiProductDetails(tmp_product)
            products.append(tmp_product) 

        except Exception as e:
                with open("errors/error_BonanzaSatrangi.json", "a") as f:
                    error_log = {
                    "datetime": datetime.datetime.now().isoformat(),
                    "product_name": str(name),
                    "exception_message": str(e),
                    "pageURL number": pageURL
                    }
                    json.dump(error_log, f)        

         

    return products

def getBonanzaSatrangiProductDetails(product):
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
        availableSizes = [
            el.get('data-value') 
            for el in soup.select('div[data-swatch-option][data-id="0"] div.sr4-swatch__item')
        ]
        # -----------------------
        # Get Secondary Images
        # -----------------------
        media_items = soup.select(".sr4-product__media-item img[data-master]")

        for img_tag in media_items:
            img_url = img_tag.get("data-master")
            if img_url:
                full_url = "https:" + img_url if img_url.startswith("//") else img_url
                secondaryImages.append(full_url)


        # Remove duplicates and limit to 4
        secondaryImages = list(dict.fromkeys(secondaryImages))[:4]
        product['secondaryImages'] = secondaryImages
        product['sizes'] = availableSizes

    except Exception as e:
        print("An Error Occurred While Getting The Product Details")
        print(str(e))

        with open("errors/error_BonanzaSatrangi.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
            }
            json.dump(error_log, f)
            f.write(',')

    return product