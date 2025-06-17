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
        mainContainer = soup.find('ul',{'class': 'grid'})
        productsDiv = mainContainer.find_all('li', {'class': 'grid__item'})
        #print(len(productsDiv))
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
                'page': pageURL,
                'views' : 0,
                'likes' : 0,
                'shares' : 0,
                'favourites' : 0,
                'list' : 0,
                'keywords': [],
                'piece': ''
            }            
            
            nameDiv =product.find('div',{'class':'card__information'}) 
            name = nameDiv.text.strip()
            url = nameDiv.find('a',{'class':'product-link-main'})['href']
            imageUrl = product.find('img')['src']
            productID =  product['data-variant-id']
            priceDiv = product.find('div',{'class':'price__container'})
            try:                    
                oldPrice = priceDiv.find('div',{'class':'price__sale'}).find('span',{'class':'money'}).text.strip()
                oldPrice = functions.extractInt(oldPrice)
                newPrice = priceDiv.find('div',{'class':'price__regular'}).find('span',{'class':'money'}).text.strip()
                newPrice =functions.extractInt(newPrice)
                discount = math.ceil((newPrice - oldPrice) / oldPrice * 100)
                discount = abs(discount)
                if discount == 0:
                     oldPrice = 0
            except:
                newPrice = priceDiv.find('span',{'class':'money'}).text.strip()
                newPrice = functions.extractInt(newPrice)
                oldPrice = 0
                discount = 0
            
            tmp_product['id'] = productID
            tmp_product['name'] = functions.filterName(name,productID)
            tmp_product['oldPrice'] = oldPrice
            tmp_product['newPrice'] = newPrice
            tmp_product['discount'] = discount
            tmp_product['url'] = 'https://outfitters.com.pk'+  url
            tmp_product['imageUrl'] = 'https:' + imageUrl
            tmp_product['category'] =  category
            tmp_product['subCategory'] = subCategory
            tmp_product['subSubCategory'] = subSubCategory
            tmp_product['piece'] = piece
            products.append(tmp_product) 
            # print(tmp_product)
            
    except Exception as e:
            with open("errors/error_Outfitters.json", "a") as f:
                    error_log = {
                    "datetime": datetime.datetime.now().isoformat(),
                    #"product_name": str(name),
                    "exception_message": str(e),
                    "pageURL number": pageURL
                    }
                    json.dump(error_log, f)    

    return products





def getOutfittersProductDetails(product):
    try:
        html = functions.getRequest(product["url"], 'text')
        soup = BeautifulSoup(html, "html.parser")
        
        with open("output.html", "w", encoding="utf-8") as f:
             f.write(soup.prettify())

        
        availableSizes = []
        availableColors = []    
        productDescription = ""
        secondaryImages = []

        productDescription = str(soup.find('div',{'class':'product__description'}))

        #Size
        try:
            sizeElement = soup.find('div',{'class':'size-wrapper'}).find_all('input')
            for size in sizeElement:
                availableSizes.append(size['data-filter'])
        except:
            availableSizes = []
            

        #Color
        try:
            colorElement = soup.find('div',{'class':'color-wrapper'}).find_all('input')
            for color in colorElement:
                availableColors.append(color['data-filter'])
        except:
            availableColors = []    

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
        availableSizes = functions.sortSizes('Outfitters', availableSizes)
        availableColors = functions.sortColors('Outfitters', availableColors)
        
        print(product["url"],productDescription,availableSizes,availableColors,secondaryImages[:4])


        product['Description'] = productDescription
        product['Sizes'] = availableSizes
        product['Colors'] = availableColors
        product['secondaryImages'] = secondaryImages[:4]
        product['sizeColors'] = functions.crossJoin(availableSizes,availableColors)

    except Exception as e:
        print ("An Error Occured While Getting The Product Details")
        print(product["url"] , str(e))
        with open("errors/error_Outfitters.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
                }
            json.dump(error_log, f) 
    return product

