"""
Useful time functions. 
Author Daniel Sapojnikov, 2023.
"""
import pytz
from datetime import datetime, timezone

UNIX_TIME_FORMAT = "%d/%m/%Y - %H:%M"

def get_unix_time() -> str:
    """
    Calculates UTC time based on Jerusalem timezone.
    
    Returns:
        str: Formatted Current time.
    """
    uni_time = datetime.now(pytz.timezone("Asia/Jerusalem"))
    return uni_time.strftime(UNIX_TIME_FORMAT)