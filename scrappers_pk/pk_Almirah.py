import json
from bs4 import BeautifulSoup
import datetime
import math
import os
import random
import functions


def getProducts(soup, category, subCategory, subSubCategory, pageURL):
    products = []
    mainContainer = soup.find('div', {'class': 'grid grid--uniform grid--collection'})
    productsDiv = mainContainer.find_all('div',{'class': 'grid-product__content'})

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
                'pageUrl': pageURL,
                'views' : 0,
                'likes' : 0,
                'shares' : 0,
                'favourites' : 0,
                'list' : 0,
                'keywords': []
            }
        
        
        name = i.find('div', {'class': 'grid-product__title grid-product__title--body'}).text.strip()
        name.replace("\u00a02", ' ')
        try:    
            productID = name.split(' - ')[1]
            url = i.find('a', {'class': 'grid-product__link'})['href']
            imageUrl = i.find('img', {'class': 'grid-product__image lazyloaded'})['src']
            imageUrl = imageUrl.replace('400x', '1000x')
            price_elements = i.find_all('span', {'class': 'money'})
            oldPrice = price_elements[0].text.strip().split('.')[1].replace(',', '')
            try:
                newPrice = price_elements[1].text.strip().split('.')[1].replace(',', '')
                temp_discount = i.find('div', {'class': 'grid-product__tag grid-product__tag--sale'}).text.strip()
                discount = temp_discount.split('%')[0]
            except:
                newPrice = oldPrice
                oldPrice = 0
                discount = 0
            
            tmp_product['productID'] = productID
            # tmp_product['name'] = name
            tmp_product['name'] = functions.filterName(name,productID)
            tmp_product['oldPrice'] = int(oldPrice)
            tmp_product['newPrice'] = int(newPrice)
            tmp_product['discount'] = int(discount)
            tmp_product['url'] =  'https://www.almirah.com.pk' + url
            tmp_product['imageUrl'] = 'https:' + imageUrl 
            tmp_product['category'] =  category
            tmp_product['subCategory'] = subCategory
            tmp_product['subSubCategory'] = subSubCategory
        
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


def getAlmirahProductDetails(product):  
    try:
        html = functions.getRequest(product["url"], 'text')
        soup = BeautifulSoup(html, "html.parser")
        
        with open("output.html", "w", encoding="utf-8") as f:
             f.write(soup.prettify())
        
        availableSizes = []
        availableColors = []
        secondaryImages = []
        # Extracting available sizes,colors and description
        varientElements = soup.find_all('div', {'class': 'variant-wrapper'}) # 0 is size 1 is color 2 is style (not used)
        sizeElements = varientElements[0].find_all('div', {'class': 'variant-input'})
        for element in sizeElements:
            availableSizes.append(element.find('label').text.strip())

        colorElements = varientElements[1].find_all('div', {'class': 'variant-input'})
        for element in colorElements:
            availableColors.append(element.find('label').text.strip())    

        productDescription= str(soup.find('div', {'class': 'product-single__description rte'}))
        
        # to include the table
        # productDescription += str(soup.find('div', {'class': 'collapsible-content__inner rte'}))

        mainContainer = soup.find('div',{'class':'product__photos'})
        secondaryImagesDiv = mainContainer.find_all('div',{'class':'product__thumb-item'})
        
        for img in secondaryImagesDiv:
            img = img.find('img')
            # print(img)
            if 'data-src' in img.attrs:
                    # print(img["data-src"])
                    img_url = img["data-src"].replace('{width}', '1000')
                    secondaryImages.append('https:' + img_url)

        secondaryImages= list(set(secondaryImages))
        # secondaryImages = [image for image in secondaryImages if image != product['imageUrl']]
        availableColors= list(set(availableColors))

        productDescription = functions.filterDescription(productDescription)
        availableSizes = functions.sortSizes('Almirah',availableSizes)
        availableColors = functions.sortColors('Almirah',availableColors)


        print(product["url"],productDescription,availableSizes,availableColors,secondaryImages[:4])

        product['Description'] = productDescription
        product['Sizes'] = availableSizes
        product['Colors'] = availableColors
        product['secondaryImages'] = secondaryImages[:4]
        product['sizeColors'] = functions.crossJoin(availableSizes,availableColors)

    except Exception as e:
        print ("An Error Occured While Getting The Product Details")
        print(str(e))
        with open("errors/error_Almirah.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
                }
            json.dump(error_log, f)  
    return product