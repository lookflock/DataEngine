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
    mainContainer = soup.find('div', {'class':'productList'})
    try:
        productsDiv = mainContainer.find_all('div', {'class':'gitem'})
    except:
        productsDiv = mainContainer.find_all('div', {'class':'changestyle gitem'})
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

            nameDiv  = i.find('a', class_='grid-view-item__title')
            name = nameDiv.text.strip()
            try:
                url = nameDiv['href']
                productID = re.search(r'/products/([^"]+)', url).group(1)
                productID = productID.split("-")[-3]
                imageUrl = i.find('div',{'class':'swiper-slide'}).find('img')['src']
                # imageUrl = imageUrl.replace('150x', '1000x')
                # print(imageUrl)
                try:
                    oldPrice = i.find('s', class_='pr_price regular').text.strip()
                    oldPrice = functions.extractInt(oldPrice)
                    newPrice = i.find('span', class_='pr_price sale').text.strip()
                    newPrice =functions.extractInt(newPrice)
                    discount = math.ceil((oldPrice - newPrice) / oldPrice * 100)
                except:
                    newPrice = i.find('span',{'class','pr_price'}).text.strip()
                    newPrice =functions.extractInt(newPrice)
                    oldPrice = 0
                    discount = 0
            
            
                tmp_product['productID'] = productID.upper()
                tmp_product['name'] = functions.filterName(name,tmp_product['productID'])
                tmp_product['oldPrice'] = oldPrice
                tmp_product['newPrice'] = newPrice
                tmp_product['discount'] = discount
                tmp_product['url'] = 'https://wearego.com'+  url
                tmp_product['imageUrl'] = 'https:' + imageUrl 
                tmp_product['category'] =  category
                tmp_product['subCategory'] = subCategory
                tmp_product['subSubCategory'] = subSubCategory
                tmp_product['piece'] = piece
                
                products.append(tmp_product) 

            except Exception as e:
                with open("errors/error_Ego.json", "a") as f:
                    error_log = {
                    "datetime": datetime.datetime.now().isoformat(),
                    "product_name": str(name),
                    "exception_message": str(e),
                    "pageURL": pageURL
                    }
                    json.dump(error_log, f)    

    return products

def getEgoProductDetails(product): 
    try:
        html = functions.getRequest(product["url"], 'text')
        soup = BeautifulSoup(html, "html.parser")
        
        #with open("output.html", "w", encoding="utf-8") as f:
        #    f.write(soup.prettify())

        
        availableSizes = []
        availableColors = []
        secondaryImages = []

        sizeElement = soup.find('div',{'class':'product-form'}).find_all('div',{'class':'swatch-element'})
        for size in sizeElement:
            availableSizes.append(size.text.strip())

        productDescription= str(soup.find('div', {'class': 'product-single__description rte'}))
        
        mainContainer = soup.find('div',{'class':'pr_thumbs'})
        secondaryImagesDiv = mainContainer.find_all('div',{'class','pr_thumbs_item'})
        
        for img in secondaryImagesDiv:
            img = img.find('a')
            if img is not None:
                if 'href' in img.attrs:
                    img_url = img["href"].replace('_50x','_1000x')
                    secondaryImages.append('https:' + img_url)

        secondaryImages= list(set(secondaryImages))
        # secondaryImages = [image for image in secondaryImages if image != product['imageUrl']]
        productDescription = functions.filterDescription(productDescription)
        availableSizes = functions.sortSizes('Ego',availableSizes)
        availableColors = functions.sortColors('Ego',availableColors)

        
        print(product["url"],productDescription,availableSizes,availableColors,secondaryImages[:4])


        product['Description'] = productDescription
        product['Sizes'] = availableSizes
        product['Colors'] = availableColors
        product['secondaryImages'] = secondaryImages[:4]
        product['sizeColors'] = functions.crossJoin(availableSizes,availableColors)

    except Exception as e:
        print ("An Error Occured While Getting The Product Details")
        print(str(e))
        with open("errors/error_Ego.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
                }
            json.dump(error_log, f)  
    return product              