import json
from bs4 import BeautifulSoup
import math
import os
import datetime
import re
import config
import functions


def getProducts(soup, category, subCategory, subSubCategory,piece, pageURL):
    products = []
    
    try:
        mainContainer = soup.find('div', {'class': 'product-grid-container'})
        productsDiv = mainContainer.find('ul', {'class': 'product-grid'}).find_all('li', {'class': 'grid__item'})

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
                'views': 0,
                'likes': 0,
                'shares': 0,
                'favourites': 0,
                'list': 0,
                'keywords': [],
                'piece': ''
            }

            # Get product name and URL
            name_element = product.find('h3', {'class': 'card__heading'}) or product.find('h3', {'class': 'card__heading h5'})
            if name_element:
                name_link = name_element.find('a', {'class': 'full-unstyled-link'})
                if name_link:
                    name = name_link.text.strip()
                    url = name_link['href']
                    tmp_product['name'] = functions.filterName(name, url.split('/')[-1])
                    tmp_product['url'] = 'https://pk.ethnc.com' + url
                    tmp_product['productID'] = url.split('/')[-1]

            # Get image URL
            img = product.find('img', {'class': 'motion-reduce'})
            if img:
                imageUrl = img['src']
                if not imageUrl.startswith('http'):
                    imageUrl = 'https:' + imageUrl
                tmp_product['imageUrl'] = imageUrl

            # Get prices
            price_container = product.find('div', {'class': 'price__container'})
            if price_container:
                # Check if there's a sale price
                sale_price = price_container.find('div', {'class': 'price__sale'})
                if sale_price:
                    # Get both regular and sale prices
                    regular_price = sale_price.find('s', {'class': 'price-item--regular'}).find('span', {'class': 'money'}).text.strip()
                    sale_price_value = sale_price.find('span', {'class': 'price-item--sale'}).find('span', {'class': 'money'}).text.strip()
                    
                    tmp_product['oldPrice'] = functions.extractInt(regular_price)
                    tmp_product['newPrice'] = functions.extractInt(sale_price_value)
                    
                    # Calculate discount from percentage if available
                    discount_percent = sale_price.find('span', {'class': 'percentage__sale'})
                    if discount_percent:
                        discount = functions.extractInt(discount_percent.text.strip().replace('-', '').replace('%', ''))
                    else:
                        # Calculate discount manually if percentage not available
                        discount = math.ceil((tmp_product['oldPrice'] - tmp_product['newPrice']) / tmp_product['oldPrice'] * 100)
                    
                    tmp_product['discount'] = discount
                else:
                    # Only regular price available
                    regular_price = price_container.find('div', {'class': 'price__regular'}).find('span', {'class': 'money'}).text.strip()
                    tmp_product['newPrice'] = functions.extractInt(regular_price)
                    tmp_product['oldPrice'] = 0
                    tmp_product['discount'] = 0

            # Set categories
            tmp_product['category'] = category
            tmp_product['subCategory'] = subCategory
            tmp_product['subSubCategory'] = subSubCategory
            tmp_product['piece'] = piece
            
            products.append(tmp_product)

    except Exception as e:
        with open("errors/error_Ethnic.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "exception_message": str(e),
                "pageURL": pageURL
            }
            json.dump(error_log, f)
            f.write('\n')  # Add newline for better log readability

    return products


def getEthnicProductDetails(product): 
    try:
        html = functions.getRequest(product["url"], 'text')
        soup = BeautifulSoup(html, "html.parser")
        
        #with open("output.html", "w", encoding="utf-8") as f:
        #    f.write(soup.prettify())

        
        availableSizes = []
        availableColors = []
        secondaryImages = []

        sizeElement = soup.find('fieldset',{'class':'js product-form__input option-size'}).find_all('input')
        for size in sizeElement:
            availableSizes.append(size['value'])
            

        productDescription = str(soup.find('div', {'class': 'product__description rte quick-add-hidden'}))
        mainContainer = soup.find('div',{'class':'swiper-wrapper'})
        secondaryImagesDiv = mainContainer.find_all('img')
        
        for img in secondaryImagesDiv:
            if img is not None:
                if 'src' in img.attrs:
                    img_url = img["src"]
                    secondaryImages.append('https:' + img_url)

        secondaryImages= list(set(secondaryImages))
        # secondaryImages = [image for image in secondaryImages if image != product['imageUrl']]
        productDescription = functions.filterDescription(productDescription)
        availableSizes = functions.sortSizes('Ethnic',availableSizes)
        availableColors = functions.sortColors('Ethnic',availableColors)
        
        print(product["url"],productDescription,availableSizes,availableColors,secondaryImages[:4])


        product['Description'] = productDescription
        product['Sizes'] = availableSizes
        product['Colors'] = availableColors
        product['secondaryImages'] = secondaryImages[:4]
        product['sizeColors'] = functions.crossJoin(availableSizes,availableColors)


    except Exception as e:
        print ("An Error Occured While Getting The Product Details")
        print(product["url"],str(e))
        with open("errors/error_Ethnic.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
                }
            json.dump(error_log, f)  
    return product              