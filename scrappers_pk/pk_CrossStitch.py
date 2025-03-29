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
    mainContainer = soup.find('div',{'class': 'full-wrapper'})
    productsDiv = mainContainer.find_all('div', {'class': 'grid-view-item product-card'})
   
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

            linkdiv = i.find('a', {'class','grid-view-item__link'})
            name = linkdiv.text.strip()
            url = linkdiv['href']      
            try:
                imageUrl = i.find('img', {'class','grid-view-item__image'})['data-src']
                url_parts = imageUrl.split('/')
                productID = url_parts[-1].split('_')[-1].split('=')[1]
                imageUrl = imageUrl.replace('{width}', '1000')
                try:
                    oldPrice = i.find('s',{'class','price-item price-item--regular'}).find('span',{'class','money'}).text.strip()
                    oldPrice = functions.extractInt(oldPrice)
                    newPrice = i.find('span',{'class','price-item price-item--sale'}).find('span',{'class','money'}).text.strip()
                    newPrice =functions.extractInt(newPrice)
                    discount = math.ceil((oldPrice - newPrice) / oldPrice * 100)
                    if discount == 0:
                        oldPrice = 0
                except:
                    newPrice = i.find('span',{'class','spf-product-card__price'}).find('span',{'class','money'}).text.strip()
                    newPrice =functions.extractInt(newPrice)
                    oldPrice = 0
                    discount = 0
            
                tmp_product['productID'] = productID
                tmp_product['name'] = functions.filterName(name,productID)
                tmp_product['oldPrice'] = oldPrice
                tmp_product['newPrice'] = newPrice
                tmp_product['discount'] = discount
                tmp_product['url'] = 'https://crossstitch.pk'+  url
                tmp_product['imageUrl'] = 'https:' + imageUrl
                tmp_product['category'] =  category
                tmp_product['subCategory'] = subCategory
                tmp_product['subSubCategory'] = subSubCategory
                tmp_product['piece'] = piece
                
                products.append(tmp_product) 

            except Exception as e:
                with open("errors/error_CrossStitch.json", "a") as f:
                    error_log = {
                    "datetime": datetime.datetime.now().isoformat(),
                    "product_name": str(name),
                    "exception_message": str(e),
                    "pageURL": pageURL
                    }
                    json.dump(error_log, f)    
 
    return products


def getCrossStitchProductDetails(product) :
    try:
        html = functions.getRequest(product["url"], 'text')
        soup = BeautifulSoup(html, "html.parser")
        
        with open("output.html", "w", encoding="utf-8") as f:
             f.write(soup.prettify())


        availableSizes = []
        availableColors = []
        secondaryImages = []
        Element = soup.find_all('div', {'class': 'swatch clearfix'})
        try:
            sizeElement = Element[1]
            sizeElement = sizeElement.find_all('div',{'class':'swatch-element'})
            for size in sizeElement:
                availableSizes.append(size.text.strip())
        except:
            availableSizes = []
        
        try: 
            colorElement = Element[0]
            colorElement = colorElement.find_all('div',{'class':'swatch-element'})
            for color in colorElement:
                availableColors.append(color.text.strip())
        except:
            availableColors = []

        productDescription= str(soup.find('div', {'class': 'fulldescription'}))

        mainContainer = soup.find('div',{'class':'MagicToolboxSelectorsContainer'})
        secondaryImagesDiv = mainContainer.find_all('img')
        
        for img in secondaryImagesDiv:
            if img is not None:
                if 'src' in img.attrs:
                    img_url = img["src"].replace('_medium','_1000x')
                    secondaryImages.append('https:' + img_url)

        secondaryImages= list(set(secondaryImages))
        # secondaryImages = [image for image in secondaryImages if image != product['imageUrl']]
        productDescription = functions.filterDescription(productDescription)
        availableSizes = functions.sortSizes('CrossStitch',availableSizes)
        availableColors = functions.sortColors('CrossStitch',availableColors)
        
        print(product["url"],productDescription,availableSizes,availableColors,secondaryImages[:4])


        product['Description'] = productDescription
        product['Sizes'] = availableSizes
        product['Colors'] = availableColors
        product['secondaryImages'] = secondaryImages[:4]
        product['sizeColors'] = functions.crossJoin(availableSizes,availableColors)




    except Exception as e:
        print ("An Error Occured While Getting The Product Details")
        print(product["url"],str(e))
        with open("errors/error_CrossStitch.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
                }
            json.dump(error_log, f)  
    return product            