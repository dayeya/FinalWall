import pytz
import time
from datetime import datetime


UNIX_TIME_FORMAT = "%d/%m/%Y, %H:%M:%S"


def get_unix_time(tz: str) -> str:
    """
    Calculates UTC time based on Jerusalem timezone.
    :returns: formatted current time.
    """
    uni_time = datetime.now(pytz.timezone(tz))
    return uni_time.strftime(UNIX_TIME_FORMAT)


def get_epoch_time() -> float:
    """
    Time in seconds since the Epoch
    :return:
    """
    return time.time()
