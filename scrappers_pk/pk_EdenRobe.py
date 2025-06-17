import json
from bs4 import BeautifulSoup
import math
import datetime
import re
import functions
from urllib.parse import urlparse, urlunparse
import requests
        

supplier= 'EdenRobe'

def getProducts(soup, category, subCategory, subSubCategory, piece, pageURL):
    products = []
    container = soup.find('ul', id='product-grid')
    if not container:
        print(f"ERROR: No products container found using selector 'ul#product-grid'")
        with open("errors/error_EdenRobe.json", "a") as f:
            json.dump({
                "datetime": datetime.datetime.now().isoformat(),
                "error": "ERROR: No products container found using selector 'ul#product-grid'",
            }, f)
            f.write("\n")
        return products

    items = container.find_all('li', class_='column')
    print(f"Found {len(items)} items in grid")

    for li in items:
        try:
            link_tag = li.find('a', class_='product-featured-image-link')
            if not link_tag:
                continue
            url = link_tag['href']
            product_name = link_tag.get('title', '').strip()
            productID = product_name.split('-')[-1].strip()

            img_tag = link_tag.find('img', class_='product-primary-image')
            # img_url = (
            #     'https:' + img_tag['src'].split('?')[0].replace('width=375', 'width=1000')
            #     if img_tag and img_tag.get('src') else ''
            # )
            img_url = (
                img_tag['src'].split('?')[0].replace('width=375', 'width=1000')
                if img_tag and img_tag.get('src') else ''
            )
            img_url=normalize_image_url(img_url)

            # Find <script type="application/json"> to get pricing and sizes
            json_script = li.find('script', type='application/json')
            if json_script:
                try:
                    variants = json.loads(json_script.string)
                    # Pick first variant with available pricing
                    for variant in variants:
                        if 'price' in variant:
                            newPrice = int(variant['price'] / 100)
                            oldPrice = int(variant.get('compare_at_price', newPrice) / 100)
                            break
                    else:
                        newPrice = oldPrice = 0
                except Exception as je:
                    newPrice = oldPrice = 0
            else:
                newPrice = oldPrice = 0

            discount = math.ceil(int(100 * (oldPrice - newPrice) / oldPrice)) if oldPrice else 0

            tmp_product = {
                'supplier': supplier,
                'id': productID,
                'name': functions.filterName(product_name, productID),
                'oldPrice': oldPrice,
                'newPrice': newPrice,
                'discount': discount,
                'url': 'https://www.edenrobe.com' + url,
                'imageUrl': img_url,
                'category': category,
                'subCategory': subCategory,
                'subSubCategory': subSubCategory,
                'page': pageURL,
                'piece': piece,
                'views': 0,
                'likes': 0,
                'shares': 0,
                'favourites': 0,
                'status': 1,
                'list': 0,
                'keywords': [],
                'valid': 1
            }
            # tmp_product=getEdenRobeProductDetails(tmp_product)
            products.append(tmp_product)

        except Exception as e:
            with open("errors/error_EdenRobe.json", "a") as f:
                json.dump({
                    "datetime": datetime.datetime.now().isoformat(),
                    "error": str(e),
                    "item_html": str(li)[:500]
                }, f)
                f.write("\n")
    return products


def normalize_image_url(url):
    parsed = urlparse(url)
    path = parsed.path
    path = re.sub(r'(_\d+x)?(\.\w+)$', r'\2', path)  # remove _360x, _720x, etc.
    return urlunparse(parsed._replace(path=path, query=""))


def getEdenRobeProductDetails(product):
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
            sizeElement = soup.find('fieldset',{'data-handle': 'size'})
            sizeElement = sizeElement.find_all('label')
            for size in sizeElement:
                availableSizes.append(size.text.strip())
            availableSizes = functions.sortSizes('Cambridge', availableSizes)
        except:
            availableSizes = []

        # Get Secondary Images
        # -----------------------
        mainContainer = soup.find('div',{'class':'product-image-container'})
        secondaryImagesDiv = mainContainer.find_all('img')
        main_image = product.get("imageUrl")

        for img in secondaryImagesDiv:
            if img is not None:
                if 'src' in img.attrs:
                    img_url = img["src"].replace('_20x','_1000x')
                    if img_url:
                        if img_url.startswith('//'):
                            img_url = 'https:' + img_url
                        elif img_url.startswith('/'):
                            img_url = 'https://www.edenrobe.com' + img_url

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

        with open("errors/error_EdenRobe.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
            }
            json.dump(error_log, f)
            f.write(',')

    return product


# def getProducts(soup, category, subCategory, subSubCategory, piece, pageURL):
    
