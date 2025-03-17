Scrapping Workflow

STEP-1: Scrap the products for the given brand

Satrting Point: scrapper.py -> scrapBrand() 

1 - Takes brand name as an input to scrap data from the brand's website
2 - Checks weather the brand exist in the navigation/navigation.json file. If the brand exist then it returns pk_brandName.json file which contains all the links which needs to be scrapped from the brands website. The links are organised under Category(gender)->SubCategory->SubSubCategory. It then obtains the soup for every link then pass the soup to a wrapper function named scrapProducts()
3 - scrapProducts() is a wrapper function. It contains the list of all the brands which can be scrapped and then call the function responsible for scrapping the brands

