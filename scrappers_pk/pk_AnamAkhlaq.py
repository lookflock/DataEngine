import json
from bs4 import BeautifulSoup
import math
import datetime
import re
import functions
from urllib.parse import urlparse, urlunparse
import requests
        
supplier='AnamAkhlaq'

def getProducts(soup, category, subCategory, subSubCategory, piece, pageURL):
    products = []
    mainContainer = soup.find('ul', {'class': 'grid grid--uniform grid--view-items'})
    productsDiv = mainContainer.find_all('li',{'class': 'grid__item'})    
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
        nameDiv = product.find('a', {'class': 'grid-view-item__link'})
        name = nameDiv.text.strip()
        try:    
            productID = product.find('div',{'class','grid-view-item__image-wrapper'})['id'].split('-')[-1]     
            url = nameDiv['href']
            imageUrl = product.find('div', {'class': 'grid-view-item__image-wrapper'}).find('img',{'class':'grid-view-item__image'})['data-src']
            imageUrl = imageUrl.replace('_{width}x', '_1000x')
            USD_convert = 281.07
            try:
                oldPrice = product.find('span', class_='price-item price-item--regular').text.strip()
                oldPrice = functions.extractInt(oldPrice)*USD_convert
                newPrice = product.find('span', class_='price-item price-item--sale').text.strip()
                newPrice = functions.extractInt(newPrice)*USD_convert
                discount = math.ceil((oldPrice - newPrice) / oldPrice * 100)
                if discount == 0:
                    oldPrice = 0
            except:
                newPrice = product.find('span', class_='price-item--sale').text.strip()
                newPrice = functions.extractInt(newPrice)*USD_convert
                oldPrice = 0
                discount = 0
            
            tmp_product['id'] = productID
            # tmp_product['name'] = name
            tmp_product['name'] = functions.filterName(name,productID)
            tmp_product['oldPrice'] = int(oldPrice)
            tmp_product['newPrice'] = int(newPrice)
            tmp_product['discount'] = int(discount)
            tmp_product['url'] =  'https://anamakhlaq.com' + url
            tmp_product['imageUrl'] = 'https:' + normalize_image_url(imageUrl) 
            tmp_product['category'] =  category
            tmp_product['subCategory'] = subCategory
            tmp_product['subSubCategory'] = subSubCategory
            tmp_product['piece'] = piece
            # tmp_product=getAnamAkhlaqProductDetails(tmp_product)
            products.append(tmp_product)    

        except Exception as e:
            with open("errors/error_AnamAkhlaq.json", "a") as f:
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

def getAnamAkhlaqProductDetails(product):
    print(f"[Product Details] Extracting Details for Product id: {product['id']}")

    try:
        html = functions.getRequest(product["url"], 'text')
        soup = BeautifulSoup(html, "html.parser")
        
        # with open("output_generate.html", "w", encoding="utf-8") as f:
        #      f.write(soup.prettify())
        # html = functions.getRequest(product["url"], 'text')
        # with open("debug_output.html", "w", encoding="utf-8") as f:
        #     f.write(html)

        # soup = BeautifulSoup(html, "html.parser")

        availableSizes = []
        secondaryImages = []

        # -----------------------
        # Get Sizes
        # -----------------------
        size_select = soup.select_one('select#SingleOptionSelector-0')
        availableSizes = [option.get_text(strip=True) for option in size_select.find_all('option')]
        availableSizes = functions.sortSizes('AnamAkhlaq', availableSizes)

        # -----------------------
        # Get Secondary Images
        # -----------------------
        main_image = product.get("imageUrl")

        for a_tag in soup.select('ul.product-single__thumbnails a[href]'):
            img_url = a_tag['href']
            if img_url.startswith('//'):
                img_url = 'https:' + img_url  # Convert to full URL

            
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

        with open("errors/error_AnamAkhlaq.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
            }
            json.dump(error_log, f)
            f.write(',')

    return product