#     products = []
#     mainContainer = soup.find('ul', {'class','products collection row small-up-2 medium-up-4 pagination--infinite'})
#     productsDiv = mainContainer.find_all('li', {'class': 'column'})
#     for product in productsDiv:            
#             tmp_product = {
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
#                 'pageUrl': pageURL,
#                 'views' : 0,
#                 'likes' : 0,
#                 'shares' : 0,
#                 'favourites' : 0,
#                 'list' : 0,
#                 'keywords': [],
#                 'piece': ''
#             }
            
#             urlDiv = product.find('a',{'class','product-card-title'})
#             name = urlDiv.text.strip()
#             url = urlDiv['href']
#             try:
#                 imageUrl = product.find('img', {'class','lazyload product-primary-image'})['src']
#                 imageUrl = imageUrl.replace('_20x_', '_1000x_')
#                 # url_parts = imageUrl.split('/')
#                 productID = product.find('a',{'class','product-card-title'})['title'].split(' - ')[-1].strip()
#                 # imageUrl = imageUrl.replace('{width}', '360')
#                 prices = product.find_all('span',{'class','amount'})
#                 try:                    
#                     oldPrice = prices[0].text.strip()
#                     oldPrice = functions.extractInt(oldPrice)
#                     newPrice = prices[1].text.strip()
#                     newPrice =functions.extractInt(newPrice)
#                     discount = math.ceil((oldPrice - newPrice) / oldPrice * 100)
#                     if discount == 0:
#                          oldPrice = 0
#                 except:
#                     newPrice = prices[0].text.strip()
#                     newPrice =functions.extractInt(newPrice)
#                     oldPrice = 0
#                     discount = 0
            
#                 tmp_product['id'] = productID
#                 tmp_product['name'] = functions.filterName(name,productID)
#                 tmp_product['oldPrice'] = oldPrice
#                 tmp_product['newPrice'] = newPrice
#                 tmp_product['discount'] = discount
#                 tmp_product['url'] = 'https://edenrobe.com'+  url
#                 tmp_product['imageUrl'] = 'https:' + imageUrl
#                 tmp_product['category'] =  category
#                 tmp_product['subCategory'] = subCategory
#                 tmp_product['subSubCategory'] = subSubCategory
#                 tmp_product['piece'] = piece
#                 products.append(tmp_product) 

#             except Exception as e:
#                 with open("errors/error_EdenRobe.json", "a") as f:
#                     error_log = {
#                     "datetime": datetime.datetime.now().isoformat(),
#                     "product_name": str(name),
#                     "exception_message": str(e),
#                     "pageURL number": pageURL
#                     }
#                     json.dump(error_log, f)    
 
#     return products

# def getEdenRobeProductDetails(product):
#     try:
#         html = functions.getRequest(product["url"], 'text')
#         soup = BeautifulSoup(html, "html.parser")
        
#         #with open("output.html", "w", encoding="utf-8") as f:
#         #    f.write(soup.prettify())

        
#         availableSizes = []
#         availableColors = []
#         secondaryImages = []


#         try:
#             sizeElement = soup.find('fieldset',{'data-handle': 'size'})
#             sizeElement = sizeElement.find_all('label')
#             for size in sizeElement:
#                 availableSizes.append(size.text.strip())
#         except:
#             availableSizes = []
            
#         try:
#             colorElement = soup.find('fieldset',{'data-handle': 'color'})
#             colorElement = colorElement.find_all('label')
#             for color in colorElement:
#                 availableColors.append(color.text.strip())
#         except:
#             colorElement = []

#         productDescription= str(soup.find('div', {'class': 'product-short-description rte'}))

#         mainContainer = soup.find('div',{'class':'product-image-container'})
#         secondaryImagesDiv = mainContainer.find_all('img')
        
#         for img in secondaryImagesDiv:
#             if img is not None:
#                 if 'src' in img.attrs:
#                     img_url = img["src"].replace('_20x','_1000x')
#                     secondaryImages.append('https:' + img_url)

#         secondaryImages= list(set(secondaryImages))
#         # secondaryImages = [image for image in secondaryImages if image != product['imageUrl']]
#         productDescription = functions.filterDescription(productDescription)
#         availableSizes = functions.sortSizes('EdenRobe',availableSizes)
#         availableColors = functions.sortColors('EdenRobe',availableColors)
        
#         print(product["url"],productDescription,availableSizes,availableColors,secondaryImages[:4])


#         product['Description'] = productDescription
#         product['Sizes'] = availableSizes
#         product['Colors'] = availableColors
#         product['secondaryImages'] = secondaryImages[:4]
#         product['sizeColors'] = functions.crossJoin(availableSizes,availableColors)


#     except Exception as e:
#         print ("An Error Occured While Getting The Product Details")
#         print(str(e))
#         with open("errors/error_EdenRobe.json", "a") as f:
#             error_log = {
#                 "datetime": datetime.datetime.now().isoformat(),
#                 "product_name": str(product['name']),
#                 "exception_message": str(e)
#                 }
#             json.dump(error_log, f)  
#     return product              