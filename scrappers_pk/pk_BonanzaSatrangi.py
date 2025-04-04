import json
from bs4 import BeautifulSoup
import math
import os
import datetime
import re
import config
import functions
import random

def getProducts(soup, category, subCategory, subSubCategory, piece, pageURL):
    
    products = []
    mainContainer = soup.find('div', {'class':'sr4-products'})
    try:
        productsDiv = mainContainer.find_all('div', {'class':'sr4-product'})
    except:
        return products

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
                'keywords': [],
                'piece': ''
            }
        with open("output3.html", "w", encoding="utf-8") as f:
            f.write(i.prettify())

        name = i.find('h3',{'class':'sr4-product-title'}).text.strip()
        try:
            url = i.find('h3',{'class':'sr4-product-title'}).find('a')['href']
            Product_id = re.findall( r'\((.*?)\)', name)[0]
            imageUrl = i.find('img', {'class':'sr4-product-main-img lazyloadsr4'})['data-src']
            imageUrl = imageUrl.replace('{width}', '1000')
            try:
                price = i.find('div',{'class':'sr4-product-price'})
                oldPrice = price.find_all('span',{'class':'money'})[0].text.strip()
                oldPrice = functions.extractInt(oldPrice)
                newPrice = price.find_all('span',{'class':'money'})[1].text.strip()
                newPrice =functions.extractInt(newPrice)
                discount = math.ceil((oldPrice - newPrice) / oldPrice * 100)
            except:
                newPrice = i.find('div',{'class':'details'}).find('span', class_='product-price__price').text.strip()
                newPrice = functions.extractInt(newPrice)
                oldPrice = 0
                discount = 0
            
            
            tmp_product['productID'] = Product_id
            tmp_product['name'] = functions.filterName(name,Product_id)
            tmp_product['oldPrice'] = oldPrice
            tmp_product['newPrice'] = newPrice
            tmp_product['discount'] = discount
            tmp_product['url'] = 'https://bonanzasatrangi.com'+  url
            tmp_product['imageUrl'] = 'https:' + imageUrl 
            tmp_product['category'] =  category
            tmp_product['subCategory'] = subCategory
            tmp_product['subSubCategory'] = subSubCategory
            tmp_product['piece'] = piece
            products.append(tmp_product) 

        except Exception as e:
                with open("errors/error_BonanzaSatrangi.json", "a") as f:
                    error_log = {
                    "datetime": datetime.datetime.now().isoformat(),
                    "product_name": str(name),
                    "exception_message": str(e),
                    "pageURL number": pageURL
                    }
                    json.dump(error_log, f)        

         

    return products

def getBonanzaSatrangiProductDetails(product):
    try:
        html = functions.getRequest(product["url"], 'text')
        soup = BeautifulSoup(html, "html.parser")
        
        #with open("output.html", "w", encoding="utf-8") as f:
        #     f.write(soup.prettify())

         
        availableSizes = []
        availableColors = []
        secondaryImages = []
        Element_headertext = soup.find('div', {'class': 'swatch clearfix option2'}).find('label',{'class','header'}).text.strip()
        # print('Text',Element_headertext)
        # print()
        if Element_headertext == 'Color:   Size Chart':
            sizeElement = soup.find('div', {'class': 'swatch clearfix option1'}).find_all('div', {'class': 'swatch-element'})
            for size in sizeElement:
                availableSizes.append(size.text.strip())

            colorElement = soup.find('div', {'class': 'swatch clearfix option2'}).find_all('div', {'class': 'swatch-element'})
            for color in colorElement:
                availableColors.append(color.text.strip())
        
        else:
            availableSizes = []
            colorElement = soup.find('div', {'class': 'swatch clearfix option1'}).find_all('div', {'class': 'swatch-element'})
            for color in colorElement:
                availableColors.append(color.text.strip())

        productDescription= str(soup.find('div', {'class': 'product-description rte'}))



        mainContainer = soup.find('div',{'class':'product-single__thumbnails'})
        secondaryImagesDiv = mainContainer.find_all('div',{'class':'product-single__thumbnails-item'})
        
        for img in secondaryImagesDiv:
            img = img.find('img')
            if img is not None:
                if 'src' in img.attrs:
                    img_url = img["src"].replace('60x','1000x')
                    secondaryImages.append('https:' + img_url)

        secondaryImages= list(set(secondaryImages))
        # secondaryImages = [image for image in secondaryImages if image != product['imageUrl']]
        productDescription = functions.filterDescription(productDescription)
        availableSizes = functions.sortSizes('BonanzaSatrangi',availableSizes)
        availableColors = functions.sortColors("BonanzaSatrangi",availableColors)
        
        print(product["url"],productDescription,availableSizes,availableColors,secondaryImages[:4])


        product['Description'] = productDescription
        product['Sizes'] = availableSizes
        product['Colors'] = availableColors
        product['secondaryImages'] = secondaryImages[:4]
        product['sizeColors'] = functions.crossJoin(availableSizes,availableColors)

 
    except Exception as e:
        print ("An Error Occured While Getting The Product Details")
        print(str(e))
        with open("errors/error_BonanzaSatrangi.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
                }
            json.dump(error_log, f)  
    return product     