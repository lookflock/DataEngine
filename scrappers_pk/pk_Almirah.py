import json
from bs4 import BeautifulSoup
import datetime
import math
import os
import random
import functions

import datetime
import json
import re
import functions  # Assuming you have a module named functions.py


def getProducts(soup, category, subCategory, subSubCategory, piece, pageURL):
    products = []
    container = soup.find('ul', id='product-grid')
    if not container:
        print(f"ERROR: No products container found using selector 'ul#product-grid'")
        with open("errors/error_Almirah.json", "a") as f:
                json.dump({
                    "datetime": datetime.datetime.now().isoformat(),
                    "error": "ERROR: No products container found using selector 'ul#product-grid'",
                }, f)
                f.write("\n")
        return products

    items = container.find_all('li', class_='grid__item')
    print(f"Found {len(items)} items in grid")

    for li in items:
        try:
            link = li.find('a', class_='custom-product-link-wrap')
            url = link['href']
            title_img = link.find('img')
            name = title_img['alt'].strip()
            productID = name.split('-')[-1].strip()

            # Price extraction: requires looking for price container
            price_el = li.select_one('.price-item--regular')
            new_el   = li.select_one('.price-item--sold .price--highlight') or price_el

            oldPrice = re.sub(r'[^\d]', '', price_el.text) if price_el else '0'
            newPrice = re.sub(r'[^\d]', '', new_el.text) if new_el else oldPrice
            discount = math.ceil(int(100 * (int(oldPrice) - int(newPrice)) / int(oldPrice))) if int(oldPrice) else 0
            # discount = math.ceil((oldPrice - newPrice) / oldPrice * 100)

            img_url = title_img['src'].replace('width=533', 'width=1000') if title_img else ''

            tmp_product={
                'productID': productID,
                'name': functions.filterName(name, productID),
                'oldPrice': int(oldPrice),
                'newPrice': int(newPrice),
                'discount': discount,
                'url': 'https://www.almirah.com.pk' + url,
                'imageUrl': img_url,
                'category': category,
                'subCategory': subCategory,
                'subSubCategory': subSubCategory,
                'pageUrl': pageURL,
                'piece': piece,
                'views': 0, 'likes': 0, 'shares': 0,
                'favourites': 0, 'list': 0, 'keywords': []
            }
            tmp_product=getAlmirahProductDetails(tmp_product)
            products.append(tmp_product) 
            # products.append({
            #     'productID': productID,
            #     'name': functions.filterName(name, productID),
            #     'oldPrice': int(oldPrice),
            #     'newPrice': int(newPrice),
            #     'discount': discount,
            #     'url': 'https://www.almirah.com.pk' + url,
            #     'imageUrl': img_url,
            #     'category': category,
            #     'subCategory': subCategory,
            #     'subSubCategory': subSubCategory,
            #     'pageUrl': pageURL,
            #     'piece': piece,
            #     'views': 0, 'likes': 0, 'shares': 0,
            #     'favourites': 0, 'list': 0, 'keywords': []
            # })
        except Exception as e:
            with open("errors/error_Almirah.json", "a") as f:
                json.dump({
                    "datetime": datetime.datetime.now().isoformat(),
                    "error": str(e),
                    "item_html": str(li)[:200]
                }, f)
                f.write("\n")
    return products

def getAlmirahProductDetails(product):
    try:
        html = functions.getRequest(product["url"], 'text')
        soup = BeautifulSoup(html, "html.parser")
        
        with open("output_generate.html", "w", encoding="utf-8") as f:
             f.write(soup.prettify())
        # html = functions.getRequest(product["url"], 'text')
        # with open("debug_output.html", "w", encoding="utf-8") as f:
        #     f.write(html)

        # soup = BeautifulSoup(html, "html.parser")

        availableSizes = []
        secondaryImages = []

        # -----------------------
        # Get Sizes
        # -----------------------
        size_inputs = soup.select('fieldset.size input[type="radio"][value]')
        availableSizes = [input_tag['value'] for input_tag in size_inputs]
        # -----------------------
        # Get Secondary Images
        # -----------------------
        media_items = soup.select('div.product__media img, div.swiper-wrapper img, div.product-gallery img')
        for img in media_items:
            img_url = img.get('data-master') or img.get('data-src') or img.get('src')
            if img_url:
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                elif img_url.startswith('/'):
                    img_url = 'https://www.almirah.com.pk' + img_url
                if img_url not in secondaryImages:
                    secondaryImages.append(img_url)

        # Remove duplicates and limit to 4
        secondaryImages = list(dict.fromkeys(secondaryImages))[:4]
        product['secondaryImages'] = secondaryImages
        product['sizes'] = availableSizes

    except Exception as e:
        print("An Error Occurred While Getting The Product Details")
        print(str(e))

        with open("errors/error_Almirah.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
            }
            json.dump(error_log, f)
            f.write(',')

    return product

# def getAlmirahProductDetails(product):  
#     try:
#         html = functions.getRequest(product["url"], 'text')
#         soup = BeautifulSoup(html, "html.parser")
        
#         with open("output.html", "w", encoding="utf-8") as f:
#              f.write(soup.prettify())
        
#         availableSizes = []
#         availableColors = []
#         secondaryImages = []
#         # Extracting available sizes,colors and description
#         varientElements = soup.find_all('div', {'class': 'variant-wrapper'}) # 0 is size 1 is color 2 is style (not used)
#         sizeElements = varientElements[0].find_all('div', {'class': 'variant-input'})
#         for element in sizeElements:
#             availableSizes.append(element.find('label').text.strip())

#         colorElements = varientElements[1].find_all('div', {'class': 'variant-input'})
#         for element in colorElements:
#             availableColors.append(element.find('label').text.strip())    

#         productDescription= str(soup.find('div', {'class': 'product-single__description rte'}))
        
#         # to include the table
#         # productDescription += str(soup.find('div', {'class': 'collapsible-content__inner rte'}))

#         mainContainer = soup.find('div',{'class':'product__photos'})
#         secondaryImagesDiv = mainContainer.find_all('div',{'class':'product__thumb-item'})
        
#         for img in secondaryImagesDiv:
#             img = img.find('img')
#             # print(img)
#             if 'data-src' in img.attrs:
#                     # print(img["data-src"])
#                     img_url = img["data-src"].replace('{width}', '1000')
#                     secondaryImages.append('https:' + img_url)

#         secondaryImages= list(set(secondaryImages))
#         # secondaryImages = [image for image in secondaryImages if image != product['imageUrl']]
#         availableColors= list(set(availableColors))

#         productDescription = functions.filterDescription(productDescription)
#         availableSizes = functions.sortSizes('Almirah',availableSizes)
#         availableColors = functions.sortColors('Almirah',availableColors)


#         print(product["url"],productDescription,availableSizes,availableColors,secondaryImages[:4])

#         product['Description'] = productDescription
#         product['Sizes'] = availableSizes
#         product['Colors'] = availableColors
#         product['secondaryImages'] = secondaryImages[:4]
#         product['sizeColors'] = functions.crossJoin(availableSizes,availableColors)

#     except Exception as e:
#         print ("An Error Occured While Getting The Product Details")
#         print(str(e))
#         with open("errors/error_Almirah.json", "a") as f:
#             error_log = {
#                 "datetime": datetime.datetime.now().isoformat(),
#                 "product_name": str(product['name']),
#                 "exception_message": str(e)
#                 }
#             json.dump(error_log, f)  
#     return product