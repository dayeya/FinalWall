"""
Author: Daniel Sapojnikov, 2023.
Useful time functions. 
"""
import pytz
from datetime import datetime, timezone

UNIX_TIME_FORMAT = "%d/%m/%Y - %H:%M"

def get_unix_time() -> str:
    """
    Calculates UTC time based on Jerusalem timezone.
    
    Returns:
        str: Formatted current time.
    """
    uni_time = datetime.now(pytz.timezone("Asia/Jerusalem"))
    return uni_time.strftime(UNIX_TIME_FORMAT)

def date_formatted_data(data: str) -> str:
    """
    Crafts a formatted string with a unix time.

    Args:
        data - str: data to log.

    Returns:
        str: A new formatted string.
    """
    return f'{get_unix_time()}, {data}'