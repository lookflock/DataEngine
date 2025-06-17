import json
from bs4 import BeautifulSoup
import math
import datetime
import re
import functions
from urllib.parse import urlparse, urlunparse
import requests
        

supplier='Deepakperwani'


import math
import json
import datetime
from bs4 import BeautifulSoup

def getProducts(soup, category, subCategory, subSubCategory, piece, pageURL):
    products = []
    
    try:
        mainContainer = soup.find('div', {'class': 'item-grid'})
        productsDiv = mainContainer.find_all('div', {'class': 'item-box'})
    except:
        return products

    for i in productsDiv:
        tmp_product = {
                'supplier': supplier,
                'id': '',
                'name': '',
                'oldPrice': 0,
                'newPrice': 0,
                'discount': 0,
                'category': category,
                'subCategory': subCategory,
                'subSubCategory': subSubCategory,
                'url': '',
                'imageUrl': '',
                'page': pageURL,
                'views' : 0,
                'likes' : 0,
                'shares' : 0,
                'favourites' : 0,
                'status' : 1,
                'list' : 0,
                'keywords': [],
                'piece': piece,
                'valid': 1
            }

        try:
            nameDiv = i.find('div', {'class': 'picture'})
            detailsDiv = i.find('div', {'class': 'details'})

            name = detailsDiv.find('h2', {'class': 'product-title'}).text.strip()
            url = nameDiv.find('a')['href']
            productID = i.find('div', {'class': 'product-item'})['data-productid']

            # Use main image (not hover)
            imageUrl = nameDiv.find('img', {'class': 'lazyload'})['data-src']
            imageUrl = imageUrl.replace('600.', '1000.')
            
            # Pricing logic
            try:
                oldPrice = detailsDiv.find('span', class_='price actual-price').text.strip()
                oldPrice = functions.extractInt(oldPrice)
                newPriceEl = detailsDiv.find('span', class_='price sale-price')
                if newPriceEl:
                    newPrice = functions.extractInt(newPriceEl.text.strip())
                else:
                    newPrice = oldPrice
                discount = math.ceil((oldPrice - newPrice) / oldPrice * 100) if oldPrice > newPrice else 0
            except:
                priceText = detailsDiv.find('span', class_='price').text.strip()
                newPrice = functions.extractInt(priceText)
                oldPrice = 0
                discount = 0

            tmp_product['id'] = productID
            tmp_product['name'] = functions.filterName(name, productID)
            tmp_product['oldPrice'] = oldPrice
            tmp_product['newPrice'] = newPrice
            tmp_product['discount'] = discount
            tmp_product['url'] = 'https://www.deepakperwani.com' + url
            tmp_product['imageUrl'] = normalize_image_url(imageUrl) if imageUrl.startswith('http') else 'https:' + normalize_image_url(imageUrl)
            # tmp_product=getDeepakperwaniProductDetails(tmp_product)
            products.append(tmp_product)

        except Exception as e:
            with open("errors/error_DeepakPerwani.json", "a") as f:
                error_log = {
                    "datetime": datetime.datetime.now().isoformat(),
                    "product_name": str(name) if 'name' in locals() else 'N/A',
                    "exception_message": str(e),
                    "pageURL": pageURL
                }
                json.dump(error_log, f)
                f.write(",\n")  # append comma for valid JSON array format

    return products


def normalize_image_url(url):
    parsed = urlparse(url)
    path = parsed.path
    path = re.sub(r'(_\d+x)?(\.\w+)$', r'\2', path)  # remove _360x, _720x, etc.
    return urlunparse(parsed._replace(path=path, query=""))


