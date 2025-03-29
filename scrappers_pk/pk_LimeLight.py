import json
from bs4 import BeautifulSoup
import math
import os
import datetime
import config
import functions

def getProducts(soup, category, subCategory, subSubCategory,piece, pageURL):
    products = []
            
    div = soup.find('div', {'class': 'collection'})
    ul = div.find('ul', {'class': 'product-grid'})
    try:
        items = ul.findAll('li', {'class': 'grid__item'})
        for i in items:
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
            
            # Get product ID from URL
            product_link = i.find('a', {'class': 'full-unstyled-link'})
            if product_link:
                productID = product_link['href'].split('/')[-1]
                tmp_product['productID'] = productID
                
                # Get product URL
                url = 'https://www.limelight.pk' + product_link['href']
                tmp_product['url'] = url

            # Get product name
            name_element = i.find('h3', {'class': 'card__heading'}) or i.find('h3', {'class': 'card__heading h5'})
            if name_element:
                name = name_element.text.strip()
                tmp_product['name'] = functions.filterName(name, productID) if 'productID' in locals() else name

            # Get prices
            price_container = i.find('div', {'class': 'price__container'})
            if price_container:
                price_items = price_container.findAll('span', {'class': 'money'})
                if len(price_items) >= 2:
                    # There's a sale price
                    oldPrice = price_items[0].text.strip().split(' ')[1].replace(',','')
                    newPrice = price_items[1].text.strip().split(' ')[1].replace(',','')
                    discount = round((float(oldPrice) - float(newPrice)) / float(oldPrice) * 100)
                else:
                    # No sale, just regular price
                    newPrice = price_items[0].text.strip().split(' ')[1].replace(',','')
                    oldPrice = newPrice
                    discount = 0
                
                tmp_product['oldPrice'] = functions.extractInt(oldPrice)
                tmp_product['newPrice'] = functions.extractInt(newPrice)
                tmp_product['discount'] = functions.extractInt(discount)

            # Get image URL
            img = i.find('img', {'class': 'motion-reduce'})
            if img:
                imageUrl = 'https:' + img['src']
                imageUrl = imageUrl.replace('330x','1000x')
                tmp_product['imageUrl'] = imageUrl

            # Set categories
            tmp_product['category'] = category
            tmp_product['subCategory'] = subCategory
            tmp_product['subSubCategory'] = subSubCategory
            tmp_product['piece'] = piece
            
            products.append(tmp_product)
            
    except Exception as e:
        with open("errors/error_LimeLight.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(name),
                "exception_message": str(e),
                "pageURL": pageURL
            }
            json.dump(error_log, f)
            f.write('\n')  # Add newline for better readability in log file

    return products

def getLimeLightProductDetails(product):
    try:
        html = functions.getRequest(product["url"], 'text')
        soup = BeautifulSoup(html, "html.parser")
        
        with open("output_L.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())

        secondaryImages = []
        availableSizes = []
        availableColors = [] 
             
        productDescription = ''
        productDescription = str(soup.find('div', {'class':'product-des-main'}))

        #Size
        try:
            sizeElement = soup.find('fieldset',{'class':'product-size-btns'}).find_all('label')
            for size in sizeElement:
                availableSizes.append(size.text.strip())
        except:
            availableSizes = []

        # other colors / complete your look
        try:
            # otherColorLink = soup.find('div',{'class':'color-look-main'}).find('a',{'class':'full-unstyled-link'})[href]
            colorElement = soup.find('div',{'class':'color-look-main'}).find_all('div',{'class':'card-wrapper'})
            for color in colorElement:
                availableColors.append(color['data-color-variants'])
        except:
            try:
                # otherColorLink = soup.find('div',{'class':'swiper-slide grid__item complete-look-item swiper-slide-active'}).find('a',{'class':'full-unstyled-link'})[href]
                colorElement = soup.find('div',{'class':'swiper-slide grid__item complete-look-item swiper-slide-active'}).find_all('div',{'class':'card-wrapper'})
                for color in colorElement:
                    availableColors.append(color['data-color-variants'])
            except:
                availableColors = []

                

        #mainContainer = soup.find('div',{'class':'product-secondary-imgs'})
        #secondaryImagesDiv = mainContainer.find_all('img')
        
        # for img in secondaryImagesDiv:
        #     if img is not None:
        #         if 'src' in img.attrs:
        #             img_url = img["src"]
        #             img_url = img_url.replace('120x', '900x')
        #             secondaryImages.append('https:' + img_url)

        # secondaryImages[0]= product['imageUrl']
        # secondaryImages= list(set(secondaryImages))
        # secondaryImages = [image for image in secondaryImages if image != product['imageUrl']]
        productDescription = functions.filterDescription(productDescription)
        availableSizes = functions.sortSizes('LimeLight', availableSizes)
        availableColors = functions.sortColors('LimeLight', availableColors)
        
        print(product["url"],availableSizes,availableColors,secondaryImages)


        product['Description'] = productDescription
        product['Sizes'] = availableSizes
        product['Colors'] = availableColors
        product['secondaryImages'] = secondaryImages
        product['sizeColors'] = functions.crossJoin(availableSizes,availableColors)


    except Exception as e:
        print ("An Error Occured While Getting The Product Details")
        print(str(e))
        with open("errors/error_LimeLight.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
                }
            json.dump(error_log, f)  
    return product
