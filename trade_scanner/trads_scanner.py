import yfinance as yf
import pandas as pd
import ta

# Define the parameters
cci_period = 20
sma_periods = [20, 50, 150, 200]
market_cap_threshold = 1e9  # 1 billion dollars

# Define weights for each indicator
weights = {
    'CCI': 0.2,
    'RSI': 0.1,
    'MACD': 0.2,
    'BB': 0.1,
    'ATR': 0.1,
    'Stoch': 0.1,
    'EMA': 0.2
}

# Load the S&P 500 tickers
sp500_tickers = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol'].tolist()
total_tickers = len(sp500_tickers)

# Function to get stock data and calculate required metrics
def get_stock_data(tickers):
    results = []
    for index, ticker in enumerate(tickers, start=1):
        try:
            formatted_ticker = ticker.replace('.', '-')
            stock_data = yf.download(formatted_ticker, period='1y', interval='1d')
            if stock_data.empty:
                continue

            stock_info = yf.Ticker(formatted_ticker).info
            market_cap = stock_info.get('marketCap', 0)
            if market_cap < market_cap_threshold:
                continue

            # Calculate CCI
            stock_data['CCI'] = ta.trend.CCIIndicator(high=stock_data['High'], low=stock_data['Low'], close=stock_data['Close'], window=cci_period).cci()

            # Calculate SMAs
            for period in sma_periods:
                stock_data[f'SMA_{period}'] = stock_data['Close'].rolling(window=period).mean()

            # Calculate RSI
            stock_data['RSI'] = ta.momentum.RSIIndicator(close=stock_data['Close'], window=14).rsi()

            # Calculate MACD
            macd = ta.trend.MACD(close=stock_data['Close'])
            stock_data['MACD'] = macd.macd()
            stock_data['MACD_Signal'] = macd.macd_signal()
            stock_data['MACD_Diff'] = macd.macd_diff()

            # Calculate Bollinger Bands
            bb = ta.volatility.BollingerBands(close=stock_data['Close'], window=20, window_dev=2)
            stock_data['BB_High'] = bb.bollinger_hband()
            stock_data['BB_Low'] = bb.bollinger_lband()

            # Calculate Average True Range
            stock_data['ATR'] = ta.volatility.AverageTrueRange(high=stock_data['High'], low=stock_data['Low'], close=stock_data['Close'], window=14).average_true_range()

            # Calculate Stochastic Oscillator
            stoch = ta.momentum.StochasticOscillator(high=stock_data['High'], low=stock_data['Low'], close=stock_data['Close'], window=14, smooth_window=3)
            stock_data['Stoch_%K'] = stoch.stoch()
            stock_data['Stoch_%D'] = stoch.stoch_signal()

            # Calculate EMAs
            stock_data['EMA_12'] = stock_data['Close'].ewm(span=12, adjust=False).mean()
            stock_data['EMA_26'] = stock_data['Close'].ewm(span=26, adjust=False).mean()

            # Calculate required metrics
            last_close = stock_data['Close'].iloc[-1]
            cci_value = stock_data['CCI'].iloc[-1]
            rsi_value = stock_data['RSI'].iloc[-1]
            macd_value = stock_data['MACD'].iloc[-1]
            macd_signal_value = stock_data['MACD_Signal'].iloc[-1]
            macd_diff_value = stock_data['MACD_Diff'].iloc[-1]
            bb_high_value = stock_data['BB_High'].iloc[-1]
            bb_low_value = stock_data['BB_Low'].iloc[-1]
            atr_value = stock_data['ATR'].iloc[-1]
            stoch_k_value = stock_data['Stoch_%K'].iloc[-1]
            stoch_d_value = stock_data['Stoch_%D'].iloc[-1]
            ema_12_value = stock_data['EMA_12'].iloc[-1]
            ema_26_value = stock_data['EMA_26'].iloc[-1]

            average_volume = stock_data['Volume'].mean()
            current_volume = stock_data['Volume'].iloc[-1]
            volume_percentage = ((current_volume - average_volume) / average_volume) * 100

            # Determine previous 3 days trend
            last_3_days = stock_data.tail(3)
            price_trend = last_3_days['Close'] > last_3_days['Open']
            if all(price_trend):
                trend = 'up'
            elif all(~price_trend):
                trend = 'down'
            else:
                trend = 'mixed'

            # Determine if the last day is bullish or bearish
            last_day = stock_data.iloc[-1]
            if last_day['Close'] > last_day['Open']:
                candle_type = 'bullish'
            elif last_day['Close'] < last_day['Open']:
                candle_type = 'bearish'
            else:
                candle_type = 'neutral'

            # Determine if above or below SMAs
            above_sma_20 = 'above' if last_close > stock_data['SMA_20'].iloc[-1] else 'below'
            above_sma_50 = 'above' if last_close > stock_data['SMA_50'].iloc[-1] else 'below'
            above_sma_150 = 'above' if last_close > stock_data['SMA_150'].iloc[-1] else 'below'
            above_sma_200 = 'above' if last_close > stock_data['SMA_200'].iloc[-1] else 'below'

            # Determine volume trend
            if last_3_days['Volume'].iloc[-1] > last_3_days['Volume'].iloc[-2] and last_3_days['Volume'].iloc[-2] > last_3_days['Volume'].iloc[-3]:
                volume_trend = 'up'
            elif last_3_days['Volume'].iloc[-1] < last_3_days['Volume'].iloc[-2] and last_3_days['Volume'].iloc[-2] < last_3_days['Volume'].iloc[-3]:
                volume_trend = 'down'
            else:
                volume_trend = 'mixed'

            # Determine good volume trend
            good_volume_trend = (volume_trend == 'up' or volume_trend == 'down')

            # Normalize indicators for recommendation score
            normalized_cci = (cci_value + 100) / 200  # CCI normalized to 0-1 range
            normalized_rsi = rsi_value / 100  # RSI normalized to 0-1 range
            normalized_macd = (macd_value - macd_signal_value) / 2  # MACD diff normalized to -1 to 1 range
            normalized_bb = (last_close - bb_low_value) / (bb_high_value - bb_low_value)  # BB normalized to 0-1 range
            normalized_stoch = stoch_k_value / 100  # Stochastic %K normalized to 0-1 range
            normalized_ema = (ema_12_value - ema_26_value) / ema_26_value  # EMA diff normalized to 0-1 range

            # Calculate recommendation score
            recommendation_score = (
                weights['CCI'] * normalized_cci +
                weights['RSI'] * normalized_rsi +
                weights['MACD'] * normalized_macd +
                weights['BB'] * normalized_bb +
                weights['ATR'] * (1 / (atr_value + 1)) +  # ATR inversely weighted
                weights['Stoch'] * normalized_stoch +
                weights['EMA'] * normalized_ema
            )

            results.append({
                'Ticker': ticker,
                'Market Cap': market_cap,
                'Last Day Closing Price': last_close,
                'CCI': cci_value,
                'RSI': rsi_value,
                'MACD': macd_value,
                'MACD Signal': macd_signal_value,
                'MACD Diff': macd_diff_value,
                'BB High': bb_high_value,
                'BB Low': bb_low_value,
                'ATR': atr_value,
                'Stoch %K': stoch_k_value,
                'Stoch %D': stoch_d_value,
                'EMA 12': ema_12_value,
                'EMA 26': ema_26_value,
                '% from Average Volume': volume_percentage,
                'Previous 3 Days Trend': trend,
                'Last Day Candle': candle_type,
                'Above SMA 20': above_sma_20,
                'Above SMA 50': above_sma_50,
                'Above SMA 150': above_sma_150,
                'Above SMA 200': above_sma_200,
                'Volume Trend': volume_trend,
                'Good Volume Trend': good_volume_trend,
                'Recommendation Score': recommendation_score
            })
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
        
        print(f"{index} of {total_tickers} completed")

    return results

