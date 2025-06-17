import json
from bs4 import BeautifulSoup
import math
import datetime
import re
import functions
from urllib.parse import urlparse, urlunparse
import requests
        

supplier='Cambridge'

def getProducts(soup, category, subCategory, subSubCategory, piece, pageURL):
    
    products = []
    #with open("output.html", "w", encoding="utf-8") as file:
    #  file.write(soup.prettify())
    mainContainer = soup.find('div',{'class': 'collection'})
    productsDiv = mainContainer.find_all('li', {'class': 'product'})  
    for product in productsDiv:      
                  
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
            
                tmp_product['id'] = productID
                tmp_product['name'] = functions.filterName(name,productID)
                tmp_product['oldPrice'] = oldPrice
                tmp_product['newPrice'] = newPrice
                tmp_product['discount'] = discount
                tmp_product['url'] = 'https://diners.com.pk'+  url
                tmp_product['imageUrl'] = 'https:' + normalize_image_url(imageUrl)
                tmp_product['category'] =  category
                tmp_product['subCategory'] = subCategory
                tmp_product['subSubCategory'] = subSubCategory
                tmp_product['piece'] = piece
                # tmp_product=getDinersProductDetails(tmp_product)
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


def normalize_image_url(url):
    parsed = urlparse(url)
    path = parsed.path
    path = re.sub(r'(_\d+x)?(\.\w+)$', r'\2', path)  # remove _360x, _720x, etc.
    return urlunparse(parsed._replace(path=path, query=""))


def getDinersProductDetails(product):
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
            sizeElement = soup.find('div',{'class':'productView-options'}).find_all('span',{'class':'text'})
            for size in sizeElement:
                availableSizes.append(size.text.strip())
            availableSizes = functions.sortSizes('Cambridge', availableSizes)
        except:
            availableSizes = []

        # Get Secondary Images
        # -----------------------
        mainContainer = soup.find('div',{'class':'productView-image-wrapper'})
        secondaryImagesDiv = mainContainer.find_all('img')
        main_image = product.get("imageUrl")
        for img in secondaryImagesDiv:
            if img is not None:
                if 'src' in img.attrs:
                    img_url = img["src"]
                    if img_url:
                        if img_url.startswith('//'):
                            img_url = 'https:' + img_url
                        elif img_url.startswith('/'):
                            img_url = 'https://www.diners.com.pk' + img_url

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

        with open("errors/error_Diners.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
            }
            json.dump(error_log, f)
            f.write(',')

    return product
