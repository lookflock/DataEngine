import json
from bs4 import BeautifulSoup
import math
import os
import datetime
import re
import config
import functions
import random
import time
from urllib.parse import urlparse, urlunparse
import requests

supplier='Almirah'

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
            name.replace("\u00a02", ' ')
            productID = name.split(' - ')[1] 

            # Price extraction: requires looking for price container
            price_el = li.select_one('.price-item--regular')
            new_el   = li.select_one('.price-item--sold .price--highlight') or price_el

            oldPrice = re.sub(r'[^\d]', '', price_el.text) if price_el else '0'
            newPrice = re.sub(r'[^\d]', '', new_el.text) if new_el else oldPrice
            discount = math.ceil(int(100 * (int(oldPrice) - int(newPrice)) / int(oldPrice))) if int(oldPrice) else 0
            # discount = math.ceil((oldPrice - newPrice) / oldPrice * 100)

            img_url = title_img['src'].replace('width=533', 'width=1000') if title_img else ''

            tmp_product={
                'supplier': supplier,
                'id': productID,
                'name': functions.filterName(name, productID),
                'oldPrice': int(oldPrice),
                'newPrice': int(newPrice),
                'discount': discount,
                'category': category,
                'subCategory': subCategory,
                'subSubCategory': subSubCategory,
                'url': 'https://www.almirah.com.pk' + url,
                'imageUrl': 'https:' + normalize_image_url(img_url) ,
                'page':pageURL,
                'views': 0, ''
                'likes': 0,
                'shares': 0,
                'favourites': 0,
                'status' : 1,
                'list': 0,
                'keywords': [],
                'piece': piece,
                'valid':1
            }
            # tmp_product=getAlmirahProductDetails(tmp_product)
            products.append(tmp_product) 
        except Exception as e:
            print("ERRORRR", json.dumps(tmp_product, indent=4, ensure_ascii=False))      
            error_log = {
                "datetime": datetime.now().isoformat(),
                "product_id": productID,
                "product_name": str(name),
                "exception_message": str(e),
                "pageURL number": pageURL
            }        
            error_filename = functions.get_latest_error_file("Almirah")
            if not error_filename:
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
                error_filename = f"errors/error_AhmadRaza_{timestamp}.json"

                # Save updated logs
            with open(error_filename, "w", encoding="utf-8") as f:
                json.dump(error_log, f, indent=2, ensure_ascii=False)
    return products

def normalize_image_url(url):
    parsed = urlparse(url)
    path = parsed.path
    path = re.sub(r'(_\d+x)?(\.\w+)$', r'\2', path)  # remove _360x, _720x, etc.
    return urlunparse(parsed._replace(path=path, query=""))

def getAlmirahProductDetails(product):
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
        size_inputs = soup.select('fieldset.size input[type="radio"][value]')
        availableSizes = [input_tag['value'] for input_tag in size_inputs]
        availableSizes = functions.sortSizes('Almirah', availableSizes)
        # -----------------------
        # Get Secondary Images
        # -----------------------
        media_items = soup.select('div.product__media img, div.swiper-wrapper img, div.product-gallery img')
        main_image = product.get("imageUrl")

        for img in media_items:
            img_url = img.get('data-master') or img.get('data-src') or img.get('src')
            if img_url:
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                elif img_url.startswith('/'):
                    img_url = 'https://www.almirah.com.pk' + img_url
                
                parsed_url = urlparse(img_url)
                cleaned_url = urlunparse(parsed_url._replace(query=""))


                # Skip if this is the same as the main image
                if main_image:
                    normalized_main = normalize_image_url(main_image)
                    normalized_secondary = normalize_image_url(cleaned_url)

                    if normalized_main == normalized_secondary:
                        continue

                # Verify and add
                try:
                    response = requests.head(cleaned_url, timeout=5)
                    if response.status_code == 200:
                        secondaryImages.append(cleaned_url)
                    else:
                        print(f"[image check] Invalid image (status {response.status_code}): {cleaned_url}")
                except Exception as e:
                    print(f"[image check] Failed to verify image: {cleaned_url} — {e}")

        # Finalize
        secondaryImages = list(set(secondaryImages))
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