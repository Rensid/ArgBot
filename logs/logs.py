import logging
from functools import wraps


def configure_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        filename="my_logging.log",
        format="%(levelname)-7s (%(asctime)s): %(message)s (Line: %(lineno)d [%(filename)s])",
        datefmt="%d/%m/%Y %I:%M:%S",
        encoding="utf-8",
        filemode="w",
    )


def log_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        logging.info(
            "Вызов функции %s с аргументами: %s, %s", func.__name__, args, kwargs
        )
        try:
            result = func(*args, **kwargs)
            logging.info(
                "Функция %s завершила работу с результатом: %s", func.__name__, result
            )
        except Exception:
            logging.exception(
                "Произошло исключение при выполнении функции %s", func.__name__
            )
            raise
        return result

    return wrapper


configure_logging()
