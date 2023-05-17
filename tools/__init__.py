import os
from pathlib import Path

from MySQLdb import connect, cursors
from django.contrib import auth

BASE_DIR = Path(__file__).resolve().parent.parent
MIGRATION_DIR_NAME = 'migrations'

PYTHON_PATH = BASE_DIR / 'venv/bin/python'


class ToolsHandler(object):
    class _MySQLConf(object):
        host: str
        port: int
        user: str
        password: str

        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    def __init__(self, host, port, user, password, db_name):
        self.mysql_dict = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'cursorclass': cursors.DictCursor
        }
        self.db_name = db_name
        self.conn = connect(**self.mysql_dict)

    @property
    def _mysql_conf(self):
        return self._MySQLConf(**self.mysql_dict)

    def _rebuild(self):
        cur = None
        try:
            cur = self.conn.cursor()
            drop_sql = 'DROP DATABASE IF EXISTS %s' % self.db_name
            cur.execute(drop_sql)
        except Exception:
            pass
        else:
            cur = self.conn.cursor()
            sql = ('CREATE DATABASE IF NOT EXISTS %s DEFAULT CHARSET utf8mb4 '
                   'COLLATE utf8mb4_unicode_ci' % self.db_name)
            cur.execute(sql)
            cur.close()
        if cur:
            cur.close()

    @staticmethod
    def _clean():
        if os.path.exists(BASE_DIR):
            for root, dirs, files in os.walk(BASE_DIR):
                if os.path.split(root)[-1] == MIGRATION_DIR_NAME:
                    for f in files:
                        if f != '__init__.py' and len(f) > 6 and f[:4].isdigit():
                            os.remove(os.path.join(root, f))
                    # for d in dirs:
                    #     if d == '__pycache__':
                    #         shutil.rmtree(os.path.join(root, d))

        # # clean guardian
        # guardian_migrations_dir = os.path.join(os.path.dirname(guardian.__file__), MIGRATION_DIR_NAME)
        # for f in os.listdir(guardian_migrations_dir):
        #     abs_path = os.path.join(guardian_migrations_dir, f)
        #     if os.path.isfile(abs_path) and f != '__init__.py':
        #         os.remove(abs_path)
        #         print("  Migration file '%s' removed." % abs_path)

        # clean contrib apps
        auth_migrations_dir = os.path.join(os.path.dirname(auth.__file__), MIGRATION_DIR_NAME)
        for f in os.listdir(auth_migrations_dir):
            abs_path = os.path.join(auth_migrations_dir, f)
            if os.path.isfile(abs_path) and f != '__init__.py':
                os.remove(abs_path)

    def _clean_migrations_table(self):
        # 清理django_migrations表
        cur = self.conn.cursor()
        cur.execute(f'TRUNCATE TABLE {self.db_name}.django_migrations')
        cur.close()

    @staticmethod
    def _make_and_migrate(fake=False):
        fake_arg = '--fake' if fake else ''
        os.system(f'{str(PYTHON_PATH.absolute())} manage.py makemigrations 1> /dev/null')
        os.system(f'{str(PYTHON_PATH.absolute())} manage.py migrate {fake_arg} 1> /dev/null')
