import json
from bs4 import BeautifulSoup
import math
import os
import datetime
import re
import functions
import requests
import random

def getProducts(soup, category, subCategory, subSubCategory,piece, pageURL):
    products = []
    # Changed main container selector to match the HTML structure
    productsGrid = soup.find('div', {'class': 'products-grid column-5 disable-srollbar'})
    
    if not productsGrid:
        return products
        
    try:
        # Updated selector to match the product div structure
        productsDiv = productsGrid.find_all('div', {'class': 'product-item'})
    except Exception as e:
        print(f"Error finding products: {str(e)}")
        return products

    for product in productsDiv:
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
            'list': 0,
            'keywords': [],
            'piece': ''
        }

        try:
            # Extract data from JSON attribute
            json_data = json.loads(product.get('data-json-product', '{}'))
            variants = json_data.get('variants', [{}])
            
            # Product ID from data attribute
            tmp_product['productID'] = product.get('data-product-id', '')
            
            # Name extraction
            name_link = product.find('a', {'class': 'card-title'})
            tmp_product['name'] = name_link.text.strip()
            tmp_product['url'] = 'https://www.chinyere.pk' + name_link['href']
            
            # Image handling
            img = product.find('img', {'class': 'motion-reduce lazyload'})
            if img:
                image_url = img.get('data-srcset', '').split(',')[0].strip()
                image_url = image_url.split('?')[0]  # Remove query parameters
                tmp_product['imageUrl'] = f'https:{image_url}'

            # Price handling
            price_div = product.find('div', {'class': 'card-price'})
            if price_div:
                # Regular price
                regular_price = price_div.find('dd', {'class': 'price__compare'})
                if regular_price:
                    tmp_product['oldPrice'] = functions.extractInt(regular_price.text)
                
                # Sale price
                sale_price = price_div.find('dd', {'class': 'price__last'})
                tmp_product['newPrice'] = functions.extractInt(sale_price.text) if sale_price else tmp_product['oldPrice']
                
                # Calculate discount
                if tmp_product['oldPrice'] and tmp_product['newPrice']:
                    discount = ((tmp_product['oldPrice'] - tmp_product['newPrice']) / tmp_product['oldPrice']) * 100
                    tmp_product['discount'] = round(discount, 0)
                else:
                    tmp_product['discount'] = 0

            # Extract additional details from card-summary
            summary = product.find('div', {'class': 'card-summary'})
            if summary:
                details = summary.text.strip().split('Color:')
                if len(details) > 1:
                    color_fabric = details[1].split('Fabric:')
                    tmp_product['keywords'] = [c.strip() for c in color_fabric[0].split(',')]

            tmp_product['piece'] = piece
            products.append(tmp_product)

        except Exception as e:
                with open("errors/error_Chinyere.json", "a") as f:
                    error_log = {
                    "datetime": datetime.datetime.now().isoformat(),
                    "product_name": str(name),
                    "exception_message": str(e),
                    "pageURL": pageURL
                    }
                    json.dump(error_log, f)

    return products


def getChinyereProductDetails(product):
    try:
        html = functions.getRequest(product['url'], 'text')
        soup = BeautifulSoup(html, "html.parser")
        
        with open("output.html", "w", encoding="utf-8") as f:
             f.write(soup.prettify())

        availableSizes = []
        availableColors = []
        secondaryImages = []
        sizeElement = soup.find_all('input',{'name':'Size'})
        for size in sizeElement:
            availableSizes.append(size['value'])

        colorElement = soup.find_all('input',{'name': 'Color'})
        for color in colorElement:
            availableColors.append(color['value'])

        productDescription= str(soup.find('div', {'class': 'tab-popup-content'}))

        mainContainer = soup.find('div',{'class':'productView-thumbnail-wrapper'})
        secondaryImagesDiv = mainContainer.find_all('div',{'class':'productView-thumbnail'})
        
        for img in secondaryImagesDiv:
            img = img.find('img')
            if img is not None:
                if 'src' in img.attrs:
                    img_url = img["src"].replace('_compact','')
                    secondaryImages.append('https:' + img_url)

        secondaryImages= list(set(secondaryImages))
        # secondaryImages = [image for image in secondaryImages if image != product['imageUrl']]
                
        productDescription = functions.filterDescription(productDescription)
        availableSizes = functions.sortSizes('Chinyere',availableSizes)
        availableColors = functions.sortColors('Chinyere',availableColors)

        
        print(product["url"],productDescription,availableSizes,availableColors,secondaryImages[:4])


        product['Description'] = productDescription
        product['Sizes'] = availableSizes
        product['Colors'] = availableColors
        product['secondaryImages'] = secondaryImages[:4]
        product['sizeColors'] = functions.crossJoin(availableSizes,availableColors)


    except Exception as e:
        print ("An Error Occured While Getting The Product Details")
        print(str(e))
        with open("errors/error_Chinyere.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
                }
            json.dump(error_log, f)  
    return product        