"""
一般用于测试服数据重置
"""
import sys
from pathlib import Path

from django.core.management import CommandError

# --- 添加到每个脚本
BASE_DIR = Path(__file__).resolve().parent.parent
TOOLS_DIR = BASE_DIR / 'tools'

for _path in (BASE_DIR, TOOLS_DIR):
    if _path not in sys.path:
        sys.path.append(str(_path.absolute()))
# ---

from tools import ToolsHandler
from common.utils.general import PrintHandler
from common.core.settings import project_settings

MYSQL = project_settings.mysql


class InitHandler(ToolsHandler):

    def init(self):
        ph = PrintHandler()

        ph.print(f'Rebuilding Database "{self.db_name}" ... ')
        self._rebuild()
        ph.print('[OK]', add=True)

        ph.print(f'Cleaning migration files ... ')
        self._clean()
        ph.print('[OK]', add=True)

        ph.print(f'Making migrations ... ')
        self._make_and_migrate()
        ph.print('[OK]', add=True)

        print('Database is successfully init. Please restart your project.')

        self.conn.close()


if __name__ == '__main__':

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
            InitHandler(MYSQL.host, MYSQL.port, MYSQL.user, MYSQL.password, MYSQL.name).init()
        except CommandError as e:
            print(f'[Error] \n{e}')
    else:
        print('\nCanceled')
