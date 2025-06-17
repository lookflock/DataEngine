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
    #with open("output.html", "w", encoding="utf-8") as file:
    #    file.write(soup.prettify())
    try:
        mainContainer = soup.find('div',{'class': 't4s_box_pr_grid'})
        productsDiv = mainContainer.find_all('div', {'class': 't4s-product'})
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
            nameDiv =i.find('div',{'class':'t4s-product-info'})
            name = nameDiv.find('h3').text.strip()
            url = nameDiv.find('a')['href']
            imageUrl = i.find('img', {'class':'t4s-product-main-img'})['data-src']
            imageUrl = imageUrl.replace('width=1','width=1000')
            productOptions  =  json.loads(i['data-product-options'])
            productID = productOptions.get('id', '')
            try:                    
                oldPrice = productOptions.get('compare_at_price', 0)
                oldPrice = int(oldPrice / 100)
                newPrice = productOptions.get('price', 0)
                newPrice = int(newPrice / 100)
                discount = math.ceil((newPrice - oldPrice) / oldPrice * 100)
                discount = abs(discount)
                if discount == 0:
                     oldPrice = 0
            except:
                newPrice = productOptions.get('price', 0)
                newPrice = int(newPrice / 100)
                oldPrice = 0
                discount = 0
            
            tmp_product['id'] = productID
            tmp_product['name'] = functions.filterName(name,productID)
            tmp_product['oldPrice'] = oldPrice
            tmp_product['newPrice'] = newPrice
            tmp_product['discount'] = discount
            tmp_product['url'] = 'https://Nureh.pk'+  url
            tmp_product['imageUrl'] = 'https:' + imageUrl
            tmp_product['category'] =  category
            tmp_product['subCategory'] = subCategory
            tmp_product['subSubCategory'] = subSubCategory
            tmp_product['piece'] = piece
            products.append(tmp_product)             
           
    except Exception as e:
            with open("errors/error_Nureh.json", "a") as f:
                    error_log = {
                    "datetime": datetime.datetime.now().isoformat(),
                    "exception_message": str(e),
                    "pageURL": pageURL
                    }
                    json.dump(error_log, f)    
 
    return products


def getNurehProductDetails(product):
    try:
        html = functions.getRequest(product["url"], 'text')
        soup = BeautifulSoup(html, "html.parser")
        
        with open("output.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())

        
        availableSizes = []
        availableColors = []    
        productDescription = ''
        secondaryImages = []

        productDescription = str(soup.find('div',{'class':'t4s-product__description'}))

        #Size
        try:
            Element = soup.find_all('div',{'class':'t4s-swatch__list'})
            sizeElement = Element[0]
            for size in sizeElement:
                availableSizes.append(size.text.strip())
        except:
            availableSizes = []

        #Color
        try:
            colorElement = soup.find('div',{'class':'t4s-swatch__option is-t4s-name__color'}).find_all('div',{'class':'t4s-swatch__item'})
            for color in colorElement:
                availableColors.append(color.text.strip())
        except:
            availableColors = []


        mainContainer = soup.find('div',{'class':'t4s-col-md-6 t4s-col-12 t4s-col-item t4s-product__media-wrapper'})
        secondaryImagesDiv = mainContainer.find_all('img', {'class','t4s-img-noscript'})
        
        for img in secondaryImagesDiv:
            if img is not None:
                if 'src' in img.attrs:
                    img_url = img["src"]
                    secondaryImages.append('https:' + img_url)

        secondaryImages= list(set(secondaryImages))
        # secondaryImages = [image for image in secondaryImages if image != product['imageUrl']]
        productDescription = functions.filterDescription(productDescription)
        availableSizes = functions.sortSizes('Nureh', availableSizes)
        availableColors = functions.sortColors('Nureh', availableColors)
        
        print(product["url"],productDescription,availableSizes,availableColors,secondaryImages[:4])
        
        product['name'] = product['subSubCategory'] + " " + product['name']
        product['Description'] = productDescription
        product['Sizes'] = availableSizes
        product['Colors'] = availableColors
        product['secondaryImages'] = secondaryImages[:4]
        product['sizeColors'] = functions.crossJoin(availableSizes,availableColors)


    except Exception as e:
        print ("An Error Occured While Getting The Product Details")
        print(str(e))
        with open("errors/error_Nureh.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
                }
            json.dump(error_log, f)  
    return product
