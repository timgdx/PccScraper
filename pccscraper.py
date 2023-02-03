#import requests
import signal
import cloudscraper
from prettytable import PrettyTable
import time
import json
import os
import datetime

##############
MAX_PRICE = 620
TARGET_PRODUCTS = ["3080","3070 Ti","6800"]
OPTIMAL_PRICE = [550,400,550]
LOOP = 60*5 # 0 - run once; > 0 - run every X seconds
URL = "https://www.pccomponentes.pt/"
TARGET_URL = "https://www.pccomponentes.pt/api-v1/products/search?categoryId=2194165b-70a8-4e4e-ab74-0007a55b73ab&sort=price_asc&channel=pt&page={0}&pageSize=40&seller_type[]=pccomponentes_seller&offer_promotional_price_from=200&offer_promotional_price_to={1}"
##############

OPTIMAL_COLOR = "\033[38;5;35m"
MORE_COLOR = "\033[38;5;196m"
LESS_COLOR = "\033[38;5;40m"
RESET_COLOR = "\033[0m"
HISTORY_FILENAME = "history.json"

def main():
    # exit gracefully
    signal.signal(signal.SIGINT, exitGracefully)
    signal.signal(signal.SIGTERM, exitGracefully)
    # history
    historyFile = open(HISTORY_FILENAME,"r+")
    history = None
    try:
        history = json.load(historyFile)
    except:
        history = {}
    historyOld = dict(history)
    # scraper
    scraper = cloudscraper.create_scraper()
    pt = PrettyTable()
    pt.field_names = ["Price","Name","Link"]
    pt.align["Price"] = "r"
    while True:
        historyChanged = False
        currentPage = 1 # pageSize > 40 returns an error
        productsFound = 0
        products = []
        while True:
            response = None
            data = None
            try:
                response = scraper.get(TARGET_URL.format(currentPage,MAX_PRICE)).text
                data = json.loads(response)
                if len(data["articles"]) == 0:
                    break
            except:
                print("Something went wrong.")
                break
            productsFound += len(data["articles"])
            for product in data["articles"]:
                if len(product["availability"]) > 0 and any(x in product["name"] for x in TARGET_PRODUCTS):
                    price = float(product["originalPrice"]) if not (product["promotionalPrice"]) else float(product["promotionalPrice"])
                    historyPrice = history.get(product["name"])
                    # save to history
                    if historyPrice:
                        if price < historyPrice:
                            historyChanged = True
                            history[product["name"]] = price
                    else:
                        historyChanged = True
                        history[product["name"]] = price
                    # price delta - uses data from the start
                    historyPriceOld = historyOld.get(product["name"])
                    priceDeltaStr = ""
                    if historyPriceOld:
                        priceDelta = price-historyPriceOld
                        if priceDelta > 0:
                            priceDeltaStr = MORE_COLOR+f"(+{priceDelta:.2f})"+RESET_COLOR
                        elif priceDelta < 0:
                            priceDeltaStr = LESS_COLOR+f"({priceDelta:.2f})"+RESET_COLOR
                    #
                    if [price-OPTIMAL_PRICE[x] for x in range(len(TARGET_PRODUCTS)) if TARGET_PRODUCTS[x] in product["name"]][0] > 0:
                        products.append([priceDeltaStr+str(price),product["name"],link(URL+product["slug"],"Link")])
                    else:
                        products.append([priceDeltaStr+OPTIMAL_COLOR+str(price)+RESET_COLOR,OPTIMAL_COLOR+product["name"]+RESET_COLOR,OPTIMAL_COLOR+link(URL+product["slug"],"Link")+RESET_COLOR])
                        print('\007') # sound alert
            currentPage += 1
        print(f"Filtered through {productsFound} products")
        for p in products:
            pt.add_row(p)
        print(pt)
        print("Last update:", datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        # save history if changed
        if historyChanged:
            historyFile.seek(0)
            json.dump(history,historyFile,indent=4)
            historyChanged = False
        if LOOP > 0:
            pt.clear_rows()
            time.sleep(LOOP)
            os.system('cls' if os.name=='nt' else 'clear')

def exitGracefully(x,y):
    exit()

# https://stackoverflow.com/a/71309268
def link(uri, label=None): # doesn't work with cmd
    if label is None: 
        label = uri
    parameters = ''
    # OSC 8 ; params ; URI ST <name> OSC 8 ;; ST 
    escape_mask = '\033]8;{};{}\033\\{}\033]8;;\033\\'
    return escape_mask.format(parameters, uri, label)

main()