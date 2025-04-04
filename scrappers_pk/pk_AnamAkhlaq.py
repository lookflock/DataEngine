import json
from bs4 import BeautifulSoup
import datetime
import math
import os
import random
import functions


def getProducts(soup, category, subCategory, subSubCategory, piece, pageURL):
    products = []
    mainContainer = soup.find('ul', {'class': 'grid grid--uniform grid--view-items'})
    productsDiv = mainContainer.find_all('li',{'class': 'grid__item'})    
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
        nameDiv = product.find('a', {'class': 'grid-view-item__link'})
        name = nameDiv.text.strip()
        try:    
            productID = product.find('div',{'class','grid-view-item__image-wrapper'})['id'].split('-')[-1]     
            url = nameDiv['href']
            imageUrl = product.find('div', {'class': 'grid-view-item__image-wrapper'}).find('img',{'class':'grid-view-item__image'})['data-src']
            imageUrl = imageUrl.replace('_{width}x', '_1000x')
            USD_convert = 281.07
            try:
                oldPrice = product.find('span', class_='price-item price-item--regular').text.strip()
                oldPrice = functions.extractInt(oldPrice)*USD_convert
                newPrice = product.find('span', class_='price-item price-item--sale').text.strip()
                newPrice = functions.extractInt(newPrice)*USD_convert
                discount = math.ceil((oldPrice - newPrice) / oldPrice * 100)
                if discount == 0:
                    oldPrice = 0
            except:
                newPrice = product.find('span', class_='price-item--sale').text.strip()
                newPrice = functions.extractInt(newPrice)*USD_convert
                oldPrice = 0
                discount = 0
            
            tmp_product['productID'] = productID
            # tmp_product['name'] = name
            tmp_product['name'] = functions.filterName(name,productID)
            tmp_product['oldPrice'] = int(oldPrice)
            tmp_product['newPrice'] = int(newPrice)
            tmp_product['discount'] = int(discount)
            tmp_product['url'] =  'https://anamakhlaq.com' + url
            tmp_product['imageUrl'] = 'https:' + imageUrl 
            tmp_product['category'] =  category
            tmp_product['subCategory'] = subCategory
            tmp_product['subSubCategory'] = subSubCategory
            tmp_product['piece'] = piece
            products.append(tmp_product)    

        except Exception as e:
            with open("errors/error_Almirah.json", "a") as f:
                error_log = {
                    "datetime": datetime.datetime.now().isoformat(),
                    "product_name": str(name),
                    "exception_message": str(e),
                    "pageURL number": pageURL
                    }
                json.dump(error_log, f)
       
    return products


def getAnamAkhlaqProductDetails(product):  
    try:
        html = functions.getRequest(product["url"], 'text')
        soup = BeautifulSoup(html, "html.parser")
        
        # with open("output.html", "w", encoding="utf-8") as f:
            #  f.write(soup.prettify())
        
        availableSizes = []
        availableColors = []
        secondaryImages = []
        # Extracting available sizes,colors and description
        try:
            sizeElements = soup.find('select',{'class','single-option-selector'}).find_all('option')
            for element in sizeElements:
                availableSizes.append(element['value'])
        except:
            availableSizes = []
        

        productDescription= str(soup.find('div', {'class': 'product-single__description rte'}))
        
        # to include the table
        # productDescription += str(soup.find('div', {'class': 'collapsible-content__inner rte'}))
        try:
            mainContainer = soup.find('ul',{'class':'grid grid--uniform product-single__thumbnails product-single__thumbnails-product-template'})
            secondaryImagesDiv = mainContainer.find_all('li',{'class':'grid__item'})
            
            for img in secondaryImagesDiv:
                img = img.find('a')
                # print(img)
                if 'href' in img.attrs:
                        # print(img["data-src"])
                        img_url = img["href"]
                        secondaryImages.append('https:' + img_url)

            secondaryImages= list(set(secondaryImages))
        except:
            secondaryImages = []

        
        # secondaryImages = [image for image in secondaryImages if image != product['imageUrl']]
        availableColors= list(set(availableColors))

        productDescription = functions.filterDescription(productDescription)
        availableSizes = functions.sortSizes('AnamAkhlaq',availableSizes)
        availableColors = functions.sortColors('AnamAkhlaq',availableColors)


        print(product["url"],productDescription,availableSizes,availableColors,secondaryImages[:4])

        product['Description'] = productDescription
        product['Sizes'] = availableSizes
        product['Colors'] = availableColors
        product['secondaryImages'] = secondaryImages[:4]
        product['sizeColors'] = functions.crossJoin(availableSizes,availableColors)

    except Exception as e:
        print(product["url"])
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