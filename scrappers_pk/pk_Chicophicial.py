import json
from bs4 import BeautifulSoup
import datetime
import math
import os
import random
import functions

def getProducts(soup, category, subCategory, subSubCategory, piece, pageURL):
    products = []

    mainContainer = soup.find('div', class_='collection')
    if not mainContainer:
        return products  # If container not found, return empty list

    productsDiv = mainContainer.find_all('div', class_='gitem fl')

    # Save parsed HTML to inspect structure if needed
    with open("output.html", "w", encoding="utf-8") as f:
        f.write(soup.prettify())

    for i in productsDiv:
        tmp_product = {
            'productID': '',
            'name': '',
            'oldPrice': 0,
            'newPrice': 0,
            'discount': 0,
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
            nameDiv = i.find('a', class_='grid_lnk')
            if not nameDiv:
                continue

            name = nameDiv.get('aria-label', '').strip()
            url = nameDiv.get('href', '').strip()

            # Product ID
            pr_review = i.find('div', class_='pr_review')
            productID = pr_review.find('span')['data-id'] if pr_review else ''

            # Image URL
            primary_img_div = nameDiv.find('div', class_='grid_img wow zoomIn lazyload primary')
            imageUrl = ''
            if primary_img_div and 'data-bgset' in primary_img_div.attrs:
                imageUrl = primary_img_div['data-bgset'].split(' ')[0].replace('_150x', '_1000x')
                if not imageUrl.startswith('https:'):
                    imageUrl = 'https:' + imageUrl

            # Prices
            # USD_convert = functions.PKR_rate_USD()
            try:
                oldPriceText = i.find('s', class_='pr_price')
                newPriceText = i.find('span', class_='pr_price sale')

                if oldPriceText and newPriceText:
                    oldPrice = functions.extractInt(oldPriceText.text.strip()) 
                    newPrice = functions.extractInt(newPriceText.text.strip()) 
                else:
                    newPrice = functions.extractInt(i.find('span', class_='pr_price').text.strip()) 
                    oldPrice = 0
                discount = math.ceil((oldPrice - newPrice) / oldPrice * 100) if oldPrice else 0
            except:
                newPrice = functions.extractInt(i.find('span', class_='pr_price').text.strip())
                oldPrice = 0
                discount = 0

            # Fill product data
            tmp_product['productID'] = productID
            tmp_product['name'] = functions.filterName(name, productID)
            tmp_product['oldPrice'] = int(oldPrice)
            tmp_product['newPrice'] = int(newPrice)
            tmp_product['discount'] = int(discount)
            tmp_product['url'] = 'https://chicophicial.com' + url
            tmp_product['imageUrl'] = imageUrl
            tmp_product=getChicophicialProductDetails(tmp_product)
            products.append(tmp_product)

        except Exception as e:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": name if 'name' in locals() else '',
                "exception_message": str(e),
                "pageURL": pageURL
            }
            with open("errors/error_Chichophicial.json", "a", encoding="utf-8") as f:
                json.dump(error_log, f)
                f.write("\n")

    return products


def getChicophicialProductDetails(product):
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
        sizeElements = soup.find('div',{'class','product-form'}).find_all('div',{'class','swatch-element'})
        for element in sizeElements:
            availableSizes.append(element['data-value'])

        # Get Secondary Images
        # -----------------------
        mainContainer = soup.find('div',{'class','swiper-wrapper'})
        secondaryImagesDiv = mainContainer.find_all('a',{'class','swiper-slide'})
        
        for img in secondaryImagesDiv:
            # img = img.find('a')
            # print(img)
            if 'href' in img.attrs:
                    # print(img["data-src"])
                    img_url = img["href"]
                    secondaryImages.append('https:' + img_url)
       
        # Remove duplicates and limit to 4
        secondaryImages = list(dict.fromkeys(secondaryImages))[:4]
        product['secondaryImages'] = secondaryImages
        product['sizes'] = availableSizes

    except Exception as e:
        print("An Error Occurred While Getting The Product Details")
        print(str(e))

        with open("errors/error_Chicophicial.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
            }
            json.dump(error_log, f)
            f.write(',')

    return product