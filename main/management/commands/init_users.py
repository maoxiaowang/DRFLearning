from pathlib import Path

import yaml
from django.core.management.base import BaseCommand

from DRFLearning.settings import BASE_DIR
from main.models import User, Group

MAIN_ETC_DIR = Path(BASE_DIR) / 'main/etc'
GROUP_PERMS_DIR = MAIN_ETC_DIR / 'group_perms'
USER_PERMS_DIR = MAIN_ETC_DIR / 'user_perms'


class Command(BaseCommand):

    def handle(self, *args, **options):
        # init default users
        self.stdout.write(self.style.MIGRATE_HEADING('Initialization default users:'))

        with open(MAIN_ETC_DIR / 'default_users.yaml') as f:
            default_users = yaml.load(f, yaml.CLoader)

        for user in default_users:
            user.update(is_active=True)
            temp_password = str(user.pop('password'))
            if not temp_password:
                raise ValueError('Password not set')
            user_obj, created = User.objects.get_or_create(defaults=user, id=user['id'])
            if created:
                user['password'] = temp_password
                user_obj.set_password(temp_password)
                user_obj.save()
                self.stdout.write(
                    '  Creating user "%(username)s" with default password "%(password)s"... ' % user +
                    self.style.SUCCESS('OK')
                )
        self.stdout.write('  Default users initialization done.')

        with open(MAIN_ETC_DIR / 'default_groups.yaml') as f:
            default_groups = yaml.load(f, yaml.CLoader)

        # init default groups
        for group in default_groups:
            group_obj, created = Group.objects.update_or_create(defaults=group, id=group['id'])
            if created:
                self.stdout.write(
                    '  Creating group "%(name)s"... ' % group + self.style.SUCCESS('OK')
                )
        self.stdout.write('  Default groups initialization done.')

        with open(MAIN_ETC_DIR / 'group_users.yaml') as f:
            group_users = yaml.load(f, yaml.CLoader)

        # 指定用户加入组
        for group, users in group_users.items():
            group_obj = Group.objects.get(name=group)
            for username in users:
                try:
                    user_obj = User.objects.get(username=username)
                except User.DoesNotExist:
                    continue
                if user_obj not in group_obj.user_set.all():
                    self.stdout.write(self.style.SUCCESS(f'  Assign user {username} to group {group}.'))
                    group_obj.user_set.add(user_obj)
