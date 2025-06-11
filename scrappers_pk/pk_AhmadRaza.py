import json
from bs4 import BeautifulSoup
import math
import os
import datetime
import re
import config
import functions
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time


def getProducts(soup, category, subCategory, subSubCategory, piece, pageURL):
    
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
                'keywords': [],
                'piece': ''
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
            tmp_product['piece'] = piece
            # tmp_product=getAhmadRazaProductDetails(tmp_product)
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
        
        availableSizes = []
        secondaryImages = []

        # Get sizes from input[type="radio"] inside swatch
        swatch_div = soup.find('div', class_='swatch')
        if swatch_div:
            size_inputs = swatch_div.find_all('input', {'type': 'radio', 'name': 'option-0'})
            for input_tag in size_inputs:
                size_value = input_tag.get('value', '').strip()
                if size_value:  # Avoid empty values
                    availableSizes.append(size_value.upper())

        # Get secondary images
        image_wrappers = soup.select('div.product-photo-container.slider-for div.thumb img')
        for img in image_wrappers:
            if 'src' in img.attrs:
                img_url = img['src']
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                elif img_url.startswith('/'):
                    img_url = 'https://www.ahmadraza.com.pk' + img_url
                secondaryImages.append(img_url)

        # Remove duplicates and limit to 4
        secondaryImages = list(set(secondaryImages))[:4]
        product['secondaryImages'] = secondaryImages
        product['sizes'] = availableSizes

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



# def getAhmadRazaProductDetails(product):
#     try:
#         html = functions.getRequest(product["url"], 'text')
#         soup = BeautifulSoup(html, "html.parser")

#         availableSizes = product.get("Sizes", [])
#         availableColors = []
#         secondaryImages = []
#         productDescription = ""
        
#         productDescription = str(soup.find('div', {'class': 'tab-popup-content'}).find('p'))

#         for img in soup.find('div', {'class': 'productView-thumbnail-wrapper'}).find_all('img'):
#             # img_tag = img.find('img')
#             if  'src' in img.attrs:
#                 # img_url = img['src'].replace('60x', '1000x')
#                 secondaryImages.append('https:' + img['src'])

#         secondaryImages = list(set(secondaryImages))
#         # productDescription = functions.filterDescription(productDescription)
#         availableColors = functions.sortColors("AhmedRaza", availableColors)

#         product['Description'] = productDescription
#         product['Colors'] = availableColors
#         product['secondaryImages'] = secondaryImages[:4]
#         product['sizeColors'] = functions.crossJoin(availableSizes, availableColors)

#         # print(productDescription)
#     except Exception as e:
#         print("An Error Occurred While Getting The Product Details")
#         print(str(e))
        
#         with open("errors/error_AhmadRaza.json", "a") as f:
#             error_log = {
#                 "datetime": datetime.datetime.now().isoformat(),
#                 "product_name": str(product['name']),
#                 "exception_message": str(e)
#             }
#             json.dump(error_log, f)
#             f.write(',')
#     return product

# def get_dynamic_ahmadraza_details(product_url):
#     options = Options()
#     options.add_argument("--headless")  # Run in background
#     options.add_argument("--disable-gpu")
#     driver = webdriver.Chrome(options=options)

#     try:
#         driver.get(product_url)
#         time.sleep(3)  # Wait for JS to load content

#         soup = BeautifulSoup(driver.page_source, "html.parser")

#         # Extract description from meta tag
#         meta_desc = soup.find('meta', attrs={'property': 'og:description'})
#         description = meta_desc['content'] if meta_desc else ""

#         # Extract secondary images from og:image tags
#         image_tags = soup.find_all('meta', attrs={'property': 'og:image'})
#         secondary_images = []
#         for tag in image_tags:
#             img_url = tag.get('content', '')
#             if img_url and "cdn.shopify" in img_url:
#                 img_url = img_url.replace("_grande", "")
#                 secondary_images.append(img_url)

#         driver.quit()
#         return {
#             "Description": description,
#             "secondaryImages": list(set(secondary_images))
#         }

#     except Exception as e:
#         driver.quit()
#         print("Error loading dynamic content:", e)
#         return {
#             "Description": "",
#             "secondaryImages": []
#         }
