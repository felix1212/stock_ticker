import sys
import configparser
import os
import glob
import time
from datetime import datetime, timedelta
from validate import validate_network
from myutil import create_logger, parse_tuple, get_weather
from validate import validate_symbol
from mystock import get_stock_info, get_stock_graph, get_stock_calendar
from waveshare_epd import epd7in3e
from PIL import Image,ImageDraw,ImageFont


"""
Environment Preparation
"""
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
    timezone = config.get("Settings", "timezone")
    market_name = config.get("Settings", "market_name")
    location = config.get("Settings", "location")
    openweather_api_key = config.get("Settings", "openweather_api_key")
    weather_refresh_hour = config.get("Settings","weather_refresh_hour")
except Exception as e:
    print(f"Config error: {e}")
    sys.exit(0)

# Create Screen Object
epd = epd7in3e.EPD()

# Create logger
logger = create_logger(log_level,__name__)
logger.info("Application started")

"""
Environment Verification
"""
def verify_env():
    # Validate symbols
    for symbol in symbol_tuple:
        if not validate_symbol(symbol):
            logger.error(f"Symbol '{symbol}' in settings.ini is invalid.")
            sys.exit(0)
        else:
            logger.debug(f'{symbol} symbol verification passed.')
    logger.info(f'Configuration verification passed.')

    # Verify Timezone
    try:
        get_stock_calendar(market_name, timezone)
    except Exception as e:
        logger.error(f"{market_name} or {timezone} verification failed. Error: {e}")
        sys.exit(0)

    # Verify Weather
    try:
        get_weather(openweather_api_key,location)
    except Exception as e:
        logger.error(f"Weather retrieval failed. Error: {e}")
        sys.exit(0)

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


"""
Send Data To Display
"""
def send_to_display(symbol,full_name,previous_close,open,high,low,volume,latest_price,change,change_percentage,market_name,timezone,temperature):
    logger.info(f'Sent {symbol} data to Display')
    # Setup fonts
    full_name_font = ImageFont.truetype(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fonts', light_font), 35)
    symbol_font = ImageFont.truetype(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fonts', bold_font), 50)
    latest_price_font = ImageFont.truetype(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fonts', bold_font), 110)
    market_font = ImageFont.truetype(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fonts', light_font), 25)
    change_font = ImageFont.truetype(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fonts', light_font), 25)
    detail_font = ImageFont.truetype(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fonts', light_font), 25)
    datetime_font = ImageFont.truetype(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fonts', light_font), 18)
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
        draw.text((580,130), f'{change} ({change_percentage}%)', font = change_font, fill = epd.RED)
    else:
        draw.polygon(up_triangle_coords,outline = epd.GREEN,fill = epd.GREEN)
        draw.text((580,130), f'{change} ({change_percentage}%)', font = change_font, fill = epd.GREEN)
    logger.debug(f'Added triangle to ImageDraw')

    # Add text information
    draw.text((130,35), symbol, font = symbol_font, fill = epd.BLACK)
    draw.text((300,43), full_name, font = full_name_font, fill = epd.BLACK)
    draw.text((45,105), latest_price, font = latest_price_font, fill = epd.BLACK)
    if get_stock_calendar(market_name, timezone):
        draw.text((580,167), 'Market Open', font = market_font, fill = epd.GREEN)
    else:
        draw.text((580,167), 'Market Closed', font = market_font, fill = epd.RED)
    detailed_text = (
        f"Previous Close: ${previous_close}\n"
        f"Open: ${open}\n"
        f"High: ${high}\n"
        f"Low: ${low}\n"
        f"Volume: {volume}"
    )
    draw.text((47,257), detailed_text, font = detail_font, fill = epd.BLACK)
    draw.text((632,20), f'{datetime.now().strftime("%a, %b %d")} {datetime.now().strftime("%H:%M")}', font = datetime_font, fill = epd.BLACK)
    draw.text((730,43), f'{temperature}°C', font = datetime_font, fill = epd.BLACK)
    logger.debug(f'Added detailed text to ImageDraw')
    
    # Add image
    overlay_image = Image.open(f'{graph_path}{symbol}.bmp')
    image.paste(overlay_image, (350, 225))
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

"""
Main
"""
if __name__ == "__main__":
    verify_env()
    last_weather_time = None
    cached_weather_data = None
    while True:
        try:
            # Iterate from symbol tuple
                for symbol in symbol_tuple:
                    # get data for each symbol
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

                    # Generate trend graph
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=trend_days)
                    try:
                        get_stock_graph(symbol,start_date.strftime("%Y-%m-%d"),end_date.strftime("%Y-%m-%d"),graph_path,resized_trend_resolution)
                        if os.path.isfile(f'{graph_path}{symbol}.bmp'):
                            logger.info(f'{graph_path}{symbol}.bmp generated.')
                    except Exception as e:
                        logger.error(f"Graph generation error: {e}")
                    
                    # get weather data per time period
                    current_time = datetime.now()
                    if last_weather_time is None or current_time - last_weather_time > timedelta(hours=weather_refresh_hour):
                        try:
                            temperature = get_weather(openweather_api_key,location)
                            last_temperature_retrieval_time = datetime.now()
                        except Exception as e:
                            logger.error(f"Weather retrieval failed. Error: {e}")

                    # display data
                    send_to_display(symbol,full_name,previous_close,open,high,low,volume,latest_price,change,change_percentage,market_name,timezone,str(round(temperature)))

                    # Pause by defined time period
                    logger.info(f'Pause for {refresh_seconds} seconds to display next symbol data')
                    time.sleep(refresh_seconds)

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