import json
from bs4 import BeautifulSoup
import math
import os
import datetime
import config
import functions
import random

def getProducts(soup, category, subCategory, subSubCategory, pageURL):
    products = []
    mainContainer = soup.find('ul', {'id': 'product-grid'})
    if mainContainer:
        productsDiv = mainContainer.find_all('li',{'class': 'grid__item'})
    
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
                'pageUrl': pageURL,
                'views' : 0,
                'likes' : 0,
                'shares' : 0,
                'favourites' : 0,
                'list' : 0,
                'keywords': []
            }
            try:
                productID = i.find('div',{'class':'card'})['data-product-id']
            except:
                print('Product ID not found')
                continue;
            try:
                name = i.find('h3').text.strip()
                url = i.find('div',{'class':'card__inner'}).find('a')['href']
                imageUrl = i.find('img',{'class','motion-reduce'})['src']
                try:
                    oldPrice = i.find('span', {'class': 'price-item price-item--regular'}).text.strip()
                    newPrice = i.find('span', {'class': 'price-item price-item--sale'}).text.strip()            
                    discount =  i.find('div',{'class':'ctm-sale-label'}).text.strip()
                except:
                    newPrice = i.find('span', {'class': 'price-item price-item--regular'}).text.strip() 
                    oldPrice =0
                    discount =0
                
                tmp_product['productID'] = productID
                tmp_product['name'] = functions.filterName(name,productID)
                tmp_product['oldPrice'] = functions.extractInt(oldPrice)
                tmp_product['newPrice'] = functions.extractInt(newPrice)
                tmp_product['discount'] = functions.extractInt(discount) 
                tmp_product['url'] =  'https://beechtree.pk' + url
                tmp_product['imageUrl'] = 'https:' + imageUrl 
                tmp_product['category'] =  category
                tmp_product['subCategory'] = subCategory
                tmp_product['subSubCategory'] = subSubCategory
                
                products.append(tmp_product) 
            except Exception as e:
                with open("errors/error_BeechTree.json", "a") as f:
                    error_log = {
                    "datetime": datetime.datetime.now().isoformat(),
                    "product_name": str(name),
                    "exception_message": str(e),
                    "pageURL number": pageURL
                    }
                    json.dump(error_log, f)
    return products


def getBeechTreeProductDetails(product):
    try:
        html = functions.getRequest(product["url"], 'text')
        soup = BeautifulSoup(html, "html.parser")
        
        with open("output.html", "w", encoding="utf-8") as f:
             f.write(soup.prettify())
           
        availableSizes = []
        availableColors = []
        secondaryImages = []

        sizeElement = soup.find_all('div', {'class': 'variant__input'})
        for size in sizeElement:
            availableSizes.append(size.text.strip())

        colorElement = soup.find_all('input', {'name': 'Color'})
        for color in colorElement:
            availableColors.append(color['value'])

        productDescription= str(soup.find('div', {'class': 'description_accordion'}))

        availableSizes = list(set(availableSizes))

        mainContainer = soup.find('ul',{'class':'product__media-list'})
        secondaryImagesDiv = mainContainer.find_all('li')
        
        for img in secondaryImagesDiv:
            img = img.find('img')
            # print(img)
            if 'src' in img.attrs:
                    # print(img["data-src"])
                    img_url = img["src"].replace('width=1946', 'width=533')
                    secondaryImages.append('https:' + img_url)
        secondaryImages= list(set(secondaryImages))
        # secondaryImages = [image for image in secondaryImages if image != product['imageUrl']]
        productDescription = functions.filterDescription(productDescription)
        availableSizes = functions.sortSizes('BeechTree',availableSizes)
        availableColors = functions.sortColors("BeechTree",availableColors)

        product['Description'] = productDescription
        product['Sizes'] = availableSizes
        product['Colors'] = availableColors
        product['secondaryImages'] = secondaryImages[:4]
        product['sizeColors'] = functions.crossJoin(availableSizes,availableColors)
        
        print(product["url"],productDescription,availableSizes,availableColors,secondaryImages[:4])

        
    except Exception as e:
        print ("An Error Occured While Getting The Product Details")
        print(str(e))
        with open("errors/error_BeechTree.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
                }
            json.dump(error_log, f)  
    return product  