def getDeepakperwaniProductDetails(product):
    print(f"[Product Details] Extracting Details for Product id: {product['id']}")
    try:
        html = functions.getRequest(product["url"], 'text')
        soup = BeautifulSoup(html, "html.parser")
        
        # with open("output_generate.html", "w", encoding="utf-8") as f:
        #      f.write(soup.prettify())
        
        availableSizes = []
        secondaryImages = []

        # -----------------------
        # Get Sizes
        # -----------------------
        try:
            sizeElements = soup.find('ul',{'class','option-list'}).find_all('li')
            for element in sizeElements:
                availableSizes.append(element.text.strip())
            availableSizes = functions.sortSizes('Cambridge', availableSizes)
        except:
            availableSizes = []

        # Get Secondary Images
        # -----------------------
        mainContainer = soup.find('div',{'class','thumb-holder'})
        secondaryImagesDiv = mainContainer.find_all('img')
        main_image = product.get("imageUrl")
        for img in secondaryImagesDiv:
            # img = img.find('a')
            # print(img)
            if 'data-src' in img.attrs:
                    # print(img["data-src"])
                    img_url = img["data-src"]
                    img_url = img_url.replace('_200','_1000')
                    if img_url:
                        if img_url.startswith('//'):
                            img_url = 'https:' + img_url
                        elif img_url.startswith('/'):
                            img_url = 'https://www.deepakperwani.com' + img_url

                        parsed_url = urlparse(img_url)
                        cleaned_url = urlunparse(parsed_url._replace(query=""))

                        # Skip if this is the same as the main image
                        if main_image:
                            normalized_main = normalize_image_url(main_image)
                            normalized_secondary = normalize_image_url(cleaned_url)

                            if normalized_main == normalized_secondary:
                                continue
                            
                        # Verify and add
                        try:
                            print(f"[Product Details] Verifying Secondary Images for Product id: {product['id']}")
                            response = requests.head(cleaned_url, timeout=5)
                            if response.status_code == 200:
                                secondaryImages.append(cleaned_url)
                            else:
                                print(f"[image check] Invalid image (status {response.status_code}): {cleaned_url}")
                        except Exception as e:
                            print(f"[image check] Failed to verify image: {cleaned_url} — {e}")

        # Finalize
        secondaryImages = list(set(secondaryImages))
        product['secondaryImages'] = secondaryImages
        product['sizes'] = availableSizes

    except Exception as e:
        print("An Error Occurred While Getting The Product Details")
        print(str(e))

        with open("errors/error_DeepakPerwani.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
            }
            json.dump(error_log, f)
            f.write(',')

    return product

# def getProducts(soup, category, subCategory, subSubCategory, page):
# def getProducts(soup, category, subCategory, subSubCategory,piece, pageURL):

#     products = []
#     try:
#         mainContainer = soup.find('div', {'class': 'item-grid'})
#         productsDiv = mainContainer.find_all('div',{'class': 'item-box'})

#     except:
#         return products

#     with open("output.html", "w", encoding="utf-8") as f:
#            f.write(soup.prettify())
    
#     for i in productsDiv:
#         tmp_product = {
#                 'productID': '',
#                 'name': '',
#                 'oldPrice': '',
#                 'newPrice': '',
#                 'discount': '',
#                 'category': '',
#                 'subCategory': '',
#                 'subSubCategory': '',
#                 'url': '',
#                 'imageUrl': '',
#                 'views' : 0,
#                 'likes' : 0,
#                 'shares' : 0,
#                 'favourites' : 0,
#                 'list' : 0,
#                 'keywords': [],
#                 'piece': ''
#             }
        
        
#         nameDiv = i.find('div', {'class': 'picture'})
#         name = i.find('h2',{'class','product-title'}).text.strip()
#         try:    
#             url = nameDiv.find('a')['href']
#             productID = url.split("/")[-1]
#             imageUrl = nameDiv.find('img',{'class','lazyload'})['data-src']
#             # imageUrl = i.find('div', {'class': 'grid_img wow zoomIn lazyload primary'})['data-bgset'].split(" ")[0]
#             imageUrl = imageUrl.replace('600.', '1000.')
#             try:
#                 oldPrice = i.find('span', class_='price actual-price').text.strip()
#                 oldPrice = functions.extractInt(oldPrice)
#                 newPrice = i.find('span', class_='price sale-price').text.strip()
#                 newPrice = functions.extractInt(newPrice)
#                 discount = math.ceil((oldPrice - newPrice) / oldPrice * 100)
#             except:
#                 newPrice = i.find('span', class_='price').text.strip()
#                 newPrice = functions.extractInt(newPrice)
#                 oldPrice = 0
#                 discount = 0
            
#             tmp_product['id'] = productID
#             # tmp_product['name'] = name
#             tmp_product['name'] = functions.filterName(name,productID)
#             tmp_product['oldPrice'] = int(oldPrice)
#             tmp_product['newPrice'] = int(newPrice)
#             tmp_product['discount'] = int(discount)
#             tmp_product['url'] =  'https://deepakperwani.com' + url
#             tmp_product['imageUrl'] = imageUrl 
#             tmp_product['category'] =  category
#             tmp_product['subCategory'] = subCategory
#             tmp_product['subSubCategory'] = subSubCategory
#             # print(tmp_product)
#             products.append(tmp_product)    

#         except Exception as e:
#             with open("errors/error_Deepakperwani.json", "a") as f:
#                 error_log = {
#                     "datetime": datetime.datetime.now().isoformat(),
#                     "product_name": str(name),
#                     "exception_message": str(e),
#                     "page number": page
#                     }
#                 json.dump(error_log, f)
       
#     return products
