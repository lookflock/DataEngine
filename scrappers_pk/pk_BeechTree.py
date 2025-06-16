import json
from bs4 import BeautifulSoup
import math
import datetime
import re
import functions
from urllib.parse import urlparse, urlunparse
import requests

supplier="BeechTree"
def getProducts(soup, category, subCategory, subSubCategory, piece, pageURL):
    products = []
    mainContainer = soup.find('ul', {'id': 'product-grid'})
    if mainContainer:
        productsDiv = mainContainer.find_all('li',{'class': 'grid__item'})
    
        with open("output.html", "w", encoding="utf-8") as f:
             f.write(soup.prettify())
          
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
            try:
                productID = i.find('div',{'class':'card'})['data-product-id']
            except:
                print('Product ID not found')
                continue
            try:
                name = i.find('h3').text.strip()
                url = i.find('div',{'class':'card__inner'}).find('a')['href']
                imageUrl = i.find('img',{'class','motion-reduce'})['src']
                try:
                    
                    # Try to find the old (original) price if it exists
                    old_price_tag = i.find('s', class_='price-item price-item--regular')
                    if old_price_tag:
                        money_span = old_price_tag.find('span', class_='money')
                        oldPrice = money_span.text.strip() if money_span else None
                    else:
                        oldPrice = None
                    
                    # Try to find the new (sale) price
                    sale_price_tag = i.find('span', class_='price-item price-item--sale')
                    if sale_price_tag:
                        money_span_new = sale_price_tag.find('span', class_='money')
                        newPrice = money_span_new.text.strip() if money_span_new else None
                    else:
                        newPrice = None


                    # old_price_tag = i.find('s', {'class': 'price-item price-item--regular'})
                    # money_span = old_price_tag.find('span', {'class': 'money'})
                    # oldPrice = money_span.text.strip()
                    # newPrice = i.find('span', {'class': 'price-item price-item--sale'}).text.strip()            
                    discount =  i.find('div',{'class':'ctm-sale-label'}).text.strip()
                   
                except:
                    newPrice = i.find('span', {'class': 'price-item price-item--regular'}).text.strip() 
                    oldPrice =0
                    discount =0
                
                tmp_product['id'] = productID
                tmp_product['name'] = functions.filterName(name,productID)
                tmp_product['oldPrice'] = functions.extractInt(oldPrice)
                tmp_product['newPrice'] = functions.extractInt(newPrice)
                tmp_product['discount'] = functions.extractInt(discount) 
                tmp_product['url'] =  'https://beechtree.pk' + url
                tmp_product['imageUrl'] = 'https:' + normalize_image_url(imageUrl) 
                tmp_product['category'] =  category
                tmp_product['subCategory'] = subCategory
                tmp_product['subSubCategory'] = subSubCategory
                tmp_product['piece'] = piece
                # tmp_product=getBeechTreeProductDetails(tmp_product)
                products.append(tmp_product) 
            except Exception as e:
                with open("errors/error_BeechTree.json", "a") as f:
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


def getBeechTreeProductDetails(product):
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
        availableSizes = [el.get('value') for el in soup.select('div.new_options_container input[type="radio"][name^="Size-1"]')]
        availableSizes = functions.sortSizes('BeechTree', availableSizes)

        # -----------------------
        # Get Secondary Images
        # -----------------------
        main_image = product.get("imageUrl")

        for a_tag in soup.select('div.swiper-slide a[href]'):
            img_url = a_tag['href']
            if img_url.startswith('//'):
                img_url = 'https:' + img_url
            elif img_url.startswith('/'):
                    img_url = 'https://www.beechtree.pk' + img_url
            
            parsed_url = urlparse(img_url)
            cleaned_url = urlunparse(parsed_url._replace(query=""))

            if main_image:
                normalized_main = normalize_image_url(main_image)
                normalized_secondary = normalize_image_url(cleaned_url)
                if normalized_main == normalized_secondary:
                    continue
            
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

        with open("errors/error_BeechTree.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
            }
            json.dump(error_log, f)
            f.write(',')

    return product