# Get the stock data
stock_data = get_stock_data(sp500_tickers)

# Create a DataFrame
df_results = pd.DataFrame(stock_data)

# Filter stocks with bullish candle, CCI between 0 and 100, above all SMAs, and trend is up
filtered_stocks = df_results[
    (df_results['Last Day Candle'] == 'bullish') &
    (df_results['CCI'] > 0) & (df_results['CCI'] < 100) &
    (df_results['Above SMA 20'] == 'above') &
    (df_results['Above SMA 50'] == 'above') &
    (df_results['Above SMA 150'] == 'above') &
    (df_results['Above SMA 200'] == 'above') &
    (df_results['Previous 3 Days Trend'] == 'up')
]

# Sort by Market Cap descending and then by Recommendation Score descending
filtered_stocks = filtered_stocks.sort_values(by=['Market Cap', 'Recommendation Score'], ascending=[False, False])

# Display the filtered stocks
print("Stocks with a bullish candle, CCI between 0 and 100, above all SMAs, and trend is up, sorted by Market Cap > Recommendation Score descending:")
print(filtered_stocks)

# Save the DataFrame to a CSV file
filtered_stocks.to_csv('filtered_stocks_data.csv', index=False)

# Print the tickers of the filtered stocks as a comma-separated list
tickers_list = filtered_stocks['Ticker'].tolist()
print("Filtered Tickers:", ",".join(tickers_list))
