import sys
import configparser
import os
import glob
import time
from datetime import datetime, timedelta
from validate import validate_network
from myutil import create_logger, parse_tuple
from validate import validate_symbol
from mystock import get_stock_info, get_stock_graph
from waveshare_epd import epd7in3e
from PIL import Image,ImageDraw,ImageFont

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
    main_font = config.get("Settings", "main_font")
    bold_font = config.get("Settings", "bold_font")
    light_font = config.get("Settings", "light_font")
    resized_trend_resolution = eval(config.get("Settings", "resized_trend_resolution"))
except Exception as e:
    print(f"Config error: {e}")
    sys.exit(0)

# Create Screen Object
epd = epd7in3e.EPD()

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

    # Verify Display
    epd.init()
    epd.Clear()
    logger.info('Display initialized.')

###########################
#     Send to Display     #
###########################
def send_to_display(symbol,full_name,previous_close,open,high,low,volume,latest_price,change,change_percentage):
    logger.info(f'Sent {symbol} data to Display')
    # Setup fonts
    full_name_font = ImageFont.truetype(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fonts', light_font), 35)
    symbol_font = ImageFont.truetype(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fonts', bold_font), 50)
    latest_price_font = ImageFont.truetype(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fonts', bold_font), 110)
    market_font = ImageFont.truetype(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fonts', light_font), 25)
    change_font = ImageFont.truetype(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fonts', light_font), 25)
    detail_font = ImageFont.truetype(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fonts', light_font), 25)
    logger.debug(f'Fonts set')
    image = Image.new('RGB',(800,480),'white')
    logger.debug(f'Image object created')
    draw = ImageDraw.Draw(image)
    logger.debug(f'ImageDraw object created')

    # Draw the up/down triangle
    x, y = 49, 43
    up_triangle_coords = [
        (x, y + 50),        # Bottom-left corner
        (x + 32, y),        # Top-center corner
        (x + 65, y + 50)    # Bottom-right corner
    ]
    logger.debug(f'up_triangle_coords')

    down_triangle_coords = [
    (x, y),            # Top-left corner (previously bottom-left)
    (x + 32, y + 50),  # Bottom-center corner (previously top-center)
    (x + 65, y)        # Top-right corner (previously bottom-right)
    ]
    logger.debug(f'down_triangle_coords')
    if (change < 0 and change_percentage < 0):
        draw.polygon(down_triangle_coords,outline = epd.RED,fill = epd.RED)
        draw.text((580,124), f'{change} ({change_percentage}%)', font = change_font, fill = epd.RED)
    else:
        draw.polygon(up_triangle_coords,outline = epd.GREEN,fill = epd.GREEN)
        draw.text((580,124), f'{change} ({change_percentage}%)', font = change_font, fill = epd.GREEN)
    logger.debug(f'Added triangle to ImageDraw')

    # Add text information
    draw.text((130,35), symbol, font = symbol_font, fill = epd.BLACK)
    draw.text((300,43), full_name, font = full_name_font, fill = epd.BLACK)
    draw.text((45,92), latest_price, font = latest_price_font, fill = epd.BLACK)
    draw.text((580,161), 'Market Closed', font = market_font, fill = epd.BLACK)
    detailed_text = (
        f"Previous Close: ${previous_close}\n"
        f"Open: ${open}\n"
        f"High: ${high}\n"
        f"Low: ${low}\n"
        f"Volume: {volume}"
    )
    draw.text((47,257), detailed_text, font = detail_font, fill = epd.BLACK)
    logger.debug(f'Added detailed text to ImageDraw')
    
    # Add image
    overlay_image = Image.open(f'{graph_path}{symbol}.bmp')
    image.paste(overlay_image, (370, 235))
    logger.debug(f'Added graph to ImageDraw')

    # Show image
    # image.show()
    epd.display(epd.getbuffer(image))

# self.BLACK  = 0x000000   #   0000  BGR
# self.WHITE  = 0xffffff   #   0001
# self.GREEN  = 0x00ff00   #   0010
# self.BLUE   = 0xff0000   #   0011
# self.RED    = 0x0000ff   #   0100
# self.YELLOW = 0x00ffff   #   0101
# self.ORANGE = 0x0080ff   #   0110

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
                full_name = result[0]
                previous_close = str(f'{result[1]:.2f}')
                open = str(f'{result[2]:.2f}')
                high = str(f'{result[3]:.2f}')
                low = str(f'{result[4]:.2f}')
                volume = str(f'{result[5]}')
                latest_price = str(f'{result[6]:.2f}')
                change = round(result[7],2)
                change_percentage = round(result[8],2)
                logger.info(f'Information for {symbol} retrieved.')
                logger.debug(f"Ticker: {symbol}")
                logger.debug(f"Full Name: {full_name}")
                logger.debug(f"Previous Close: ${previous_close}")
                logger.debug(f"Open: ${open}")
                logger.debug(f"High: ${high}")
                logger.debug(f"Low: ${low}")
                logger.debug(f"Volume: {volume}")
                logger.debug(f"Latest Price: ${latest_price}")
                logger.debug(f"Change: ${change}")
                logger.debug(f"Change Percentage: {change_percentage}%")
        except Exception as e:
            logger.error(f'{symbol} info retrieval error: {e}')

        # Generate trend graph
        end_date = datetime.now()
        start_date = end_date - timedelta(days=trend_days)
        try:
            get_stock_graph(symbol,start_date.strftime("%Y-%m-%d"),end_date.strftime("%Y-%m-%d"),graph_path,resized_trend_resolution)
            if os.path.isfile(f'{graph_path}{symbol}.bmp'):
                logger.info(f'{graph_path}{symbol}.bmp generated.')
        except Exception as e:
            logger.error(f"Graph generation error: {e}")

        # Send to display
        try:
            send_to_display(symbol,full_name,previous_close,open,high,low,volume,latest_price,change,change_percentage)
        except Exception as e:
            logger.error(f"Data display error: {e}")

        # Pause by defined time period
        logger.info(f'Pause for {refresh_seconds} seconds to display next symbol data')
        time.sleep(refresh_seconds)


if __name__ == "__main__":
    verify_env()
    while True:
        try:
            process_data()
        except KeyboardInterrupt:
            logger.debug("ctrl + c:")
            logger.debug(f'Removing all files in {graph_path}...')
            for file in glob.glob(os.path.join(str(f'{graph_path}'), "*")):
                os.remove(file)
            logger.info(f'Files in {graph_path} are removed')
            logger.debug(f'Clearing display content...')
            epd.Clear()
            logger.info(f'Display cleared')
            epd.sleep()
            logger.info(f'Display in sleeping mode')
            epd7in3e.epdconfig.module_exit(cleanup=True)
            logger.info('epdconfig.module_exit')
            break
        
        
