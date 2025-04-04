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
    # with open("output.html", "w", encoding="utf-8") as file:
    #     file.write(soup.prettify())
    try:
        mainContainer = soup.find('div',{'class': 'grid grid--uniform small--grid--flush'})
        productsDiv = mainContainer.find_all('div', {'class': 'grid__item'})
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
            name = product.find('div',{'class','grid-product__title'}).text.strip() 
            url = product.find('a',{'class','grid-product__link'})['href']
            imageUrl = product.find('img', {'class','grid-product__image'})['src']
            productID =  product['data-product-id']
            try:                    
                oldPrice = product.find('span', {'class', 'grid-product__price--original'}).text.strip()
                discount =  product.find('span', {'class', 'grid-product__price--savings'}).text.strip()
                oldPrice = functions.extractInt(oldPrice)
                discount = functions.extractInt(discount)
                newPrice = oldPrice - (oldPrice * discount / 100)
            except:
                newPrice = product.find('div',{'class','grid-product__price'}).text.strip()
                newPrice =functions.extractInt(newPrice)
                oldPrice = 0
                discount = 0
            
            tmp_product['productID'] = productID
            tmp_product['name'] = functions.filterName(name,productID)
            tmp_product['oldPrice'] = oldPrice
            tmp_product['newPrice'] = newPrice
            tmp_product['discount'] = discount
            tmp_product['url'] = 'https://hijabi.pk'+  url
            tmp_product['imageUrl'] = 'https:' + imageUrl
            tmp_product['category'] =  category
            tmp_product['subCategory'] = subCategory
            tmp_product['subSubCategory'] = subSubCategory
            tmp_product['piece'] = piece

            products.append(tmp_product) 
            #print(tmp_product)
            
    except Exception as e:
            with open("errors/error_Hijabi.json", "a") as f:
                    error_log = {
                    "datetime": datetime.datetime.now().isoformat(),
                    "product_name": str(name),
                    "exception_message": str(e),
                    "pageURL number": pageURL
                    }
                    json.dump(error_log, f)    
 
    return products




def getHijabiProductDetails(product): 
    try:
        html = functions.getRequest(product["url"], 'text')
        soup = BeautifulSoup(html, "html.parser")
        
        with open("output.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())

      
        availableSizes = []
        availableColors = []
        secondaryImages = []
        
        Element = soup.find('select', {'class':'product-single__variants no-js'})
        sizeElement = Element.find_all('option')
        for size in sizeElement:
            try:
                size = size.text.strip()
                size_color_price = size.split(' / ')
                size = size_color_price[0]
                color = size_color_price[1].split(' - ')[0]
                availableSizes.append(size)
                availableColors.append(color)
            except:
                size_color_price = size.split(' - ')
                size = size_color_price[0]
                availableSizes.append(size)
                

        productDescription = str(soup.find_all('div', {'class':'rte'})[1])
        

        availableSizes = list(set(availableSizes))
        availableColors = list(set(availableColors))
        
        mainContainer = soup.find('div',{'class':'product__thumbs--scroller'})
        secondaryImagesDiv = mainContainer.find_all('div',{'class','product__thumb-item'})
        
        for img in secondaryImagesDiv:
            img = img.find('a')
            if img is not None:
                if 'href' in img.attrs:
                    img_url = img["href"]
                    secondaryImages.append('https:' + img_url)

        secondaryImages= list(set(secondaryImages))
        # secondaryImages = [image for image in secondaryImages if image != product['imageUrl']]

        productDescription = functions.filterDescription(productDescription)
        availableSizes = functions.sortSizes('Hijabi', availableSizes)
        availableColors = functions.sortColors('Hijabi', availableColors)
        
        print(product["url"],productDescription,availableSizes,availableColors,secondaryImages[:4])

        product['Description'] = productDescription
        product['Sizes'] = availableSizes
        product['Colors'] = availableColors
        product['secondaryImages'] = secondaryImages[:4]
        product['sizeColors'] = functions.crossJoin(availableSizes,availableColors)

    except Exception as e:
        print ("An Error Occured While Getting The Product Details")
        print(product['url'],str(e))
        with open("errors/error_Ethnic.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
                }
            json.dump(error_log, f)  
    return product              