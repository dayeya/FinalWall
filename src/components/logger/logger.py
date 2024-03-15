import logging
from fmt_time import date_formatted_data

FORMAT = "%(levelname)s: %(message)s"

class Logger(logging.Logger):
    def __init__(self, name: str, depth: int=logging.DEBUG) -> None:
        super().__init__(name, depth)

        self.__formatter = logging.Formatter(FORMAT)
        stdio_handler = logging.StreamHandler()
        stdio_handler.setLevel(depth)
        stdio_handler.setFormatter(self.__formatter)
        
        self.addHandler(stdio_handler)
        
    def log_date(self, data: str) -> None:
        self.info(date_formatted_data(data))
        
    def set_format(self, fmt: str) -> None:
        self.__formatter = logging.Formatter(fmt)