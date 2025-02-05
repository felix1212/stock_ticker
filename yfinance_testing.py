import yfinance as yf

# Define the ticker symbol
ticker_symbol = 'AAPL'  # Example: Apple Inc.

# Initialize the Ticker object
ticker = yf.Ticker(ticker_symbol)

# Fetch the current market price
current_price = ticker.history(period='1d', interval='1m')['Close'].iloc[-1]

print(f"The current price of {ticker_symbol} is ${current_price:.2f}")
