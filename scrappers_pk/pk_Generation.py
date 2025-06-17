import json
from bs4 import BeautifulSoup
import math
import datetime
import config
import functions
def getProducts(soup, category, subCategory, subSubCategory,piece, pageURL):
    products = []
    mainContainer = soup.find('div', {'class': 'CollectionMain'}).find(
        'div', {'class': 'CollectionInner'}).find(
        'div', {'class': 'CollectionInner__Products'}).find(
        'div', {'class': 'ProductListWrapper'})
    
    productsDiv = mainContainer.findAll(
        'div', {'class': 'dev Grid__Cell 1/2--phone 1/3--tablet-and-up 1/4--lap-and-up'})
    
    for i in productsDiv:
        tmp_product = {
            'productID': '',
            'name': '',
            'oldPrice': '',
            'newPrice': '',
            'discount': '',
            'category': '',
            'subCategory': '',
            'subSubCategory': '',
            'url': '',
            'imageUrl': '',
            'views': 0,
            'likes': 0,
            'shares': 0,
            'favourites': 0,
            'list': 0,
            'keywords': [],
            'piece': ''
        }

        productItem = i.find('div', {'class': 'ProductItem'})

        productID = productItem['data-product-id']
        try:
            # Extract image URL
            imageElement = productItem.find('img', {'class': 'ProductItem__Image Image--lazyLoad Image--fadeIn'})
            imageUrl = 'https:' + imageElement['data-src'].replace('{width}', '1000').split('?')[0]

            # Extract product URL
            url = 'https://generation.com.pk' + productItem.find('a', {'class': 'ProductItem__ImageWrapper'})['href']

            # Extract product name
            name = productItem.find('h2', {'class': 'ProductItem__Title Heading'}).text.strip()

            # Extract prices
            priceElement = productItem.find('span', {'class': 'ProductItem__Price Price Text--subdued'})
            newPrice = priceElement.text.split('.')[1].replace(',', '').strip()
            oldPrice = ''  # Assuming no old price is provided in the new HTML

            # Calculate discount (if old price is available)
            try:
                discount = math.floor((int(oldPrice) - int(newPrice)) / int(oldPrice) * 100) if oldPrice else 0
            except:
                discount = 0

            # Populate the product dictionary
            tmp_product['id'] = productID
            tmp_product['name'] = functions.filterName(name, productID)
            tmp_product['oldPrice'] = functions.extractInt(oldPrice)
            tmp_product['newPrice'] = functions.extractInt(newPrice)
            tmp_product['discount'] = discount
            tmp_product['url'] = url
            tmp_product['imageUrl'] = imageUrl
            tmp_product['category'] = category
            tmp_product['subCategory'] = subCategory
            tmp_product['subSubCategory'] = subSubCategory
            tmp_product['piece'] = piece

            products.append(tmp_product)
        except Exception as e:
            with open("errors/error_Generation.json", "a") as f:
                error_log = {
                    "datetime": datetime.datetime.now().isoformat(),
                    "exception_message": str(e),
                    "pageURL": pageURL
                }
                json.dump(error_log, f)

    return products


def getGenerationProductDetails(product): 
    try:
        html = functions.getRequest(product["url"], 'text')
        soup = BeautifulSoup(html, "html.parser")
        
        with open("output.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())

        availableSizes = []
        availableColors = []
        secondaryImages = []


        elements = soup.find_all('div', {'class':'Popover__ValueList'})
        sizeElement = elements[0].find_all('button')
        for size in sizeElement:
            availableSizes.append(size.text.strip())


        colorElement = elements[1].find_all('button')
        for color in colorElement:
            availableColors.append(color.text.strip())

        

        productDescription = str(soup.find('div', {'class': 'ProductMeta__Description Rte'}))
        
        
        mainContainer = soup.find('div',{'class':'Product__SlideshowNavScroller'})
        secondaryImagesDiv = mainContainer.find_all('img')
        
        for img in secondaryImagesDiv:
            if img is not None:
                if 'src' in img.attrs:
                    img_url = img["src"].replace('_160x','_1000x')
                    secondaryImages.append('https:' + img_url)

        secondaryImages= list(set(secondaryImages))
        # secondaryImages = [image for image in secondaryImages if image != product['imageUrl']]
          

        availableSizes = set(availableSizes)
        availableColors = set(availableColors)
        availableSizes = availableSizes - availableColors 
        
        availableColors = list(availableColors)
        availableSizes = list(availableSizes)


        productDescription = functions.filterDescription(productDescription)
        availableSizes = functions.sortSizes('Generation',availableSizes)
        availableColors = functions.sortColors('Generation',availableColors)
        
        
        product['Description'] = productDescription
        product['Sizes'] = availableSizes
        product['Colors'] = availableColors
        product['secondaryImages'] = secondaryImages[:4]
        product['sizeColors'] = functions.crossJoin(availableSizes,availableColors)

        print(product["url"],productDescription,availableSizes,availableColors,secondaryImages[:4])


    except Exception as e:
        print ("An Error Occured While Getting The Product Details")
        print(str(e))
        with open("errors/error_Ethnic.json", "a") as f:
            error_log = {
                "datetime": datetime.datetime.now().isoformat(),
                "product_name": str(product['name']),
                "exception_message": str(e)
                }
            json.dump(error_log, f)  
    return product              