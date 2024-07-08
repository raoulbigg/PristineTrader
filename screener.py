from PristineScreener.pristinescreener import *
from PristineScreener.marketoverview.symbols import *
import datetime
import time


#Get all US markets for 1d scan
USsymbols = Symbols().USsymbols()


while 1 > 0:
	now = datetime.datetime.now()

	#Start 1d screener
	if (now.now().hour == 10 and now.now().minute == 19):
		screener = Screener(tickers=USsymbols[1:200], timeframe="1d").start_stock_screener()
		print('done')
		time.sleep(10)
#screener takes ~30min to finish
