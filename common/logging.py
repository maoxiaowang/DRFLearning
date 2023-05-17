import logging
import threading
import warnings
from logging import LogRecord

from django.conf import settings

__all__ = [
    'loggers'
]

local = threading.local()


class RequestIDFilter(logging.Filter):

    def filter(self, record: LogRecord) -> bool:
        record.request_id = getattr(local, 'request_id', 'none')
        return True


class Loggers:
    """
    Intro:

    等级（level）从低到高为：debug，info，warning，error，critical
    logger的等级配置决定了该logger能记录的最低等级，而每个handler可以记录的日志等级即为其和logger的等级的交集。

    举例，部分配置如下：
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
            },
            'service': {
                'level': 'CRITICAL',
                'class': 'logging.handlers.WatchedFileHandler',
            }
        },
        'loggers': {
            'service': {
                'handlers': ['service', 'console'],
                'level': 'ERROR',
                'propagate': False
            },
        }

    service配置的等级为ERROR，意味着所有handler只能记录等级在ERROR及以上的日志，即error和critical。
    那么将从console输出error和critical的日志，而在service中仅记录critical等级的日志。

    ----

    Usage:

    from common.logging import loggers

    logger = loggers.task
    logger.error('Something to log')

    """
    apiv1: logging.Logger
    task: logging.Logger
    django: logging.Logger  # just console

    def __init__(self):
        logger_names = settings.LOGGING.get('loggers').keys()
        for name in self.__annotations__.keys():
            dotted_name = name.replace('_', '.')
            if name not in logger_names and dotted_name not in logger_names:
                warnings.warn(f'The logger name "{name}" is not defined in settings')

    def __getattr__(self, item):
        if item not in self.__annotations__.keys():
            warnings.warn(f'You are trying to access a logger "{item}" not defined in Logger')
        return logging.getLogger(item)


loggers = Loggers()
