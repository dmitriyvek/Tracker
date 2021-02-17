from enum import Enum, unique
from functools import partial

from loguru import logger


@unique
class LogLevelEnum(Enum):
    '''Variants of global log leveling'''
    trace = logger.level('TRACE')
    debug = logger.level('DEBUG')
    info = logger.level('INFO')
    success = logger.level('SUCCESS')
    warning = logger.level('WARNING')
    error = logger.level('ERROR')
    critical = logger.level('CRITICAL')


def exact_level_only(record, level: int, global_level: int) -> bool:
    '''Passing only logs with a specified level and if this level is greater then global log level'''
    record_level = record['level'].no
    return record_level == level and record_level >= global_level


def setup_logger(global_log_level: str):
    global_log_level = LogLevelEnum[global_log_level].value.no

    # remove default console logging
    logger.remove()
    logger.add('/home/dmitriy/1programming/aiohttp-start/tracker/backend/log/info.log',
               enqueue=True, rotation='100 MB', compression='zip', level='INFO',
               filter=partial(exact_level_only,
                              level=LogLevelEnum.info.value.no,
                              global_level=global_log_level)
               )
    logger.add('/home/dmitriy/1programming/aiohttp-start/tracker/backend/log/error.log',
               enqueue=True, rotation='100 MB', compression='zip', level='ERROR',
               filter=partial(exact_level_only,
                              level=LogLevelEnum.error.value.no,
                              global_level=global_log_level)
               )

    return logger


async def close_logger(app):
    await app['logger'].complete()
