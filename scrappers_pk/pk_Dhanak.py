import json
from bs4 import BeautifulSoup
import math
import datetime
import re
import functions
from urllib.parse import urlparse, urlunparse
import requests
        

supplier='Dhanak'
def getProducts(soup, category, subCategory, subSubCategory, piece, pageURL):
    products = []
    try:
        mainContainer = soup.find('ul', {'class': 'productListing'})
        productsDiv = mainContainer.find_all('li',{'class': 'product'})
    except:
        print('No products found')
        return products
    
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
            
            tmp_product['id'] = productID
            tmp_product['name'] = functions.filterName(name,productID)
            tmp_product['oldPrice'] = int(oldPrice)
            tmp_product['newPrice'] = int(newPrice)
            tmp_product['discount'] = int(discount)
            tmp_product['url'] =  'https://dhanak.com.pk' + url
            tmp_product['imageUrl'] = "https:" + normalize_image_url(imageUrl) 
            tmp_product['category'] =  category
            tmp_product['subCategory'] = subCategory
            tmp_product['subSubCategory'] = subSubCategory
            tmp_product['piece'] = piece
            # print(json.dumps(tmp_product, indent=4 ,ensure_ascii=False))
            # tmp_product=getDhanakProductDetails(tmp_product)
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

def normalize_image_url(url):
    parsed = urlparse(url)
    path = parsed.path
    path = re.sub(r'(_\d+x)?(\.\w+)$', r'\2', path)  # remove _360x, _720x, etc.
    return urlunparse(parsed._replace(path=path, query=""))


def get_base_filename(url):
    """Return filename without _1000x or other suffixes."""
    path = urlparse(url).path
    filename = path.split('/')[-1]
    filename = re.sub(r'(_\d+x)?(\.\w+)$', r'\2', filename)  # Remove size suffix
    return filename.lower()


def getDhanakProductDetails(product):
    print(f"[Product Details] Extracting Details for Product id: {product['id']}")
    try:
        html = functions.getRequest(product["url"], 'text')
        soup = BeautifulSoup(html, "html.parser")
        
        availableSizes = []
        secondaryImages = []
        seen_filenames = set()

        # Get Sizes
        try:
            sizeElements = soup.find('fieldset', {'class': 'js product-form__input clearfix'}).find_all('input', {'class': 'product-form__radio'})
            for element in sizeElements:
                availableSizes.append(element['value'])
            availableSizes = functions.sortSizes('Cambridge', availableSizes)
        except:
            availableSizes = []

        # Get Secondary Images
        mainContainer = soup.find_all('div', {'class': 'productView-thumbnail'})
        main_image = product.get("imageUrl")
        normalized_main = normalize_image_url(main_image)

        for img_tag in mainContainer:
            img = img_tag.find('img')
            if img and 'src' in img.attrs:
                img_url = img["src"].replace('_large', '_1000x')

                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                elif img_url.startswith('/'):
                    img_url = 'https://www.dhanak.com.pk' + img_url

                parsed_url = urlparse(img_url)
                cleaned_url = urlunparse(parsed_url._replace(query=""))
                normalized_secondary = normalize_image_url(cleaned_url)

                # Skip if same as main image
                if normalized_secondary == normalized_main:
                    continue

                # Skip duplicates based on filename
                base_filename = get_base_filename(cleaned_url)
                if base_filename in seen_filenames:
                    continue
                seen_filenames.add(base_filename)

                # Verify and append
                try:
                    print(f"[Product Details] Verifying Secondary Image for Product id: {product['id']}")
                    response = requests.head(cleaned_url, timeout=5)
                    if response.status_code == 200:
                        secondaryImages.append(cleaned_url)
                    else:
                        print(f"[image check] Invalid image (status {response.status_code}): {cleaned_url}")
                except Exception as e:
                    print(f"[image check] Failed to verify image: {cleaned_url} — {e}")

        product['secondaryImages'] = secondaryImages
        product['sizes'] = availableSizes

    except Exception as e:
        print("An Error Occurred While Getting The Product Details")
        print(str(e))

        with open("errors/error_Dhanak.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
            }
            json.dump(error_log, f)
            f.write(',')

    return product



# def getDhanakProductDetails(product):
#     print(f"[Product Details] Extracting Details for Product id: {product['id']}")
#     try:
#         html = functions.getRequest(product["url"], 'text')
#         soup = BeautifulSoup(html, "html.parser")
        
#         # with open("output_generate.html", "w", encoding="utf-8") as f:
#         #      f.write(soup.prettify())
        
#         availableSizes = []
#         secondaryImages = []

#         # -----------------------
#         # Get Sizes
#         # -----------------------
#         try:
#             sizeElements = soup.find('fieldset',{'class','js product-form__input clearfix'}).find_all('input',{'class','product-form__radio'})
#             for element in sizeElements:
#                 availableSizes.append(element['value'])
#             availableSizes = functions.sortSizes('Cambridge', availableSizes)
#         except:
#             availableSizes = []

#         # Get Secondary Images
#         # -----------------------
#         mainContainer = soup.find_all('div',{'class','productView-thumbnail'})
#         main_image = product.get("imageUrl")
#         # secondaryImagesDiv = mainContainer.find('img')
#         # print(secondaryImagesDiv)
#         for img in mainContainer:
#             img = img.find('img')
#             # print(img)
#             if 'src' in img.attrs:
#                     # print(img["data-src"])
#                     img_url = img["src"]
#                     img_url = img_url.replace('_large','_1000x')
#                     if img_url:
#                         if img_url.startswith('//'):
#                             img_url = 'https:' + img_url
#                         elif img_url.startswith('/'):
#                             img_url = 'https://www.dhanak.com.pk' + img_url

#                         parsed_url = urlparse(img_url)
#                         cleaned_url = urlunparse(parsed_url._replace(query=""))

#                         # Skip if this is the same as the main image
#                         if main_image:
#                             normalized_main = normalize_image_url(main_image)
#                             normalized_secondary = normalize_image_url(cleaned_url)

#                             if normalized_main == normalized_secondary:
#                                 continue
                            
#                         # Verify and add
#                         try:
#                             print(f"[Product Details] Verifying Secondary Images for Product id: {product['id']}")
#                             response = requests.head(cleaned_url, timeout=5)
#                             if response.status_code == 200:
#                                 secondaryImages.append(cleaned_url)
#                             else:
#                                 print(f"[image check] Invalid image (status {response.status_code}): {cleaned_url}")
#                         except Exception as e:
#                             print(f"[image check] Failed to verify image: {cleaned_url} — {e}")

#         # Finalize
#         secondaryImages = list(set(secondaryImages))
#         product['secondaryImages'] = secondaryImages
#         product['sizes'] = availableSizes

#     except Exception as e:
#         print("An Error Occurred While Getting The Product Details")
#         print(str(e))

#         with open("errors/error_Dhanak.json", "a") as f:
#             error_log = {
#                 "datetime": datetime.datetime.now().isoformat(),
#                 "product_name": str(product['name']),
#                 "exception_message": str(e)
#             }
#             json.dump(error_log, f)
#             f.write(',')

#     return product