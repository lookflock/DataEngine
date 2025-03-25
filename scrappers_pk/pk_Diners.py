import json
from bs4 import BeautifulSoup
import math
import os
import datetime
import re
import config
import functions


def getProducts(soup, category, subCategory, subSubCategory, pageURL):
    
    products = []
    #with open("output.html", "w", encoding="utf-8") as file:
    #  file.write(soup.prettify())
    mainContainer = soup.find('div',{'class': 'collection'})
    productsDiv = mainContainer.find_all('li', {'class': 'product'})  
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
                'pageUrl': pageURL,
                'views' : 0,
                'likes' : 0,
                'shares' : 0,
                'favourites' : 0,
                'list' : 0,
                'keywords': []
            }
            name = product.find('a',{'class','card-title'}).find('span', {'class','text'}).text.strip()
            url = product.find('a',{'class','card-link'})['href']
            try:
                # imageUrl = product.find_all('img', {'class','motion-reduce lazyload'}).split(' ')[0]
                imageUrl = product.find('img', {"class","motion-reduce lazyload"})["data-srcset"].split(' ')[0]
                imageUrl = imageUrl.replace('165x','1000x')
                productID = url.split('/')[-1]
                try:           
                    oldPrice = product.find('span',{'class','price-item price-item--regular'}).text.strip()
                    oldPrice = functions.extractInt(oldPrice)
                    newPrice = product.find('span',{'class','price-item price-item--sale'}).text.strip()
                    newPrice = functions.extractInt(newPrice)
                    discount = math.ceil((oldPrice - newPrice) / oldPrice * 100)
                    if discount == 0:
                        oldPrice = 0
                except:
                    newPrice = product.find('span',{'class','price-item price-item--regular'}).text.strip()
                    newPrice = functions.extractInt(newPrice)
                    oldPrice = 0
                    discount = 0
            
                tmp_product['productID'] = productID
                tmp_product['name'] = functions.filterName(name,productID)
                tmp_product['oldPrice'] = oldPrice
                tmp_product['newPrice'] = newPrice
                tmp_product['discount'] = discount
                tmp_product['url'] = 'https://diners.com.pk'+  url
                tmp_product['imageUrl'] = 'https:' + imageUrl
                tmp_product['category'] =  category
                tmp_product['subCategory'] = subCategory
                tmp_product['subSubCategory'] = subSubCategory
                #print(tmp_product)
                products.append(tmp_product) 
            
               
            except Exception as e:
                with open("errors/error_Diners.json", "a") as f:
                    error_log = {
                    "datetime": datetime.datetime.now().isoformat(),
                    "product_name": str(name),
                    "exception_message": str(e),
                    "pageURL number": pageURL
                    }
                    json.dump(error_log, f)    
 
    return products


def getDinersProductDetails(product):
    try:
        html = functions.getRequest(product["url"], 'text')
        soup = BeautifulSoup(html, "html.parser")
        
        with open("output.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())


        availableSizes = []
        availableColors = []
        secondaryImages = []
        # Element = soup.find_all('div', {'class': 'swatch clearfix'})
        # sizeElement = Element[1]
        # colorElement = Element[0]
        try:
            sizeElement = soup.find('div',{'class':'productView-options'}).find_all('span',{'class':'text'})
            for size in sizeElement:
                availableSizes.append(size.text.strip())
        except:
            availableSizes = []

        try:
            colorElement = colorElement.find_all('div',{'class':'swatch-element'})
            for color in colorElement:
                availableColors.append(color.text.strip())
        except:
            SKUcolor = soup.find('div',{'class','productView-info-item'}).find_all('span')[1].text.strip().split('-')[-1]
            availableColors.append(SKUcolor)


        productDescription= soup.find('div', {'id': 'tab-product-detail-mobile'})
        productDescription = str(productDescription)        
        
        mainContainer = soup.find('div',{'class':'productView-image-wrapper'})
        secondaryImagesDiv = mainContainer.find_all('img')
        
        for img in secondaryImagesDiv:
            if img is not None:
                if 'src' in img.attrs:
                    img_url = img["src"]
                    secondaryImages.append('https:' + img_url)

        secondaryImages= list(set(secondaryImages))
        # secondaryImages = [image for image in secondaryImages if image != product['imageUrl']]
        productDescription = functions.filterDescription(productDescription)
        availableSizes = functions.sortSizes('Diners',availableSizes)
        availableColors = functions.sortColors('Diners',availableColors)
        
        print(product["url"],productDescription,availableSizes,availableColors,secondaryImages[:4])


        product['Description'] = productDescription
        product['Sizes'] = availableSizes
        product['Colors'] = availableColors
        product['secondaryImages'] = secondaryImages[:4]
        product['sizeColors'] = functions.crossJoin(availableSizes,availableColors)





    except Exception as e:
        print ("An Error Occured While Getting The Product Details")
        print(str(e))
        with open("errors/error_Diners.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
                }
            json.dump(error_log, f)  
    return product              