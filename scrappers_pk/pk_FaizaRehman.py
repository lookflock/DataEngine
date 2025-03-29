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
        mainContainer = soup.find('div', {'class': 't4s_box_pr_grid'})
        productsDiv = mainContainer.find_all('div',{'class': 't4s-product'})

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
        
        
        nameDiv = i.find('div', {'class': 't4s-product-inner'})
        name = nameDiv.find('img')['alt']
        try:    
            url = nameDiv.find('a')['href']

            data_product_options = i['data-product-options']

            # Parse the JSON
            product_options = json.loads(data_product_options)

            # Extract the product ID
            productID = product_options.get('id', name)

            imageUrl = nameDiv.find('img',{'class','t4s-product-main-img'})['data-src']
            imageUrl = imageUrl.replace('width=1', 'width=1000')
            try:
                oldPrice = i.find('span', class_='price actual-price').text.strip()
                oldPrice = functions.extractInt(oldPrice)
                newPrice = i.find('span', class_='price sale-price').text.strip()
                newPrice = functions.extractInt(newPrice)
                discount = math.ceil((oldPrice - newPrice) / oldPrice * 100)
            except:
                newPrice = i.find('div', class_='t4s-product-price').text.strip()
                newPrice = functions.extractInt(newPrice)
                oldPrice = 0
                discount = 0
            
            tmp_product['productID'] = productID
            tmp_product['name'] = name
            # tmp_product['name'] = functions.filterName(name,productID)
            tmp_product['oldPrice'] = int(oldPrice)
            tmp_product['newPrice'] = int(newPrice)
            tmp_product['discount'] = int(discount)
            tmp_product['url'] =  'https://www.faizarehman.com' + url
            tmp_product['imageUrl'] = 'https:' + imageUrl 
            tmp_product['category'] =  category
            tmp_product['subCategory'] = subCategory
            tmp_product['subSubCategory'] = subSubCategory
            tmp_product['piece'] = piece
            products.append(tmp_product)    

        except Exception as e:
            with open("errors/error_FaizaRehman.json", "a") as f:
                error_log = {
                    "datetime": datetime.datetime.now().isoformat(),
                    "product_name": str(name),
                    "exception_message": str(e),
                    "pageURL": pageURL
                    }
                json.dump(error_log, f)
       
    return products


def getFaizaRehmanProductDetails(product):  
    try:
        html = functions.getRequest(product["url"], 'text')
        soup = BeautifulSoup(html, "html.parser")
        
        with open("output.html", "w", encoding="utf-8") as f:
             f.write(soup.prettify())
        
        availableSizes = []
        availableColors = []
        secondaryImages = []
        # Extracting available sizes,colors and description
        sizeElements = soup.find('div',{'class','t4s-dropdown__content'}).find_all('div',{'class','t4s-swatch__item'})
        for element in sizeElements:
            availableSizes.append(element.text.strip())


        # colorElement = soup.find('')
        # print(availableSizes)

        productDescription=  str(soup.find('div', {'class': 't4s-product__description t4s-rte'}).find('p'))

        
        # to include the table
        # productDescription += str(soup.find('div', {'class': 'collapsible-content__inner rte'}))

        # mainContainer = soup.find('div',{'class','t4s-col-12'})
        secondaryImagesDiv = soup.find_all('img',{'class','lazyloadt4s t4s-lz--fadeIn'})
        # print(secondaryImagesDiv)
        for img in secondaryImagesDiv:
            # img = img.find('a')
            # print(img)
            if 'data-src' in img.attrs:
                    # print(img["data-src"])
                    img_url = img["data-src"]
                    img_url = img_url.replace('&width=100','&width=1000')
                    img_url = img_url.replace('&width=1','')
                    secondaryImages.append('https:' + img_url)

        secondaryImages= list(set(secondaryImages))
        # secondaryImages = [image for image in secondaryImages if image != product['imageUrl']]
        availableColors= list(set(availableColors))

        productDescription = functions.filterDescription(productDescription)
        availableSizes = functions.sortSizes('Deepakperwani',availableSizes)
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