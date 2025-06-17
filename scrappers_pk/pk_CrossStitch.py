import json
from bs4 import BeautifulSoup
import math
import datetime
import re
import functions
from urllib.parse import urlparse, urlunparse
import requests
        

supplier='CrossStitch'

def getProducts(soup, category, subCategory, subSubCategory,piece, pageURL):
    
    products = []
    mainContainer = soup.find('div',{'class': 'full-wrapper'})
    productsDiv = mainContainer.find_all('div', {'class': 'grid-view-item product-card'})
   
    for i in productsDiv:            
            tmp_product = {
                'supplier': supplier,
                'id': '',
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
                'status' : 1,
                'list' : 0,
                'keywords': [],
                'piece': '',
                'valid': 1
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
            
                tmp_product['id'] = productID
                tmp_product['name'] = functions.filterName(name,productID)
                tmp_product['oldPrice'] = oldPrice
                tmp_product['newPrice'] = newPrice
                tmp_product['discount'] = discount
                tmp_product['url'] = 'https://crossstitch.pk'+  url
                tmp_product['imageUrl'] = 'https:' + normalize_image_url(imageUrl)
                tmp_product['category'] =  category
                tmp_product['subCategory'] = subCategory
                tmp_product['subSubCategory'] = subSubCategory
                tmp_product['piece'] = piece
                # tmp_product=getCrossStitchProductDetails(tmp_product)
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

def normalize_image_url(url):
    parsed = urlparse(url)
    path = parsed.path
    path = re.sub(r'(_\d+x)?(\.\w+)$', r'\2', path)  # remove _360x, _720x, etc.
    return urlunparse(parsed._replace(path=path, query=""))


def getCrossStitchProductDetails(product):
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
        Element = soup.find_all('div', {'class': 'swatch clearfix'})
        try:
            sizeElement = Element[1]
            sizeElement = sizeElement.find_all('div',{'class':'swatch-element'})
            for size in sizeElement:
                availableSizes.append(size.text.strip())
            availableSizes = functions.sortSizes('Cambridge', availableSizes)

        except:
            availableSizes = []

        # Get Secondary Images
        # -----------------------
        mainContainer = soup.find('div',{'class':'MagicToolboxSelectorsContainer'})
        secondaryImagesDiv = mainContainer.find_all('img')
        main_image = product.get("imageUrl")
        
        for img in secondaryImagesDiv:
            if img is not None:
                if 'src' in img.attrs:
                    img_url = img["src"].replace('_medium','_1000x')
                    if img_url:
                        if img_url.startswith('//'):
                            img_url = 'https:' + img_url
                        elif img_url.startswith('/'):
                            img_url = 'https://www.crossstitch.pk' + img_url

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

        with open("errors/error_CrossStitch.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
            }
            json.dump(error_log, f)
            f.write(',')

    return product