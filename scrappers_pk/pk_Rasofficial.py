import json
from bs4 import BeautifulSoup
import math
import os
import datetime
import re
import config
import functions


def getProducts(soup, category, subCategory, subSubCategory, piece, pageURL):
    products = []
    try:
        mainContainer = soup.find('ul', {'class': 'products'})
        productsDiv = mainContainer.find_all('li',{'class': 'entry'})
        
    except:
        return products

    # print(len(productsDiv))
    
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
                'pageURL': pageURL,
                'views' : 0,
                'likes' : 0,
                'shares' : 0,
                'favourites' : 0,
                'list' : 0,
                'keywords': []
            }
        
        # with open("output3.html", "w", encoding="utf-8") as f:
        #         f.write(product.prettify())
        # return
        # nameDiv = product.find('div', {'class': 'picture'})
        name = product.find('li',{'class','title'}).text.strip()
        try:    
            url = product.find('div',{'class','woo-entry-image-swap'}).find('a')['href']
            productID = product.find('a',{'class','owp-quick-view'})['data-product_id']
            imageUrl = product.find('div',{'class','woo-entry-image-swap'}).find('img',{'class','woo-entry-image-main'})['data-src']
            # imageUrl = imageUrl.replace('-300x300', '')
            try:
                oldPrice = product.find('span', {"class":'price actual-price'}).text.strip()
                oldPrice = functions.extractInt(oldPrice)
                newPrice = product.find('span', {"class":'price sale-price'}).text.strip()
                newPrice = functions.extractInt(newPrice)
                discount = math.ceil((oldPrice - newPrice) / oldPrice * 100)
            except:
                newPrice = product.find('span', class_='price').text.strip()
                newPrice = functions.extractInt(newPrice)
                oldPrice = 0
                discount = 0
            
            tmp_product['id'] = productID
            tmp_product['name'] = name
            # tmp_product['name'] = functions.filterName(name,productID)
            tmp_product['oldPrice'] = int(oldPrice)
            tmp_product['newPrice'] = int(newPrice)
            tmp_product['discount'] = int(discount)
            tmp_product['url'] =   url
            tmp_product['imageUrl'] = imageUrl 
            tmp_product['category'] =  category
            tmp_product['subCategory'] = subCategory
            tmp_product['subSubCategory'] = subSubCategory
            tmp_product['piece'] = piece
            # print(tmp_product)
            products.append(tmp_product)    

        except Exception as e:
            with open("errors/error_Rasofficial.json", "a") as f:
                error_log = {
                    "datetime": datetime.datetime.now().isoformat(),
                    "product_name": str(name),
                    "exception_message": str(e),
                    "pageURL number": pageURL
                    }
                json.dump(error_log, f)
       
    return products



def getRasofficialProductDetails(product): 
    try:
        html = functions.getRequest(product["url"], 'text')
        soup = BeautifulSoup(html, "html.parser")
        
        with open("output.html", "w", encoding="utf-8") as f:
             f.write(soup.prettify())
        
        availableSizes = []
        availableColors = []
        secondaryImages = []
        # Extracting available sizes,colors and description
        try:
            sizeElements = soup.find('select',{'class','woo-variation-raw-select'}).find_all('option')
            for element in sizeElements:
                availableSizes.append(element['value'])
        except:
            availableSizes = []


        # colorElement = soup.find('')
        # print(availableSizes)

        productDescription=  str(soup.find('div', {'aria-labelledby': 'tab-title-description'}))

        
        # to include the table
        # productDescription += str(soup.find('div', {'class': 'collapsible-content__inner rte'}))

        mainContainer = soup.find('div',{'class','woocommerce-product-gallery'})
        secondaryImagesDiv = mainContainer.find_all('img')
        # print(secondaryImagesDiv)
        for img in secondaryImagesDiv:
            # img = img.find('a')
            # print(img)
            if 'data-large_image' in img.attrs:
                    # print(img["data-src"])
                    img_url = img["data-large_image"].split('?')[0]
                    img_url = img_url.replace('i0.wp.com/','')
                    secondaryImages.append(img_url)

        secondaryImages= list(set(secondaryImages))
        # secondaryImages = [image for image in secondaryImages if image != product['imageUrl']]
        availableColors= list(set(availableColors))

        productDescription = functions.filterDescription(productDescription)
        availableSizes = functions.sortSizes('Rasofficial',availableSizes)


        print(product["url"],productDescription,availableSizes,availableColors,secondaryImages[:4])

        product['Description'] = productDescription
        product['Sizes'] = availableSizes
        product['Colors'] = availableColors
        product['secondaryImages'] = secondaryImages[:4]
        product['sizeColors'] = functions.crossJoin(availableSizes,availableColors)

    except Exception as e:
        print ("An Error Occured While Getting The Product Details")
        print(str(e))
        with open("errors/error_AnamAkhlaq.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
                }
            json.dump(error_log, f)  
    return product