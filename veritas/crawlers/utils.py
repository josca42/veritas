from pathlib import Path
import functools
import logging
from datetime import datetime
from time import sleep


def latest_file_in_folder(folder: Path):
    return max(folder.iterdir(), key=lambda x: x.stat().st_ctime)


def retry(func):
    logger = logging.getLogger(__name__)

    @functools.wraps(func)
    def retry_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            print(e)
            logger.info(e)

            for attempt in range(2, 4):
                sleep_seconds = attempt**2
                sleep(sleep_seconds)

                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(e)
                    logger.info(e)

    return retry_func
