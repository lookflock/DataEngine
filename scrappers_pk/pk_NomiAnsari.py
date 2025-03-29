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
        mainContainer = soup.find('div', {'class': 'item-grid'})
        productsDiv = mainContainer.find_all('div',{'class': 'item-box'})

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
        
        
        nameDiv = i.find('div', {'class': 'picture'})
        name = i.find('h2',{'class','product-title'}).text.strip()
        try:    
            url = nameDiv.find('a')['href']
            productID = url.split("/")[-1]
            imageUrl = nameDiv.find('img',{'class','lazyload'})['data-src']
            # imageUrl = i.find('div', {'class': 'grid_img wow zoomIn lazyload primary'})['data-bgset'].split(" ")[0]
            imageUrl = imageUrl.replace('600.', '1000.')
            if name == '':
                    name = productID.upper()
            try:
                oldPrice = i.find('span', class_='price actual-price').text.strip()
                oldPrice = functions.extractInt(oldPrice)
                newPrice = i.find('span', class_='price sale-price').text.strip()
                newPrice = functions.extractInt(newPrice)
                discount = math.ceil((oldPrice - newPrice) / oldPrice * 100)
            except:
                newPrice = i.find('span', class_='price').text.strip()
                newPrice = functions.extractInt(newPrice)
                oldPrice = 0
                discount = 0
            
            tmp_product['productID'] = productID
            tmp_product['name'] = name
            # tmp_product['name'] = functions.filterName(name,productID)
            tmp_product['oldPrice'] = int(oldPrice)
            tmp_product['newPrice'] = int(newPrice)
            tmp_product['discount'] = int(discount)
            tmp_product['url'] =  'https://www.nomiansari.com.pk' + url
            tmp_product['imageUrl'] = imageUrl 
            tmp_product['category'] =  category
            tmp_product['subCategory'] = subCategory
            tmp_product['subSubCategory'] = subSubCategory
            tmp_product['piece'] = piece
            # print(tmp_product)
            products.append(tmp_product)    

        except Exception as e:
            with open("errors/error_NomiAnsari.json", "a") as f:
                error_log = {
                    "datetime": datetime.datetime.now().isoformat(),
                    "product_name": str(name),
                    "exception_message": str(e),
                    "pageURL": pageURL
                    }
                json.dump(error_log, f)
       
    return products



def getNomiAnsariProductDetails(product): 
    try:
        html = functions.getRequest(product["url"], 'text')
        soup = BeautifulSoup(html, "html.parser")
        
        with open("output.html", "w", encoding="utf-8") as f:
             f.write(soup.prettify())
        
        availableSizes = []
        availableColors = []
        secondaryImages = []
        # Extracting available sizes,colors and description
        sizeElements = soup.find('ul',{'class','option-list'}).find_all('li')
        for element in sizeElements:
            availableSizes.append(element.text.strip())


        # colorElement = soup.find('')
        # print(availableSizes)

        productDescription= str(soup.find('div', {'class': 'fabrics-sections'})) + "<br>" + str(soup.find('div', {'class': 'full-description'}))

        
        # to include the table
        # productDescription += str(soup.find('div', {'class': 'collapsible-content__inner rte'}))

        mainContainer = soup.find('div',{'class','thumb-holder'})
        secondaryImagesDiv = mainContainer.find_all('img')
        # print(secondaryImagesDiv)
        for img in secondaryImagesDiv:
            # img = img.find('a')
            # print(img)
            if 'src' in img.attrs:
                    # print(img["data-src"])
                    img_url = img["src"]
                    # img_url = img_url.replace('_100.','_1000.')
                    secondaryImages.append(img_url)

        secondaryImages= list(set(secondaryImages))
        # secondaryImages = [image for image in secondaryImages if image != product['imageUrl']]
        availableColors= list(set(availableColors))

        productDescription = functions.filterDescription(productDescription)
        availableSizes = functions.sortSizes('NomiAnasri',availableSizes)
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
        with open("errors/error_AnamAkhlaq.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
                }
            json.dump(error_log, f)  
    return product