import json
from bs4 import BeautifulSoup
import math
import datetime
import re
import functions
from urllib.parse import urlparse, urlunparse
import requests
        

supplier='Chicophicial'
def getProducts(soup, category, subCategory, subSubCategory, piece, pageURL):
    products = []

    mainContainer = soup.find('div', class_='collection')
    if not mainContainer:
        return products  # If container not found, return empty list

    productsDiv = mainContainer.find_all('div', class_='gitem fl')

    # Save parsed HTML to inspect structure if needed
    with open("output.html", "w", encoding="utf-8") as f:
        f.write(soup.prettify())

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
            nameDiv = i.find('a', class_='grid_lnk')
            if not nameDiv:
                continue

            name = nameDiv.get('aria-label', '').strip()
            url = nameDiv.get('href', '').strip()

            # Product ID
            pr_review = i.find('div', class_='pr_review')
            productID = pr_review.find('span')['data-id'] if pr_review else ''

            # Image URL
            primary_img_div = nameDiv.find('div', class_='grid_img wow zoomIn lazyload primary')
            imageUrl = ''
            if primary_img_div and 'data-bgset' in primary_img_div.attrs:
                imageUrl = primary_img_div['data-bgset'].split(' ')[0].replace('_150x', '_1000x')
                if not imageUrl.startswith('https:'):
                    imageUrl = 'https:' + normalize_image_url(imageUrl)

            # Prices
            # USD_convert = functions.PKR_rate_USD()
            try:
                oldPriceText = i.find('s', class_='pr_price')
                newPriceText = i.find('span', class_='pr_price sale')

                if oldPriceText and newPriceText:
                    oldPrice = functions.extractInt(oldPriceText.text.strip()) 
                    newPrice = functions.extractInt(newPriceText.text.strip()) 
                else:
                    newPrice = functions.extractInt(i.find('span', class_='pr_price').text.strip()) 
                    oldPrice = 0
                discount = math.ceil((oldPrice - newPrice) / oldPrice * 100) if oldPrice else 0
            except:
                newPrice = functions.extractInt(i.find('span', class_='pr_price').text.strip())
                oldPrice = 0
                discount = 0

            # Fill product data
            tmp_product['id'] = productID
            tmp_product['name'] = functions.filterName(name, productID)
            tmp_product['oldPrice'] = int(oldPrice)
            tmp_product['newPrice'] = int(newPrice)
            tmp_product['discount'] = int(discount)
            tmp_product['url'] = 'https://chicophicial.com' + url
            tmp_product['imageUrl'] = imageUrl
            # tmp_product=getChicophicialProductDetails(tmp_product)
            products.append(tmp_product)

        except Exception as e:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": name if 'name' in locals() else '',
                "exception_message": str(e),
                "pageURL": pageURL
            }
            with open("errors/error_Chichophicial.json", "a", encoding="utf-8") as f:
                json.dump(error_log, f)
                f.write("\n")

    return products


def normalize_image_url(url):
    parsed = urlparse(url)
    path = parsed.path
    path = re.sub(r'(_\d+x)?(\.\w+)$', r'\2', path)  # remove _360x, _720x, etc.
    return urlunparse(parsed._replace(path=path, query=""))


def getChicophicialProductDetails(product):
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
        sizeElements = soup.find('div',{'class','product-form'}).find_all('div',{'class','swatch-element'})
        for element in sizeElements:
            availableSizes.append(element['data-value'])
        availableSizes = functions.sortSizes('Charcoal', availableSizes)

        # Get Secondary Images
        # -----------------------
        mainContainer = soup.find('div',{'class','swiper-wrapper'})
        secondaryImagesDiv = mainContainer.find_all('a',{'class','swiper-slide'})
        main_image = product.get("imageUrl")
        for img in secondaryImagesDiv:
            # img = img.find('a')
            # print(img)
            if 'href' in img.attrs:
                    # print(img["data-src"])
                    img_url = img["href"]
                    if img_url:
                        if img_url.startswith('//'):
                            img_url = 'https:' + img_url
                        elif img_url.startswith('/'):
                            img_url = 'https://www.chicophicial.com' + img_url
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

        with open("errors/error_Chicophicial.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
            }
            json.dump(error_log, f)
            f.write(',')

    return product