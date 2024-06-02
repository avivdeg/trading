import yfinance as yf
import pandas as pd
from ta.trend import SMAIndicator, CCIIndicator
from ta.momentum import RSIIndicator

# Step 1: Retrieve S&P 500 stock symbols
sp500_symbols = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol'].tolist()

# Initialize a list to store stocks meeting the criteria
qualified_stocks = []

# Function to check conditions for each stock
def check_stock(symbol):
    try:
        # Retrieve historical data
        stock_data = yf.download(symbol, period="6mo", interval="1d")
        
        # Calculate the 20 SMA
        stock_data['20_SMA'] = SMAIndicator(stock_data['Close'], window=20).sma_indicator()
        
        # Calculate the CCI
        stock_data['CCI'] = CCIIndicator(stock_data['High'], stock_data['Low'], stock_data['Close'], window=20).cci()
        
        # Check if the stock is in an uptrend
        uptrend = stock_data['Close'][-1] > stock_data['Close'][-20]
        
        # Check distance from 20 SMA
        price_above_20_SMA = stock_data['Close'][-1] > stock_data['20_SMA'][-1]
        distance_from_20_SMA = (stock_data['Close'][-1] - stock_data['20_SMA'][-1]) / stock_data['20_SMA'][-1]
        
        # Check CCI conditions
        cci_condition = (-100 <= stock_data['CCI'][-1] <= 100) and (stock_data['CCI'][-1] > stock_data['CCI'][-2])
        
        # Check if the last day candle is bullish
        bullish_candle = stock_data['Close'][-1] > stock_data['Open'][-1]
        
        # Check all conditions
        if (uptrend and (distance_from_20_SMA > 0 or (price_above_20_SMA and abs(distance_from_20_SMA) < 0.03))
            and cci_condition and bullish_candle):
            qualified_stocks.append(symbol)
    except Exception as e:
        print(f"Error processing {symbol}: {e}")

# Iterate over each stock symbol and check conditions
for symbol in sp500_symbols:
    check_stock(symbol)
    print(f"Checked {symbol}")

# Step 7: Filter stocks with a market cap over $1 billion
filtered_stocks = []
for symbol in qualified_stocks:
    stock_info = yf.Ticker(symbol).info
    if stock_info['marketCap'] > 1e9:
        filtered_stocks.append(symbol)

# Print final results
print("Stocks meeting the criteria with market cap over $1 billion:")
print(filtered_stocks)
