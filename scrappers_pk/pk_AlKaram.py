import json
from bs4 import BeautifulSoup
import math
import datetime
import re
import functions
from urllib.parse import urlparse, urlunparse
import requests
        

supplier='Alkaram'
def getProducts(soup, category, subCategory, subSubCategory, piece, pageURL):
    
    products = []   
    #with open("output.html", "w", encoding="utf-8") as file:
    #  file.write(soup.prettify())
    
    productsDiv = soup.find_all('div', {'class': 't4s-product-wrapper'})  
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
            name = i.find('h3',{'class','t4s-product-title'}).text.strip()
            url = i.find('a',{'class','t4s-full-width-link'})['href']
            discount = 0
            try:
                imageUrl = str(i.find('img', {'class','t4s-product-main-img'})['data-src']).split('?')[0].split('//')[1]
            
                # productID = str(url.split('/')[-1]).split('-')[-2]
                productID = url.split('/')[-1]    

                # priceDiv = i.find('div',{'class','t4s-product-price'}).text.strip().split(' ')[1].replace(',', '')
                priceDiv = i.find('div',{'class','t4s-product-price'})
                
                try:
                    oldPrice = priceDiv.find('del').text.strip()
                    oldPrice = functions.extractInt(oldPrice)

                except:
                    oldPrice = priceDiv.text.strip()
                    oldPrice = functions.extractInt(oldPrice)
                     
                try:
                    newPrice = priceDiv.find('ins').text.strip()
                    newPrice = functions.extractInt(newPrice)
                    discount = math.ceil((oldPrice - newPrice) / oldPrice * 100)
                except:
                        newPrice = oldPrice
                        oldPrice = 0
                        discount = 0
            
                tmp_product['id'] = productID
                tmp_product['name'] = functions.filterName(name,productID)
                tmp_product['oldPrice'] = oldPrice
                tmp_product['newPrice'] = newPrice
                tmp_product['discount'] = discount
                tmp_product['url'] = 'https://www.alkaramstudio.com'+  url
                tmp_product['imageUrl'] = 'https://' + normalize_image_url(imageUrl) 
                tmp_product['category'] =  category
                tmp_product['subCategory'] = subCategory
                tmp_product['subSubCategory'] = subSubCategory
                tmp_product['piece'] = piece
                # tmp_product=getAlKaramProductDetails(tmp_product)
                products.append(tmp_product) 
                
                

            except Exception as e:
                # exc_type, exc_obj, exc_tb = sys.exc_info()
                # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                # print(exc_type, fname, exc_tb.tb_lineno)
                
                print("ERRORRR", json.dumps(tmp_product, indent=4 ,ensure_ascii=False))
                with open("errors/error_Alkaram.json", "a") as f:
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


def getAlkaramProductDetails(product):
    print(f"[Product Details] Extracting Details for Product id: {product['id']}")
    try:
        html = functions.getRequest(product["url"], 'text')
        # with open("debug_output.html", "w", encoding="utf-8") as f:
        #     f.write(html)

        soup = BeautifulSoup(html, "html.parser")

        availableSizes = []
        secondaryImages = []

        # -----------------------
        # Get Sizes
        # -----------------------
        # size_elements = soup.select("div.t4s-swatch__option div.t4s-swatch__item")
        
        # size_elements=soup.select('div.t4s-swatch__option div.t4s-swatch__item:not([data-tooltip])')
        # for size_tag in size_elements:
        #     size_text = size_tag.get_text(strip=True)
        #     if size_text and size_text.upper() not in availableSizes:
        #         availableSizes.append(size_text.upper())
        # Find the Size section by checking the title
        size_elements = soup.select('div.t4s-swatch__option:has(h4:-soup-contains("Size:")) div.t4s-swatch__item[data-value]')
        for size_tag in size_elements:
            size_text = size_tag.get_text(strip=True)
            if size_text and size_text.upper() not in availableSizes:
                availableSizes.append(size_text.upper())
        availableSizes = functions.sortSizes('Alkaram', availableSizes)

        # -----------------------
        # Get Secondary Images
        # -----------------------
        media_items = soup.select('div[data-product-single-media-wrapper] img')
        main_image = product.get("imageUrl")

        for img in media_items:
            img_url = img.get('data-master') or img.get('data-src') or img.get('src')
            if img_url:
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                elif img_url.startswith('/'):
                    img_url = 'https://www.alkaramstudio.com' + img_url

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

        with open("errors/error_AlKaram.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
            }
            json.dump(error_log, f)
            f.write(',')

    return product
