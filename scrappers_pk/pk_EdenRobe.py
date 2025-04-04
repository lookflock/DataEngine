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
    mainContainer = soup.find('ul', {'class','products collection row small-up-2 medium-up-4 pagination--infinite'})
    productsDiv = mainContainer.find_all('li', {'class': 'column'})
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
                'pageUrl': pageURL,
                'views' : 0,
                'likes' : 0,
                'shares' : 0,
                'favourites' : 0,
                'list' : 0,
                'keywords': [],
                'piece': ''
            }
            
            urlDiv = product.find('a',{'class','product-card-title'})
            name = urlDiv.text.strip()
            url = urlDiv['href']
            try:
                imageUrl = product.find('img', {'class','lazyload product-primary-image'})['src']
                imageUrl = imageUrl.replace('_20x_', '_1000x_')
                # url_parts = imageUrl.split('/')
                productID = product.find('a',{'class','product-card-title'})['title'].split(' - ')[-1].strip()
                # imageUrl = imageUrl.replace('{width}', '360')
                prices = product.find_all('span',{'class','amount'})
                try:                    
                    oldPrice = prices[0].text.strip()
                    oldPrice = functions.extractInt(oldPrice)
                    newPrice = prices[1].text.strip()
                    newPrice =functions.extractInt(newPrice)
                    discount = math.ceil((oldPrice - newPrice) / oldPrice * 100)
                    if discount == 0:
                         oldPrice = 0
                except:
                    newPrice = prices[0].text.strip()
                    newPrice =functions.extractInt(newPrice)
                    oldPrice = 0
                    discount = 0
            
                tmp_product['productID'] = productID
                tmp_product['name'] = functions.filterName(name,productID)
                tmp_product['oldPrice'] = oldPrice
                tmp_product['newPrice'] = newPrice
                tmp_product['discount'] = discount
                tmp_product['url'] = 'https://edenrobe.com'+  url
                tmp_product['imageUrl'] = 'https:' + imageUrl
                tmp_product['category'] =  category
                tmp_product['subCategory'] = subCategory
                tmp_product['subSubCategory'] = subSubCategory
                tmp_product['piece'] = piece
                products.append(tmp_product) 

            except Exception as e:
                with open("errors/error_EdenRobe.json", "a") as f:
                    error_log = {
                    "datetime": datetime.datetime.now().isoformat(),
                    "product_name": str(name),
                    "exception_message": str(e),
                    "pageURL number": pageURL
                    }
                    json.dump(error_log, f)    
 
    return products



def getEdenRobeProductDetails(product):
    try:
        html = functions.getRequest(product["url"], 'text')
        soup = BeautifulSoup(html, "html.parser")
        
        #with open("output.html", "w", encoding="utf-8") as f:
        #    f.write(soup.prettify())

        
        availableSizes = []
        availableColors = []
        secondaryImages = []


        try:
            sizeElement = soup.find('fieldset',{'data-handle': 'size'})
            sizeElement = sizeElement.find_all('label')
            for size in sizeElement:
                availableSizes.append(size.text.strip())
        except:
            availableSizes = []
            
        try:
            colorElement = soup.find('fieldset',{'data-handle': 'color'})
            colorElement = colorElement.find_all('label')
            for color in colorElement:
                availableColors.append(color.text.strip())
        except:
            colorElement = []

        productDescription= str(soup.find('div', {'class': 'product-short-description rte'}))

        mainContainer = soup.find('div',{'class':'product-image-container'})
        secondaryImagesDiv = mainContainer.find_all('img')
        
        for img in secondaryImagesDiv:
            if img is not None:
                if 'src' in img.attrs:
                    img_url = img["src"].replace('_20x','_1000x')
                    secondaryImages.append('https:' + img_url)

        secondaryImages= list(set(secondaryImages))
        # secondaryImages = [image for image in secondaryImages if image != product['imageUrl']]
        productDescription = functions.filterDescription(productDescription)
        availableSizes = functions.sortSizes('EdenRobe',availableSizes)
        availableColors = functions.sortColors('EdenRobe',availableColors)
        
        print(product["url"],productDescription,availableSizes,availableColors,secondaryImages[:4])


        product['Description'] = productDescription
        product['Sizes'] = availableSizes
        product['Colors'] = availableColors
        product['secondaryImages'] = secondaryImages[:4]
        product['sizeColors'] = functions.crossJoin(availableSizes,availableColors)


    except Exception as e:
        print ("An Error Occured While Getting The Product Details")
        print(str(e))
        with open("errors/error_EdenRobe.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
                }
            json.dump(error_log, f)  
    return product              