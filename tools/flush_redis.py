"""
仅用于测试环境
"""
import os
import sys

from redis import Redis

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from common.core.settings import project_settings


def clean():
    redis = Redis(
        socket_connect_timeout=2,
        host=project_settings.redis.host,
        port=project_settings.redis.port,
        password=project_settings.redis.password
    )
    redis.flushall()
    print('  Redis data all flushed.')


if __name__ == '__main__':
    print('All redis data will be deleted!')
    try:
        user_input = input('Are you sure? (y/n): ')
    except KeyboardInterrupt:
        print('\nCanceled')
    else:
        if user_input in ('y', 'yes'):
            clean()
        else:
            print('Canceled')
