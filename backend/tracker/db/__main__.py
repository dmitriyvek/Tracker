'''
Utility for managing the state of the database, wrapper over alembic.
Can be called from any directory, and also specify an arbitrary DSN for the base
data other than the one specified in the alembic.ini file. 
'''
import argparse
import logging
import os

from alembic.config import CommandLine

from tracker.utils.db import make_alembic_config
from tracker.utils.settings import get_default_pg_url


def main():
    logging.basicConfig(level=logging.DEBUG)

    alembic = CommandLine()
    alembic.parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter
    alembic.parser.add_argument(
        '--pg-url', default=os.getenv('ANALYZER_PG_URL', get_default_pg_url()),
        help='Database URL [env var: ANALYZER_PG_URL]'
    )

    options = alembic.parser.parse_args()
    if 'cmd' not in options:
        alembic.parser.error('too few arguments')
        exit(128)
    else:
        config = make_alembic_config(options)
        exit(alembic.run_cmd(config, options))


if __name__ == '__main__':
    main()
