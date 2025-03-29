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
        mainContainer = soup.find('ul', {'id': 'product-grid'})
        productsDiv = mainContainer.find_all('li',{'class': 'grid__item'})

    except:
        return products

    with open("output.html", "w", encoding="utf-8") as f:
           f.write(soup.prettify())

    # print(len(productsDiv))
    
    for i in productsDiv:
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
                'views' : 0,
                'likes' : 0,
                'shares' : 0,
                'favourites' : 0,
                'list' : 0,
                'keywords': [],
                'piece': ''
            }
        
        
        # nameDiv = i.find('div', {'class': 'picture'})
        name = i.find('h3',{'class','card__heading'}).text.strip()
        try:    
            url = i.find('a')['href']
            productID = i.find('h3',{'class','card__heading h5'})['id'].split('-')[-1]

            imageUrl = i.find('img',{'class','motion-reduce'})['src']
            imageUrl = imageUrl.replace(';width=533', ';width=1000')
            try:
                oldPrice = i.find('s', class_='price-item--regular').text.strip()
                oldPrice = functions.extractInt(oldPrice)
                newPrice = i.find('span', class_='price-item--sale').text.strip()
                newPrice = functions.extractInt(newPrice)
                discount = math.ceil((oldPrice - newPrice) / oldPrice * 100)
                if discount == 0:
                    oldPrice = 0
            except:
                newPrice = i.find('span', class_='price-item').text.strip()
                newPrice = functions.extractInt(newPrice)
                oldPrice = 0
                discount = 0
            
            tmp_product['productID'] = productID
            # tmp_product['name'] = name
            tmp_product['name'] = functions.filterName(name,productID)
            tmp_product['oldPrice'] = int(oldPrice)
            tmp_product['newPrice'] = int(newPrice)
            tmp_product['discount'] = int(discount)
            tmp_product['url'] =  'https://nausheenwamiq.store' + url
            tmp_product['imageUrl'] = 'https:' + imageUrl 
            tmp_product['category'] =  category
            tmp_product['subCategory'] = subCategory
            tmp_product['subSubCategory'] = subSubCategory
            tmp_product['piece'] = piece
            # print(tmp_product)
            products.append(tmp_product)    

        except Exception as e:
            with open("errors/error_NausheenWamiq.json", "a") as f:
                error_log = {
                    "datetime": datetime.datetime.now().isoformat(),
                    "product_name": str(name),
                    "exception_message": str(e),
                    "pageURL": pageURL
                    }
                json.dump(error_log, f)
       
    return products



def getNausheenWamiqProductDetails(product): 
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
            sizeElements = soup.find('fieldset',{'class','js product-form__input product-form__input--pill'}).find_all('input')
            for element in sizeElements:
                availableSizes.append(element['value'])
        except:
            availableSizes = []


        productDescription= str(soup.find('div', {'class': 'product__description'}))

        


        mainContainer = soup.find('ul',{'class','product__media-list'})
        secondaryImagesDiv = mainContainer.find_all('li')
        # print(secondaryImagesDiv)
        for img in secondaryImagesDiv:
            img = img.find('img')
            # print(img)
            if 'src' in img.attrs:
                    # print(img["data-src"])
                    img_url = img["src"]
                    img_url = img_url.replace('&width=1946','&width=1000')
                    secondaryImages.append('https:' + img_url)

        secondaryImages= list(set(secondaryImages))
        # secondaryImages = [image for image in secondaryImages if image != product['imageUrl']]
        availableColors= list(set(availableColors))

        productDescription = functions.filterDescription(productDescription)
        availableSizes = functions.sortSizes('NausheenWamiq',availableSizes)
        # availableColors = functions.sortColors('AnamAkhlaq',availableColors)


        print(product["url"],productDescription,availableSizes,availableColors,secondaryImages[:4])

        product['Description'] = productDescription
        product['Sizes'] = availableSizes
        product['Colors'] = availableColors
        product['secondaryImages'] = secondaryImages[:4]
        product['sizeColors'] = functions.crossJoin(availableSizes,availableColors)

    except Exception as e:
        print ("An Error Occured While Getting The Product Details")
        print(str(e))
        with open("errors/error_NausheenWamiq.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
                }
            json.dump(error_log, f)  
    return product