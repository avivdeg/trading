import pandas as pd
import yfinance as yf

# Define the tickers
spx_ticker = '^GSPC'  # S&P 500 Index
voo_ticker = 'VOO'    # Vanguard S&P 500 ETF

# Download historical data for SPX and VOO
spx_data = yf.download(spx_ticker, start='2023-01-01', end='2024-01-01')
voo_data = yf.download(voo_ticker, start='2023-01-01', end='2024-01-01')

# Ensure both dataframes are aligned by date
spx_data = spx_data['Close']
voo_data = voo_data['Close']

# Combine the data into a single dataframe
combined_data = pd.DataFrame({'SPX': spx_data, 'VOO': voo_data}).dropna()

# Calculate the correlation between SPX and VOO
correlation = combined_data.corr().loc['SPX', 'VOO']

# Print the correlation
print(f'The correlation between SPX and VOO is: {correlation}')

# Get the current prices
current_spx_price = spx_data.iloc[-1]
current_voo_price = voo_data.iloc[-1]
print(f'Current SPX price: {current_spx_price}')
print(f'Current VOO price: {current_voo_price}')

# Calculate the price of VOO when SPX is 5073.21
# This simple linear regression assumes a linear relationship between SPX and VOO
slope, intercept = pd.Series(spx_data).cov(voo_data) / pd.Series(spx_data).var(), voo_data.mean() - pd.Series(spx_data).cov(voo_data) / pd.Series(spx_data).var() * spx_data.mean()
estimated_voo_price = slope * 5073.21 + intercept
print(f'Estimated VOO price when SPX is 5073.21: {estimated_voo_price}')
