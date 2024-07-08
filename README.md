# Pristine Trading - Screener + Trade Tracking

###### Stock screener that:

- Gets all US stocks (NYSE and NASDAQ).
- Receives **live** and **past** OHLC data for stocks using Yahoo yfinance lib.
- Calculates moving averages(10sma, 20sma & 200ma) and bars position.
- Close > Open.  
- Close > rising 20sma.  
- Rising 10sma > rising 20sma.   
- Plots candlestick graphs using plotly.  
- Places the graphs in a Flask application.  



##### Trade Tracker:

- Use Trade Tracker to as a trade tracking spreadsheat.  
- Automatically calculates metrics.  
- Equity Curve.  
- Set table filters.  
- Add new trades to the spreadsheet.  
- Reads .csv.  


# How to run screener and tradetracker:
```
python3 screener.py
cd TradeTrack/; flask run
```


