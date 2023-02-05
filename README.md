# PccScraper
PcComponentes scraper for graphic cards deals.
Keeps a history of the lowest price for each individual product and shows a delta when the current price is different.  
If your terminal supports ANSI escape codes set ANSI_SUPPORT=True.

Settings:
```
ANSI_SUPPORT = False # whether or not your terminal supports ANSI escape codes (for coloring and links)
MIN_PRICE = 200
MAX_PRICE = 620
TARGET_PRODUCTS = ["3080","3070 Ti","6800"]
OPTIMAL_PRICE = [550,400,550]
AVAILABLE_ONLY = False
LOOP = 60*5 # 0 - run once; > 0 - run every X seconds
```
