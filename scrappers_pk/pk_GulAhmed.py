import json
from bs4 import BeautifulSoup
import math
import os
import datetime
import config
import functions 


import datetime
import json
import math

def getProducts(soup, category, subCategory, subSubCategory, piece, pageURL):
    products = []

    # Find the product list container
    ol = soup.find('ol', {'class': 'products list items product-items same-height'})
    if not ol:
        return products

    items = ol.findAll('li', {'class': 'item product product-item'})

    for i in items:
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
            'piece': piece
        }
        try:
            # Extract product name and ID
            name_tag = i.find('span', {'class': 'product-item-link'})
            name = name_tag.text.strip() if name_tag else "Unknown"
            
            productID_tag = i.find('div', {'class': 'price-box'})
            productID = productID_tag['data-product-id'] if productID_tag else "Unknown"

            # Extract prices
            price_box = i.find('div', {'class': 'price-box price-final_price'})
            price_wrappers = price_box.findAll('span', {'class': 'price-wrapper'}) if price_box else []
            
            newPrice = int(price_wrappers[0]['data-price-amount']) if len(price_wrappers) > 0 else 0
            oldPrice = int(price_wrappers[1]['data-price-amount']) if len(price_wrappers) > 1 else 0
            
            discount = math.ceil((oldPrice - newPrice) / oldPrice * 100) if oldPrice else 0

            # Extract product URL and image URL
            url = i.find('a', {'class': 'product photo product-item-photo'})['href']
            image_tag = i.find('span', {'class': 'main-image'}).find('img') if i.find('span', {'class': 'main-image'}) else None
            imageUrl = image_tag['src'] if image_tag else ""

            # Populate the product dictionary
            tmp_product['id'] = productID
            tmp_product['name'] = name
            tmp_product['oldPrice'] = oldPrice
            tmp_product['newPrice'] = newPrice
            tmp_product['discount'] = discount
            tmp_product['url'] = url
            tmp_product['imageUrl'] = imageUrl

            products.append(tmp_product)

        except Exception as e:
            with open("errors/error_GulAhmed.json", "a") as f:
                error_log = {
                    "datetime": datetime.datetime.now().isoformat(),
                    "product_name": name if 'name' in locals() else "Unknown",
                    "exception_message": str(e),
                    "pageURL": pageURL
                }
                json.dump(error_log, f)

    return products



def getGulAhmedProductDetails(product):
    try:
        html = functions.getRequest(product["url"], 'text')
        soup = BeautifulSoup(html, "html.parser")

        availableSizes = []
        availableColors = []
        secondaryImages = []

        # Extract available sizes
        sizeElement = soup.find('div', {'class': 'swatch-attribute-options clearfix'})
        if sizeElement:
            sizes = sizeElement.findAll('div', {'class': 'swatch-option text'})
            for size in sizes:
                availableSizes.append(size.text.strip())

        # Extract available colors
        colorElement = soup.find('div', {'class': 'swatch-attribute color'})
        if colorElement:
            colors = colorElement.findAll('div', {'class': 'swatch-option color'})
            for color in colors:
                availableColors.append(color['data-option-label'])

        # Extract product description
        productDescription = str(soup.find('div', {'class': 'product attribute description'}))

        # Extract secondary images
        mainContainer = soup.find('div', {'class': 'MagicToolboxSelectorsContainer'})
        if mainContainer:
            secondaryImagesDiv = mainContainer.find_all('a')
            for img in secondaryImagesDiv:
                if img and 'href' in img.attrs:
                    img_url = img["href"]
                    secondaryImages.append(img_url)

        secondaryImages = list(set(secondaryImages))
        productDescription = functions.filterDescription(productDescription)
        availableSizes = functions.sortSizes('GulAhmed', availableSizes)
        availableColors = functions.sortColors('GulAhmed', availableColors)

        print(product["url"], productDescription, availableSizes, availableColors, secondaryImages[:4])

        product['Description'] = productDescription
        product['Sizes'] = availableSizes
        product['Colors'] = availableColors
        product['secondaryImages'] = secondaryImages[:4]
        product['sizeColors'] = functions.crossJoin(availableSizes, availableColors)

    except Exception as e:
        print("An Error Occurred While Getting The Product Details")
        print(str(e))
        with open("errors/error_GulAhmed.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
            }
            json.dump(error_log, f)
    return product