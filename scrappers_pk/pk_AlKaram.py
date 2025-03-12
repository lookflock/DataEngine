import functions
import datetime
import json
import math
import sys
import os

def getProducts(soup, category, subCategory, subSubCategory, pageURL):
    
    products = []
    #with open("output.html", "w", encoding="utf-8") as file:
    #  file.write(soup.prettify())
    
    productsDiv = soup.find_all('div', {'class': 't4s-product-wrapper'})  
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
                'pageUrl': pageURL,
                'views' : 0,
                'likes' : 0,
                'shares' : 0,
                'favourites' : 0,
                'list' : 0,
                'keywords': []
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
            
                tmp_product['productID'] = productID
                tmp_product['name'] = functions.filterName(name,productID)
                tmp_product['oldPrice'] = oldPrice
                tmp_product['newPrice'] = newPrice
                tmp_product['discount'] = discount
                tmp_product['url'] = 'https://www.alkaramstudio.com'+  url
                tmp_product['imageUrl'] = 'https:' + imageUrl
                tmp_product['category'] =  category
                tmp_product['subCategory'] = subCategory
                tmp_product['subSubCategory'] = subSubCategory
        
                products.append(tmp_product) 
                
                
               
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                
                with open("errors/error_Alkaram.json", "a") as f:
                    error_log = {
                        "datetime": datetime.datetime.now().isoformat(),
                        "productName": str(name),
                        "exceptionMessage": str(e),
                        "pageURL": pageURL,
                        "exceptionType": str(exc_type),
                        "fileName": str(fname),
                        "lineNo": str(exc_tb.tb_lineno)
                    }
                    json.dump(error_log, f)    
 
    return products
