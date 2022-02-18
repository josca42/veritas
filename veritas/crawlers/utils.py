from pathlib import Path
import functools
import logging
from datetime import datetime
from time import sleep
from gql.transport.exceptions import TransportQueryError


def latest_file_in_folder(folder: Path):
    return max(folder.iterdir(), key=lambda x: x.stat().st_ctime)


def error_handling(func):
    logger = logging.getLogger(__name__)

    @functools.wraps(func)
    def retry_func(*args, **kwargs):
        """
        Decorator that in case of a TransportQueryError returns
        the error. For all other errors the decorator retries the
        same call 2 times with a growing sleep interval in between.

        All errors get printed and logged
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e)
            logger.info(e)

            if isinstance(e, TransportQueryError):
                return TransportQueryError
            else:
                for attempt in range(2, 4):
                    sleep_seconds = attempt**2
                    sleep(sleep_seconds)

                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        print(e)
                        logger.info(e)

    return retry_func
