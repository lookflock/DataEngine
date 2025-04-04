import json
from bs4 import BeautifulSoup
import math
import statistics
import os
import datetime
import re
import config
import functions


def getProducts(soup, category, subCategory, subSubCategory, piece, pageURL):
    
    products = []
    mainContainer = soup.find('div',{'class':"t4s-col-item t4s-col-12 t4s-main-area t4s-main-collection-page"})
    productsDiv = mainContainer.find_all('div', {'class': 't4s-product'})
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
            # with open("output3.html", "w", encoding="utf-8") as f:
            #     f.write(product.prettify())
            name = product.find('h3',{'class','t4s-product-title'}).text.strip()
            url = product.find('a',{'class','t4s-full-width-link'})['href']
            try:
                imgDiv =product.find('img', {'class','t4s-product-main-img'}) 
                imageUrl = imgDiv['data-src']
                imageUrl = imageUrl.replace('width=1','width=1000')
                productJson =  json.loads(product['data-product-options'])
                productID = productJson['id']
                try:                   
                    priceDiv = product.find('div',{'class','t4s-product-price'}).find_all('span',{'class','money'})
                    oldPrice = priceDiv[0].text.strip()
                    oldPrice = functions.extractInt(oldPrice)
                    newPrice = priceDiv[1].text.strip()
                    newPrice =functions.extractInt(newPrice)
                    discount = math.ceil((oldPrice - newPrice) / oldPrice * 100)
                    if discount == 0:
                        oldPrice = 0    
                except:
                    newPrice = product.find('div',{'class','t4s-product-price'}).find('span',{'class','money'}).text.strip()
                    newPrice = functions.extractInt(newPrice)
                    oldPrice = 0
                    discount = 0
            
                tmp_product['productID'] = productID
                tmp_product['name'] = functions.filterName(name,productID)
                tmp_product['oldPrice'] = oldPrice
                tmp_product['newPrice'] = newPrice
                tmp_product['discount'] = discount
                tmp_product['url'] = 'https://thecambridgeshop.com'+  url
                tmp_product['imageUrl'] = 'https:' + imageUrl
                tmp_product['category'] =  category
                tmp_product['subCategory'] = subCategory
                tmp_product['subSubCategory'] = subSubCategory
                tmp_product['piece'] = piece
                products.append(tmp_product) 
                #print(tmp_product)
            except Exception as e:
                with open("errors/error_Cambridge.json", "a") as f:
                    error_log = {
                    "datetime": datetime.datetime.now().isoformat(),
                    "product_name": str(name),
                    "exception_message": str(e),
                    "page number": pageURL
                    }
                    json.dump(error_log, f)    
 
    return products


def getCambridgeProductDetails(product):
    try:
        html = functions.getRequest(product["url"], 'text')
        soup = BeautifulSoup(html, "html.parser")
        
        with open("output.html", "w", encoding="utf-8") as f:
             f.write(soup.prettify())

        availableSizes = []
        availableColors = []
        secondaryImages =[]
        Elements = soup.find_all('div', {'class': 't4s-swatch__list'})
        
        sizeElement =Elements[1].find_all('div', {'class': 't4s-swatch__item'})
        for size in sizeElement:
            availableSizes.append(size.text.strip())

        colorElement = Elements[0].find_all('div', {'class': 't4s-swatch__item'})
        for color in colorElement:
            availableColors.append(color.text.strip())
        

        productDescription= str(soup.find('div', {'class': 'full description'}))

        mainContainer = soup.find('div',{'class':'t4s-row t4s-g-0'})
        secondaryImagesDiv = mainContainer.find_all('div',{'class':'t4s-col-md-6'})
        
        for img in secondaryImagesDiv:
            img = img.find('img')
            if img is not None:
                if 'srcset' in img.attrs:
                    img_url = img["srcset"].split(',')[0][:-5].replace('&width=288','&width=1000')
                    secondaryImages.append('https:' + img_url)

        secondaryImages= list(set(secondaryImages))
        # secondaryImages = [image for image in secondaryImages if image != product['imageUrl']]
        productDescription = functions.filterDescription(productDescription)
        availableSizes = functions.sortSizes('Cambridge',availableSizes)
        availableColors = functions.sortColors("Cambridge",availableColors)
        
        print(product["url"],productDescription,availableSizes,availableColors,secondaryImages[:4])


        product['Description'] = productDescription
        product['Sizes'] = availableSizes
        product['Colors'] = availableColors
        product['secondaryImages'] = secondaryImages[:4]
        product['sizeColors'] = functions.crossJoin(availableSizes,availableColors)

        
    except Exception as e:
        print ("An Error Occured While Getting The Product Details")
        print(str(e))
        with open("errors/error_Cambridge.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
                }
            json.dump(error_log, f)  
    return product          
