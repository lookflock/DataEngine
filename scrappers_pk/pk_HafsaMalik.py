import json
from bs4 import BeautifulSoup
import datetime
import math
import os
import random
import functions


def getProducts(soup, category, subCategory, subSubCategory,piece, pageURL):
    products = []
    try:
        mainContainer = soup.find('div', {'class': 'col-lg-12 col-12'})
        productsDiv = mainContainer.find_all('div',{'class': 'col-lg-3'})

    except:
        return products

    with open("output.html", "w", encoding="utf-8") as f:
           f.write(soup.prettify())
    
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
        
        
        nameDiv = i.find('div', {'class': 'product-info__inner'})
        name = nameDiv.find('h3',{'class','product-title'}).text.strip()
        try:    
            url = nameDiv.find('a')['href']
            productID = i.find('div',{'class','product-info__btns'}).find('a')['data-id']
            # imageUrl = nameDiv.find('img',{'class','lazyload'})['data-src']
            # # imageUrl = i.find('div', {'class': 'grid_img wow zoomIn lazyload primary'})['data-bgset'].split(" ")[0]
            # imageUrl = imageUrl.replace('600.', '1000.')
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
            
            tmp_product['id'] = productID
            tmp_product['name'] = name
            # tmp_product['name'] = functions.filterName(name,productID)
            tmp_product['oldPrice'] = int(oldPrice)
            tmp_product['newPrice'] = int(newPrice)
            tmp_product['discount'] = int(discount)
            tmp_product['url'] =  'https://hafsamalik.com' + url
            # tmp_product['imageUrl'] = imageUrl 
            tmp_product['category'] =  category
            tmp_product['subCategory'] = subCategory
            tmp_product['subSubCategory'] = subSubCategory
            tmp_product['piece'] = piece
            # print(tmp_product)
            products.append(tmp_product)    

        except Exception as e:
            with open("errors/error_HafsaMalik.json", "a") as f:
                error_log = {
                    "datetime": datetime.datetime.now().isoformat(),
                    "product_name": str(name),
                    "exception_message": str(e),
                    "pageURL": pageURL
                    }
                json.dump(error_log, f)
       
    return products


def getHafsaMalikProductDetails(product):  
    try:
        html = functions.getRequest(product["url"], 'text')
        soup = BeautifulSoup(html, "html.parser")
        
        with open("output.html", "w", encoding="utf-8") as f:
             f.write(soup.prettify())
        
        availableSizes = []
        availableColors = []
        secondaryImages = []
        # Extracting available sizes,colors and description
        # sizeElements = soup.find('ul',{'class','option-list'}).find_all('li')
        # for element in sizeElements:
        #     availableSizes.append(element.text.strip())


        # colorElement = soup.find('')
        # print(availableSizes)

        productDescription=  str(soup.find('div', {'class': 'sp-tab-content'}).find('p'))

        
        # to include the table
        # productDescription += str(soup.find('div', {'class': 'collapsible-content__inner rte'}))

        mainContainer = soup.find('div',{'class','p-thumb'})
        secondaryImagesDiv = mainContainer.find_all('img')
        # print(secondaryImagesDiv)
        for img in secondaryImagesDiv:
            # img = img.find('a')
            # print(img)
            if 'src' in img.attrs:
                    # print(img["data-src"])
                    img_url = img["src"]
                    # img_url = img_url.replace('_100.','_1000.')
                    secondaryImages.append('https:' + img_url)

        secondaryImages= list(set(secondaryImages))
        # secondaryImages = [image for image in secondaryImages if image != product['imageUrl']]
        availableColors= list(set(availableColors))

        productDescription = functions.filterDescription(productDescription)
        # availableSizes = functions.sortSizes('',availableSizes)
        # availableColors = functions.sortColors('AnamAkhlaq',availableColors)


        print(product["url"],productDescription,availableSizes,availableColors,secondaryImages[:4])

        product['Description'] = productDescription
        product['Sizes'] = availableSizes
        product['Colors'] = availableColors
        product['imageUrl'] = secondaryImages[0]
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