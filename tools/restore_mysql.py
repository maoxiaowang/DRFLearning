"""
一般用于测试服数据重置
"""
import os
import sys
import time
from pathlib import Path

from django.core.management import CommandError

# --- 添加到每个脚本
BASE_DIR = Path(__file__).resolve().parent.parent
TOOLS_DIR = BASE_DIR / 'tools'

for _path in (BASE_DIR, TOOLS_DIR):
    if _path not in sys.path:
        sys.path.append(str(_path.absolute()))
# ---
from common.utils.general import PrintHandler
from tools import ToolsHandler
from common.core.settings import project_settings

MYSQL = project_settings.mysql


class RestoreHandler(ToolsHandler):

    def restore(self, sql_path):
        ph = PrintHandler()
        ph.print('Checking SQL file path ...')
        self._check_path(sql_path)
        ph.print('[OK]', add=True)

        ph.print(f'Rebuilding Database "{self.db_name}" ... ')
        self._rebuild()
        ph.print('[OK]', add=True)

        ph.print(f'Cleaning migration files ... ')
        self._clean()
        ph.print('[OK]', add=True)

        ph.print(f'Importing data from sql file "{sql_path}" ... ')
        self._source_sql(sql_path)
        ph.print('[OK]', add=True)

        ph.print(f'Cleaning table "django_migrations" ... ')
        self._clean_migrations_table()
        ph.print('[OK]', add=True)

        ph.print(f'Making migrations ... ')
        self._make_and_migrate(fake=True)
        ph.print('[OK]', add=True)

        print('Database is successfully restored. Please restart your project.')

        self.conn.close()

    @staticmethod
    def _check_path(sql_path):
        if not Path(sql_path).exists():
            raise CommandError(f'"{sql_path}" not exists.')
        if not Path(sql_path).is_file():
            raise CommandError(f'"{sql_path}" is not a file.')
        if not Path(sql_path).name.endswith('.sql'):
            raise CommandError(f'"{Path(sql_path).suffix}" is not a valid suffix, ".sql" is expected.')

    def _source_sql(self, sql_path):
        # 导入数据
        time.sleep(0.5)
        command = (f'mysql -u{self._mysql_conf.user} -p{self._mysql_conf.password} '
                   f'-h{self._mysql_conf.host} -D{self.db_name} < {sql_path} 2>/dev/null')
        os.system(command)


if __name__ == '__main__':
    try:
        _path = sys.argv[1]
    except IndexError:
        print('SQL file path must be given')
        exit(1)
        raise

    print('** DATA LOST WARNING **')
    print('** 数据丢失警告 **')
    _y = True
    if '--i-truly-understand' not in sys.argv:
        try:
            print(f'You are trying to DESTROY database "{MYSQL.name}" on "{MYSQL.host}"!')
            print(f'你正试图摧毁数据库"{MYSQL.name}"（{MYSQL.host}）!')
            print('Stop this progress unless you really know what you are doing!')
            print('中止这个进程，除非你知道自己在做什么！')
            user_input = input('Are you sure? 确定吗？(y/n): ')
        except KeyboardInterrupt:
            _y = False
        else:
            if user_input not in ('y', 'yes'):
                _y = False
    if _y:
        try:
            RestoreHandler(MYSQL.host, MYSQL.port, MYSQL.user, MYSQL.password, MYSQL.name).restore(_path)
        except CommandError as e:
            print(f'[Error] \n{e}')
    else:
        print('\nCanceled')
