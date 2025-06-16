import json
from bs4 import BeautifulSoup
import math
import datetime
import re
import functions
from urllib.parse import urlparse, urlunparse
import requests
        

supplier='Charcoal'

def getProducts(soup, category, subCategory, subSubCategory,piece, pageURL):
    products = []
    # with open("output.html", "w", encoding="utf-8") as f:
    #        f.write(soup.prettify())
    
    mainContainer = soup.find('product-list', {'class': 'product-list'})
    productsDiv = mainContainer.find_all('product-card',{'class': 'product-card'})
    
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
        
        
        nameDiv = i.find('img', {'class': 'product-card__image'})
        name = nameDiv['alt']
        try:    
            
            url = i.find('span',{'class':'product-card__title'}).find('a')['href']
            productID = url.split('/')[-1]
            imageUrl = nameDiv['src']
            try:
                oldPrice = i.find('compare-at-price', class_='text-subdued line-through').text.strip()
                oldPrice = functions.extractInt(oldPrice)
                newPrice = i.find('sale-price', class_='text-on-sale').text.strip()
                newPrice = functions.extractInt(newPrice)
                discount = math.ceil((oldPrice - newPrice) / oldPrice * 100)
            except:
                newPrice = i.find('sale-price', class_='text-subdued').text.strip()
                newPrice = functions.extractInt(newPrice)
                oldPrice = 0
                discount = 0
            
            tmp_product['id'] = productID
            # tmp_product['name'] = name
            tmp_product['name'] = functions.filterName(name,productID)
            tmp_product['oldPrice'] = int(oldPrice)
            tmp_product['newPrice'] = int(newPrice)
            tmp_product['discount'] = int(discount)
            tmp_product['url'] =  'https://charcoal.com.pk' + url
            tmp_product['imageUrl'] = 'https:' + normalize_image_url(imageUrl)
            tmp_product['category'] =  category
            tmp_product['subCategory'] = subCategory
            tmp_product['subSubCategory'] = subSubCategory
            tmp_product['piece'] = piece
            # tmp_product=getCharcoalProductDetails(tmp_product)
            products.append(tmp_product)    

        except Exception as e:
            with open("errors/error_Almirah.json", "a") as f:
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


def getCharcoalProductDetails(product):
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
        sizeElements = soup.find('fieldset',{'class','variant-picker__option'}).find_all('label',{'class','block-swatch'})
        for element in sizeElements:
            availableSizes.append(element.text.strip())
        availableSizes = functions.sortSizes('Charcoal', availableSizes)

        # Get Secondary Images
        # -----------------------
        main_image = product.get("imageUrl")
        for img in soup.select('div.product-gallery__media img[src]'):
            img_url = img['src']
            if img_url:
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                elif img_url.startswith('/'):
                    img_url = 'https://www.thecambridgeshop.com' + img_url

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

        with open("errors/error_Charcoal.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
            }
            json.dump(error_log, f)
            f.write(',')

    return product

