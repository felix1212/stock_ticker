import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import os.path

def get_stock_graph(symbol,start_date,end_date,path):
        stock_data = yf.download(symbol, start=start_date, end=end_date)
        plt.figure(figsize=(10, 5))
        plt.plot(stock_data.index, stock_data['Close'], label='Close Price')
        plt.ylabel('Price (USD)')
        plt.legend()
        #plt.grid(True)
        plt.grid(axis='y', linestyle = '--', linewidth = 0.5, color = '#D9D9D9')
        plt.savefig(f'{path}{symbol}.png', dpi=300, bbox_inches='tight')

if __name__ == "__main__":
    symbol = input("Enter ticker: ").upper()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    try:
        stock_data = yf.download(symbol, start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"))
        print(stock_data)
        plt.figure(figsize=(10, 5))
        plt.plot(stock_data.index, stock_data['Close'], label='Close Price')
        # plt.title(f'{symbol} Stock Price')
        # plt.xlabel('Date')
        plt.ylabel('Price (USD)')
        plt.legend()
        plt.grid(True)
        plt.savefig(f'{symbol}.png', dpi=300, bbox_inches='tight')
        plt.show()
    except Exception as e:
        print(f"An error occurred: {e}")