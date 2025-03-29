import json
from bs4 import BeautifulSoup
import datetime
import math
import os
import random
import functions


def getProducts(soup, category, subCategory, subSubCategory, pageURL):
    products = []
    try:
        mainContainer = soup.find('ul', {'class': 'productListing'})
        productsDiv = mainContainer.find_all('li',{'class': 'product'})
    except:
        print('No products found')
        return products
    
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
                'page': pageURL,
                'views' : 0,
                'likes' : 0,
                'shares' : 0,
                'favourites' : 0,
                'list' : 0,
                'keywords': []
            }
        
        
        nameDiv = product.find('a', {'class': 'card-title'})
        name = nameDiv.find('span',{'class':'text'}).text.strip()
        # print("Name: ",name)
        try:    
            url = nameDiv['href']
            # print("URL: ",url)
            productID = product.find('div',{'class','product-item'})['data-product-id']
            # print("Product ID: ",productID)
            imageUrl = product.find('img',{'class','motion-reduce lazyload'})['data-srcset'].split(" ")[0]
            imageUrl = imageUrl.replace('_165x', '_1000x')
            # print("Image URL: ",imageUrl)
            try:
                oldPrice = product.find('s', class_='price-item price-item--regular').text.strip()
                oldPrice = functions.extractInt(oldPrice)
                newPrice = product.find('span', class_='price-item price-item--sale').text.strip()
                newPrice = functions.extractInt(newPrice)
                discount = math.ceil((oldPrice - newPrice) / oldPrice * 100)
            except:
                newPrice = product.find('div', class_='price').text.strip()
                newPrice = functions.extractInt(newPrice)
                oldPrice = 0
                discount = 0
            
            tmp_product['productID'] = productID
            tmp_product['name'] = functions.filterName(name,productID)
            tmp_product['oldPrice'] = int(oldPrice)
            tmp_product['newPrice'] = int(newPrice)
            tmp_product['discount'] = int(discount)
            tmp_product['url'] =  'https://dhanak.com.pk' + url
            tmp_product['imageUrl'] = "https:" + imageUrl 
            tmp_product['category'] =  category
            tmp_product['subCategory'] = subCategory
            tmp_product['subSubCategory'] = subSubCategory
            # print(json.dumps(tmp_product, indent=4 ,ensure_ascii=False))
            products.append(tmp_product)    

        except Exception as e:
            with open("errors/error_Dhanak.json", "a") as f:
                error_log = {
                    "datetime": datetime.datetime.now().isoformat(),
                    "product_name": str(name),
                    "exception_message": str(e),
                    "pageURL number": pageURL
                    }
                json.dump(error_log, f)
       
    return products


def getDhanakProductDetails(product):  
    try:
        html = functions.getRequest(product["url"], 'text')
        soup = BeautifulSoup(html, "html.parser")
        
        with open("output.html", "w", encoding="utf-8") as f:
             f.write(soup.prettify())
        
        availableSizes = []
        availableColors = []
        secondaryImages = []
        # Extracting available sizes,colors and description
        try:
            sizeElements = soup.find('fieldset',{'class','js product-form__input clearfix'}).find_all('input',{'class','product-form__radio'})
            for element in sizeElements:
                availableSizes.append(element['value'])
        except:
            availableSizes = []


        try:
            colorElement = soup.find('span',{'class','productView-info-value'}).text.strip().split(' ')[-1]
            availableColors.append(colorElement)
            # print(availableSizes)

        except:
            availableColors = []
        productDescription= str(soup.find('div', {'id': 'tab-description'}).find('div',{'class','tab-popup-content'}).find('p'))

        
        # to include the table
        # productDescription += str(soup.find('div', {'class': 'collapsible-content__inner rte'}))

        mainContainer = soup.find_all('div',{'class','productView-thumbnail'})
        # secondaryImagesDiv = mainContainer.find('img')
        # print(secondaryImagesDiv)
        for img in mainContainer:
            img = img.find('img')
            # print(img)
            if 'src' in img.attrs:
                    # print(img["data-src"])
                    img_url = img["src"]
                    img_url = img_url.replace('_large','_1000x')
                    secondaryImages.append('https:' + img_url)

        secondaryImages= list(set(secondaryImages))
        # secondaryImages = [image for image in secondaryImages if image != product['imageUrl']]
        availableColors= list(set(availableColors))

        productDescription = functions.filterDescription(productDescription)
        availableSizes = functions.sortSizes('Dhanak',availableSizes)
        availableColors = functions.sortColors('Dhanak',availableColors)


        print(product["url"],productDescription,availableSizes,availableColors,secondaryImages[:4])

        product['Description'] = productDescription
        product['Sizes'] = availableSizes
        product['Colors'] = availableColors
        product['secondaryImages'] = secondaryImages[:4]
        product['sizeColors'] = functions.crossJoin(availableSizes,availableColors)

    except Exception as e:
        print ("An Error Occured While Getting The Product Details")
        print(product["url"],str(e))
        with open("errors/error_AnamAkhlaq.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
                }
            json.dump(error_log, f)  
    return product