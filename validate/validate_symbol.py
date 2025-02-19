import yfinance as yf

def validate_symbol(symbol):
    try:
        ticker = yf.Ticker(symbol) # Initialize the Ticker object
        info = ticker.info
        if 'symbol' in info:
            if info['symbol'] == symbol:
                return True
        else:
            return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False