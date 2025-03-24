from datetime import datetime
import logging
import os
from config import BASE_DIR


def get_logger(name: str):
    if not os.path.exists('logs'):
        os.makedirs('logs')
    # %(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s
    # Configure the root logger
    now = datetime.now()
    safe_timestamp = now.strftime('%Y-%m-%d_%H')
    logging.basicConfig(
        format='%(levelname)s (%(asctime)s): %(module)s | %(funcName)s : %(message)s (line: %(lineno)d) [%(filename)s]',
        datefmt='%I:%M:%S %p',
        filename=BASE_DIR / f'logs/{safe_timestamp}-scraper.log',
        filemode='a+',
        level=logging.INFO
        # level=logging.DEBUG
    )
    # Get a specific logger with the given name
    return logging.getLogger(name)