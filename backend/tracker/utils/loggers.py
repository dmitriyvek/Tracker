import sys
from enum import Enum, unique
from functools import partial
from pathlib import PosixPath

from aiohttp.web_app import Application
from loguru import logger

from tracker.utils.utils import init_logs


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
    return not record['extra'] and record_level == level and record_level >= global_level


def request_log_filter(record, global_level: int) -> bool:
    record_level = record['level'].no
    return 'request_log' in record['extra'] and record_level >= global_level


def setup_logger(
    global_log_level: str,
    error_path: PosixPath,
    info_path: PosixPath,
    request_info_path: PosixPath,
    debug: bool
) -> logger:
    '''Setting up Loguru logger'''
    global_log_level = LogLevelEnum[global_log_level].value.no

    # remove default console logging
    logger.remove()

    if debug:
        logger.add(sys.stderr, enqueue=True,
                   level=LogLevelEnum.debug.value.name,
                   filter=lambda record: record['level'].no >= global_log_level
                   )

    logger.add(info_path,
               enqueue=True, rotation='10 MB', compression='zip',
               level=LogLevelEnum.info.value.name,
               filter=partial(exact_level_only,
                              level=LogLevelEnum.info.value.no,
                              global_level=global_log_level)
               )
    logger.add(request_info_path,
               enqueue=True, rotation='10 MB', compression='zip',
               level=LogLevelEnum.info.value.name,
               filter=partial(request_log_filter,
                              global_level=global_log_level)
               )
    logger.add(error_path,
               enqueue=True, rotation='10 MB', compression='zip',
               level=LogLevelEnum.error.value.name,
               filter=partial(exact_level_only,
                              level=LogLevelEnum.error.value.no,
                              global_level=global_log_level)
               )

    return logger


async def close_logger(app: Application):
    await app['logger'].complete()
