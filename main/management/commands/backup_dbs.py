import os
from pathlib import Path

from django.core.management import BaseCommand
from common.core.settings import project_settings
from common.utils.datetime import datetime_to_str, FILENAME_FORMAT
from common.logging import loggers

db_settings = project_settings.mysql


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            'databases', type=str, nargs='*'
        )
        parser.add_argument(
            '--path', type=str, default=f'/home/db_backups/{project_settings.default.project_name}'
        )
        parser.add_argument(
            '--set-gtid-purged-off', action='store_true', default=False
        )

    def handle(self, *args, **options):
        path = Path(options['path'])
        path.mkdir(parents=True, exist_ok=True)
        databases = options['databases'] or [db_settings.name]
        set_gtid_purged_off = options['set_gtid_purged_off']
        for db_name in databases:
            filename = f'{db_name}_{datetime_to_str(fmt=FILENAME_FORMAT)}.sql'
            sql_path = path.joinpath(filename)
            set_gtid_purged_off = '--set-gtid-purged=off' if set_gtid_purged_off else ''
            cmd = (f'mysqldump --single-transaction {set_gtid_purged_off} -h{db_settings.host} '
                   f'-u{db_settings.user} -p{db_settings.password} {db_name} > {sql_path}')
            loggers.command.info(cmd)
            try:
                os.system(cmd)
            except Exception as e:
                loggers.command.error(str(e))
                continue
