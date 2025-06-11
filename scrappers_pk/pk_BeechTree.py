import json
from bs4 import BeautifulSoup
import math
import os
import datetime
import config
import functions
import random

def getProducts(soup, category, subCategory, subSubCategory, piece, pageURL):
    products = []
    mainContainer = soup.find('ul', {'id': 'product-grid'})
    if mainContainer:
        productsDiv = mainContainer.find_all('li',{'class': 'grid__item'})
    
        with open("output.html", "w", encoding="utf-8") as f:
             f.write(soup.prettify())
          
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
            try:
                productID = i.find('div',{'class':'card'})['data-product-id']
            except:
                print('Product ID not found')
                continue;
            try:
                name = i.find('h3').text.strip()
                url = i.find('div',{'class':'card__inner'}).find('a')['href']
                imageUrl = i.find('img',{'class','motion-reduce'})['src']
                try:
                    oldPrice = i.find('span', {'class': 'price-item price-item--regular'}).text.strip()
                    newPrice = i.find('span', {'class': 'price-item price-item--sale'}).text.strip()            
                    discount =  i.find('div',{'class':'ctm-sale-label'}).text.strip()
                except:
                    newPrice = i.find('span', {'class': 'price-item price-item--regular'}).text.strip() 
                    oldPrice =0
                    discount =0
                
                tmp_product['productID'] = productID
                tmp_product['name'] = functions.filterName(name,productID)
                tmp_product['oldPrice'] = functions.extractInt(oldPrice)
                tmp_product['newPrice'] = functions.extractInt(newPrice)
                tmp_product['discount'] = functions.extractInt(discount) 
                tmp_product['url'] =  'https://beechtree.pk' + url
                tmp_product['imageUrl'] = 'https:' + imageUrl 
                tmp_product['category'] =  category
                tmp_product['subCategory'] = subCategory
                tmp_product['subSubCategory'] = subSubCategory
                tmp_product['piece'] = piece
                tmp_product=getBeechTreeProductDetails(tmp_product)
                products.append(tmp_product) 
            except Exception as e:
                with open("errors/error_BeechTree.json", "a") as f:
                    error_log = {
                    "datetime": datetime.datetime.now().isoformat(),
                    "product_name": str(name),
                    "exception_message": str(e),
                    "pageURL number": pageURL
                    }
                    json.dump(error_log, f)
    return products



def getBeechTreeProductDetails(product):
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
        availableSizes = [el.get('value') for el in soup.select('div.new_options_container input[type="radio"][name^="Size-1"]')]

        # -----------------------
        # Get Secondary Images
        # -----------------------

        for a_tag in soup.select('div.swiper-slide a[href]'):
            img_url = a_tag['href']
            if img_url.startswith('//'):
                img_url = 'https:' + img_url
            secondaryImages.append(img_url)
   

        # Remove duplicates and limit to 4
        secondaryImages = list(dict.fromkeys(secondaryImages))[:4]
        product['secondaryImages'] = secondaryImages
        product['sizes'] = availableSizes

    except Exception as e:
        print("An Error Occurred While Getting The Product Details")
        print(str(e))

        with open("errors/error_BeechTree.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
            }
            json.dump(error_log, f)
            f.write(',')

    return product