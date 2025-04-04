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
        mainContainer = soup.find('div',{'class': 'collection__products'})
        productsDiv = mainContainer.find_all('div', {'class': 'product-item'})
        for i in productsDiv:           
            # with open("output.html", "w", encoding="utf-8") as file:
            #     file.write(i.prettify())
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
                'page': pageURL,
                'views' : 0,
                'likes' : 0,
                'shares' : 0,
                'favourites' : 0,
                'list' : 0,
                'keywords': [],
                'piece': ''
            }
            nameDiv =i.find('a',{'class':'product-item__image-link'}) 
            name = nameDiv['aria-label']
            url = nameDiv['href']
            imageUrl = i.find('img', {'class':'image__img'})['src']
            imageUrl = imageUrl.replace('width=320','width=1000')
            productID =  url.split('/')[-1]
            try:                    
                oldPrice = i.find('p',{'class':'product-item__price'}).find('s',{'class':'t-subdued'}).text.strip()
                oldPrice = functions.extractInt(oldPrice)
                newPrice = i.find('p',{'class':'product-item__price'}).find('span',{'class':'sale'}).text.strip()
                newPrice =functions.extractInt(newPrice)
                discount = math.ceil((oldPrice - newPrice) / oldPrice * 100)
                if discount == 0:
                     oldPrice = 0
            except:
                newPrice = i.find('p',{'class':'product-item__price'}).text.strip()
                newPrice =functions.extractInt(newPrice)
                oldPrice = 0
                discount = 0
            
            tmp_product['productID'] = productID
            tmp_product['name'] = functions.filterName(name,productID)
            tmp_product['oldPrice'] = oldPrice
            tmp_product['newPrice'] = newPrice
            tmp_product['discount'] = discount
            tmp_product['url'] = 'https://lakhanyonline.com'+  url
            tmp_product['imageUrl'] = 'https:' + imageUrl
            tmp_product['category'] =  category
            tmp_product['subCategory'] = subCategory
            tmp_product['subSubCategory'] = subSubCategory
            tmp_product['piece'] = piece
            products.append(tmp_product) 
                #print(tmp_product)
            
    except Exception as e:
            with open("errors/error_lakhanyonline.json", "a") as f:
                    error_log = {
                    "datetime": datetime.datetime.now().isoformat(),
                    "product_name": str(name),
                    "exception_message": str(e),
                    "pageURL number": pageURL
                    }
                    json.dump(error_log, f)    
 
    return products

def getLakhanayProductDetails(product):
    try:
        html = functions.getRequest(product["url"], 'text')
        soup = BeautifulSoup(html, "html.parser")
        
        with open("output_L.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())


        availableSizes = []
        availableColors = []
        productDescription = ''
        secondaryImages = []
        try:
            sizeElement = soup.find('div',{'class':'product__color-chips dynamic-variant-input-wrap'}).findAll('button')
            for size in sizeElement:
                availableSizes.append(size.text.strip())
        except :
            availableSizes = []


        if len(availableSizes) == 0:
            try:
                sizeElement = soup.find('div',{'class':'select-wrapper dynamic-variant-input-wrap'}).findAll('option')
                for size in sizeElement:
                    availableSizes.append(size.text.strip())
            except:
                availableSizes = []

        try:
            colorElement = soup.find('div', {'class':'product__color-swatches--inner dynamic-variant-input-wrap'})
            colors = colorElement.find('select', {'class':'input dynamic-variant-input'}).findAll('option')
            for color in colors:
                availableColors.append(color.text.strip())
        except:
            try:
                colorElement = soup.find('div', {'class': 'product__description'}).find_all('span')
                color = colorElement[-1].text.strip()
                availableColors.append(color)
            except:
                availableColors= []

        productDescription = str(soup.find('div', {'class': 'product__description'}))
        
        mainContainer = soup.find('div',{'class':'product__media-container'})
        secondaryImagesDiv = mainContainer.find_all('img')
        
        for img in secondaryImagesDiv:
            if img is not None:
                if 'src' in img.attrs:
                    img_url = img["src"].replace('&width=320','&width=1000')
                    secondaryImages.append('https:' + img_url)

        secondaryImages= list(set(secondaryImages))
        # secondaryImages = [image for image in secondaryImages if image != product['imageUrl']]
        productDescription = functions.filterDescription(productDescription)
        availableSizes = functions.sortSizes('Lakhanay', availableSizes)
        availableColors = functions.sortColors('Lakhanay', availableColors)
        
        
        print(product["url"],productDescription,availableSizes,availableColors,secondaryImages[:4])


        product['Description'] = productDescription
        product['Sizes'] = availableSizes
        product['Colors'] = availableColors
        product['secondaryImages'] = secondaryImages[:4]
        product['sizeColors'] = functions.crossJoin(availableSizes,availableColors)

    except Exception as e:
        print ("An Error Occured While Getting The Product Details")
        print(product["url"],str(e))
        with open("errors/error_Lakhanay.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
                }
            json.dump(error_log, f)  
    return product                