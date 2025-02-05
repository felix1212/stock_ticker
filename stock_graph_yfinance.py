import yfinance as yf
import matplotlib.pyplot as plt

# Define the ticker symbol
ticker_symbol = 'AAPL'

# Fetch the data
stock_data = yf.download(ticker_symbol, start='2024-01-31', end='2025-01-31')

print(stock_data)

plt.figure(figsize=(10, 5))
plt.plot(stock_data.index, stock_data['Close'], label='Close Price')
plt.title(f'{ticker_symbol} Stock Price')
plt.xlabel('Date')
plt.ylabel('Price (USD)')
plt.legend()
plt.grid(True)
plt.show()
