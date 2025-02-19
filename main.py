import sys
import configparser
import os
import time
from datetime import datetime, timedelta
from validate import validate_network
from myutil import create_logger, parse_tuple
from validate import validate_symbol
from mystock import get_stock_info, get_stock_graph

###########################
# Environment Preparation #
###########################
# Verify and retrieve config
config_file = 'settings.ini'
try:
    with open(config_file, 'r') as file:
        print(f"Loading configuration from {config_file}...")
except FileNotFoundError as e:
    print(f"Config error: {e}")
    sys.exit(0)
try:
    config = configparser.ConfigParser()
    config.read('settings.ini')
    log_level = config.get("Settings", "log_level")
    symbol_tuple = parse_tuple(config.get("Settings", "symbol"))
    trend_days = int(config.get("Settings","trend_days"))
    graph_path = config.get("Settings", "graph_path")
    refresh_seconds = int(config.get("Settings","refresh_seconds"))
except Exception as e:
    print(f"Config error: {e}")
    sys.exit(0)

# Create logger
logger = create_logger(log_level,__name__)
logger.info("Application started")

# Show configurations
logger.debug(f'Retrieved from settings.ini: symbol_tuple = {symbol_tuple}')
logger.debug(f'Retrieved from settings.ini: trend_days = {trend_days}')
logger.debug(f'Retrieved from settings.ini: graph_path = {graph_path}')
logger.debug(f'Retrieved from settings.ini: refresh_seconds = {refresh_seconds}')

###########################
# Environment Verificaton #
###########################
def verify_env():
    # Validate symbols
    for symbol in symbol_tuple:
        if not validate_symbol(symbol):
            logger.error(f"Symbol '{symbol}' in settings.ini is invalid.")
            sys.exit(0)
        else:
            logger.debug(f'{symbol} symbol verification passed.')
    logger.info(f'Configuration verification passed.')         

    # Verify Network
    if not validate_network():
        logger.error(f"Network verification failed. Please check network connection.")
        sys.exit(0)
    else:
        logger.info('Network verification passed.')

    # Verify Display(?)
    print('MOCK - Display verification passed.')

###########################
#     Send to Display     #
###########################
def send_to_display(symbol,result):
    print(f'MOCK - Sent {symbol} data to Display')


#############################
# Retrieve and display data #
#############################
def process_data():
    # Iterate from symbol tuple
    for symbol in symbol_tuple:
        # Retrieve symbol data
        try:
            result = get_stock_info(symbol)
            if result is not None:
                logger.info(f'Information for {symbol} retrieved.')
                logger.debug(f"Ticker: {symbol}")
                logger.debug(f"Full Name: {result[0]}")
                logger.debug(f"Previous Close: ${result[1]:.2f}")
                logger.debug(f"Open: ${result[2]:.2f}")
                logger.debug(f"High: ${result[3]:.2f}")
                logger.debug(f"Low: ${result[4]:.2f}")
                logger.debug(f"Volume: {result[5]}")
                logger.debug(f"Latest Price: ${result[6]:.2f}")
                logger.debug(f"Change: ${result[7]:.2f}")
                logger.debug(f"Change Percentage: {result[8]:.2f}%")
        except Exception as e:
            logger.error(f'{symbol} info retrieval error: {e}')

        # Generate trend graph
        end_date = datetime.now()
        start_date = end_date - timedelta(days=trend_days)
        try:
            get_stock_graph(symbol,start_date.strftime("%Y-%m-%d"),end_date.strftime("%Y-%m-%d"),graph_path)
            if os.path.isfile(f'{graph_path}{symbol}.png'):
                logger.info(f'{graph_path}{symbol}.png generated.')
        except Exception as e:
            logger.error(f"Graph generation error: {e}")

        # Send to display
        try:
            send_to_display(symbol,result)
        except Exception as e:
            logger.error(f"Data display error: {e}")

        # Pause by defined time period
        print(f'MOCK - Pause for {refresh_seconds} seconds to display {symbol} data')
        time.sleep(refresh_seconds)

if __name__ == "__main__":
    verify_env()
    while True:
        process_data()
        
        
