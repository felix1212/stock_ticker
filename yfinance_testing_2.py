import yfinance as yf
from mystock import validate_symbol

symbol = input("Enter ticker: ").upper()

if validate_symbol(symbol):
    try:
        ticker = yf.Ticker(symbol) # Initialize the Ticker object
        info = ticker.info
        full_name = info['longName']        
        previous_close = ticker.history(period='2d')['Close'].iloc[0] # Fetch the previous day's closing price
        open_price = ticker.history(period='1d')['Open'].iloc[-1]
        high_price = ticker.history(period='1d')['High'].iloc[-1]
        low_price = ticker.history(period='1d')['Low'].iloc[-1]
        volume = ticker.history(period='1d')['Volume'].iloc[-1]
        latest_price = ticker.history(period='1d', interval='1m')['Close'].iloc[-1] # Fetch the latest market price       
        absolute_change = latest_price - previous_close # Calculate the absolute change       
        percentage_change = (absolute_change / previous_close) * 100 # Calculate the percentage change

        print(f"Ticker: {symbol}")
        print(f"Full Name: {full_name}")
        print(f"Previous Close: ${previous_close:.2f}")
        print(f"Open: ${open_price:.2f}")
        print(f"High: ${high_price:.2f}")
        print(f"Low: ${low_price:.2f}")
        print(f"Volume: {volume}")
        print(f"Latest Price: ${latest_price:.2f}")
        print(f"Change: ${absolute_change:.2f}")
        print(f"Change Percentage: {percentage_change:.2f}%")
    except Exception as e:
        print(f"An error occurred: {e}")
else:
    print(f'{symbol} is not a valid symbol!')



