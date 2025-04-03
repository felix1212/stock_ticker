import pandas_market_calendars as mcal
from datetime import datetime
import pytz

def get_stock_calendar(market_name: str, local_timezone: str) -> bool:
    """
    Check if the specified stock market is currently open based on the local timezone.

    Parameters:
    - market_name (str): The name of the stock market (e.g., 'NYSE', 'NASDAQ').
    - local_timezone_str (str): The local timezone as a string (e.g., 'Asia/Shanghai').

    Returns:
    - bool: True if the market is open, False otherwise.
    """
    try:
        # Get the market calendar
        market_calendar = mcal.get_calendar(market_name.upper())
    except Exception as e:
        raise ValueError(f"Market '{market_name}' is not recognized. Error: {e}")

    try:
        # Define the local timezone
        local_timezone = pytz.timezone(local_timezone)
    except Exception as e:
        raise ValueError(f"Timezone '{local_timezone}' is not recognized. Error: {e}")

    # Get the current time in the local timezone
    local_time = datetime.now(local_timezone)

    # Convert local time to UTC
    utc_time = local_time.astimezone(pytz.utc)

    # Get the market schedule for today in UTC
    schedule = market_calendar.schedule(start_date=utc_time.date(), end_date=utc_time.date())

    if schedule.empty:
        return False

    # Check if the market is open at the current UTC time
    is_open = market_calendar.open_at_time(schedule, utc_time)

    return is_open
