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
    #with open("output.html", "w", encoding="utf-8") as file:
    #  file.write(soup.prettify())
    mainContainer = soup.find('div',{'class': 'collection'})
    productsDiv = mainContainer.find_all('li', {'class': 'product'})  
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
            name = product.find('a',{'class','card-title'}).find('span', {'class','text'}).text.strip()
            url = product.find('a',{'class','card-link'})['href']
            try:
                # imageUrl = product.find_all('img', {'class','motion-reduce lazyload'}).split(' ')[0]
                imageUrl = product.find('img', {"class","motion-reduce lazyload"})["data-srcset"].split(' ')[0]
                imageUrl = imageUrl.replace('165x','1000x')
                productID = url.split('/')[-1]
                try:           
                    oldPrice = product.find('span',{'class','price-item price-item--regular'}).text.strip()
                    oldPrice = functions.extractInt(oldPrice)
                    newPrice = product.find('span',{'class','price-item price-item--sale'}).text.strip()
                    newPrice = functions.extractInt(newPrice)
                    discount = math.ceil((oldPrice - newPrice) / oldPrice * 100)
                    if discount == 0:
                        oldPrice = 0
                except:
                    newPrice = product.find('span',{'class','price-item price-item--regular'}).text.strip()
                    newPrice = functions.extractInt(newPrice)
                    oldPrice = 0
                    discount = 0
            
                tmp_product['productID'] = productID
                tmp_product['name'] = functions.filterName(name,productID)
                tmp_product['oldPrice'] = oldPrice
                tmp_product['newPrice'] = newPrice
                tmp_product['discount'] = discount
                tmp_product['url'] = 'https://diners.com.pk'+  url
                tmp_product['imageUrl'] = 'https:' + imageUrl
                tmp_product['category'] =  category
                tmp_product['subCategory'] = subCategory
                tmp_product['subSubCategory'] = subSubCategory
                tmp_product['piece'] = piece
                tmp_product=getDinersProductDetails(tmp_product)
                #print(tmp_product)
                products.append(tmp_product) 
            
               
            except Exception as e:
                with open("errors/error_Diners.json", "a") as f:
                    error_log = {
                    "datetime": datetime.datetime.now().isoformat(),
                    "product_name": str(name),
                    "exception_message": str(e),
                    "pageURL number": pageURL
                    }
                    json.dump(error_log, f)    
 
    return products


def getDinersProductDetails(product):
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
        try:
            sizeElement = soup.find('div',{'class':'productView-options'}).find_all('span',{'class':'text'})
            for size in sizeElement:
                availableSizes.append(size.text.strip())
        except:
            availableSizes = []

        # Get Secondary Images
        # -----------------------
        mainContainer = soup.find('div',{'class':'productView-image-wrapper'})
        secondaryImagesDiv = mainContainer.find_all('img')
        
        for img in secondaryImagesDiv:
            if img is not None:
                if 'src' in img.attrs:
                    img_url = img["src"]
                    secondaryImages.append('https:' + img_url)
       
        # Remove duplicates and limit to 4
        secondaryImages = list(dict.fromkeys(secondaryImages))[:4]

        product['secondaryImages'] = secondaryImages
        product['sizes'] = availableSizes

    except Exception as e:
        print("An Error Occurred While Getting The Product Details")
        print(str(e))

        with open("errors/error_Diners.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
            }
            json.dump(error_log, f)
            f.write(',')

    return product
