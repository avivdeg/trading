import yfinance as yf
import pandas as pd

# Function to check if a stock meets the criteria
def check_stock(ticker):
    try:
        stock = yf.Ticker(ticker)
        
        # Fetch market cap and filter out stocks with market cap less than 1 billion
        info = stock.info
        market_cap = info.get('marketCap', 0)
        if market_cap < 1_000_000_000:
            print(f"{ticker}: Market cap less than 1 billion USD")
            return None, None, 0

        hist = stock.history(period="1y")
        
        if len(hist) < 150:
            print(f"{ticker}: Not enough historical data")
            return None, None, 0

        hist['SMA_150'] = hist['Close'].rolling(window=150).mean()

        # Check if SMA_150 is in an uptrend
        if hist['SMA_150'].iloc[-1] <= hist['SMA_150'].iloc[-2]:
            print(f"{ticker}: SMA_150 not in an uptrend")
            return None, None, 0

        # Check if the stock price is up to 3% above the SMA_150
        current_price = hist['Close'].iloc[-1]
        sma_150 = hist['SMA_150'].iloc[-1]
        if current_price <= sma_150 or current_price > sma_150 * 1.03:
            print(f"{ticker}: Current price not within 3% above the SMA_150")
            return None, None, 0

        # Check if the current volume is above the 50-day average volume and if buyers control the volume
        avg_volume_50 = hist['Volume'].rolling(window=50).mean().iloc[-1]
        current_volume = hist['Volume'].iloc[-1]
        if current_volume > avg_volume_50 and hist['Close'].iloc[-1] > hist['Open'].iloc[-1]:
            return ticker, True, market_cap  # Meets additional volume criteria
        else:
            return ticker, False, market_cap  # Does not meet additional volume criteria

    except Exception as e:
        print(f"{ticker}: {e}")
        return None, None, 0

# Fetch the list of S&P 500 companies from Wikipedia
url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
table = pd.read_html(url, header=0)
sp500_table = table[0]
sp500_tickers = sp500_table['Symbol'].tolist()

# Preprocess tickers to handle special characters
sp500_tickers = [ticker.replace('.', '-') for ticker in sp500_tickers]

# Scan the stocks
selected_stocks = []
high_volume_stocks = []
total_stocks = len(sp500_tickers)
print(f"Total stocks to scan: {total_stocks}")

for idx, ticker in enumerate(sp500_tickers):
    print(f"Processing {idx + 1}/{total_stocks}: {ticker}")
    result, high_volume, market_cap = check_stock(ticker)
    if result:
        selected_stocks.append((result, market_cap))
        if high_volume:
            high_volume_stocks.append((result, market_cap))

# Sort the lists by market cap in descending order
selected_stocks.sort(key=lambda x: x[1], reverse=True)
high_volume_stocks.sort(key=lambda x: x[1], reverse=True)

# Save the selected stocks to CSV files
selected_output_file = "selected_stocks.csv"
high_volume_output_file = "high_volume_stocks.csv"

pd.DataFrame(selected_stocks, columns=["Ticker", "Market Cap"]).to_csv(selected_output_file, index=False)
pd.DataFrame(high_volume_stocks, columns=["Ticker", "Market Cap"]).to_csv(high_volume_output_file, index=False)

print("Stocks that meet the criteria:")
print([stock[0] for stock in selected_stocks])
print(f"List of selected stocks saved to {selected_output_file}")

print("Stocks that also have high buyers' volume:")
print([stock[0] for stock in high_volume_stocks])
print(f"List of high volume stocks saved to {high_volume_output_file}")
