import json
from bs4 import BeautifulSoup
import math
import datetime
import re
import functions
from urllib.parse import urlparse, urlunparse
import requests
        

supplier='BonanzaSatrangi'
def getProducts(soup, category, subCategory, subSubCategory, piece, pageURL):
    
    products = []
    mainContainer = soup.find('div', {'class':'sr4-products'})
    try:
        productsDiv = mainContainer.find_all('div', {'class':'sr4-product'})
    except:
        return products

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
        # with open("output3.html", "w", encoding="utf-8") as f:
        #     f.write(i.prettify())

        name = i.find('h3',{'class':'sr4-product-title'}).text.strip()
        try:
            url = i.find('h3',{'class':'sr4-product-title'}).find('a')['href']
            Product_id = re.findall( r'\((.*?)\)', name)[0]
            imageUrl = i.find('img', {'class':'sr4-product-main-img lazyloadsr4'})['data-src'].split('?')[0].split('//')[1]

            # imageUrl = imageUrl.replace('{width}', '1000')
            try:
                price = i.find('div',{'class':'sr4-product-price'})
                oldPrice = price.find_all('span',{'class':'money'})[0].text.strip()
                oldPrice = functions.extractInt(oldPrice)
                newPrice = price.find_all('span',{'class':'money'})[1].text.strip()
                newPrice =functions.extractInt(newPrice)
                discount = math.ceil((oldPrice - newPrice) / oldPrice * 100)
            except:
                newPrice = i.find('div',{'class':'details'}).find('span', class_='product-price__price').text.strip()
                newPrice = functions.extractInt(newPrice)
                oldPrice = 0
                discount = 0
            
            
            tmp_product['id'] = Product_id
            tmp_product['name'] = functions.filterName(name,Product_id)
            tmp_product['oldPrice'] = oldPrice
            tmp_product['newPrice'] = newPrice
            tmp_product['discount'] = discount
            tmp_product['url'] = 'https://bonanzasatrangi.com'+  url
            tmp_product['imageUrl'] = 'https://' + normalize_image_url(imageUrl) 
            tmp_product['category'] =  category
            tmp_product['subCategory'] = subCategory
            tmp_product['subSubCategory'] = subSubCategory
            tmp_product['piece'] = piece
            # tmp_product=getBonanzaSatrangiProductDetails(tmp_product)
            products.append(tmp_product) 

        except Exception as e:
                with open("errors/error_BonanzaSatrangi.json", "a") as f:
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


def getBonanzaSatrangiProductDetails(product):
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
        availableSizes = [
            el.get('data-value') 
            for el in soup.select('div[data-swatch-option][data-id="0"] div.sr4-swatch__item')
        ]
        availableSizes = functions.sortSizes('BonanzaSatrangi', availableSizes)

        # -----------------------
        # Get Secondary Images
        # -----------------------
        media_items = soup.select(".sr4-product__media-item img[data-master]")
        main_image = product.get("imageUrl")

        for img_tag in media_items:
            img_url = img_tag.get("data-master")
            if img_url:
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                elif img_url.startswith('/'):
                    img_url = 'https://www.bonanzasatrangi.com' + img_url

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

        with open("errors/error_BonanzaSatrangi.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
            }
            json.dump(error_log, f)
            f.write(',')

    return product