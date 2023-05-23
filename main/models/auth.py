from django.contrib.auth import models as auth_models
from django.db import models
from django.utils.translation import gettext_lazy as _

from common.utils.model import auto_id_upload_to
from common.utils.static import DEFAULT_FILES

__all__ = [
    'User',
    'Group',
    'Permission'
]


def avatar_upload_to(instance, filename):
    return auto_id_upload_to('user/avatar', instance, filename, replace=False)


class User(auth_models.AbstractUser):
    username = models.CharField(
        max_length=32,
        unique=True
    )
    nickname = models.CharField(max_length=32, blank=True)
    avatar = models.ImageField(
        default=DEFAULT_FILES.default_image,
        upload_to=avatar_upload_to,
    )

    class Meta:
        db_table = 'main_user'
        ordering = ('id',)
        default_permissions = ()
        permissions = (
            ('view_user', 'Can view user'),
            ('add_user', 'Can add user'),
            ('change_user', 'Can change user'),
            ('delete_user', 'Can delete user'),
        )

    def __str__(self):
        return f'{self.get_username()} ({self.id})'


if not hasattr(auth_models.Group, 'description'):
    description = models.CharField(_('Description'), max_length=255, blank=True)
    description.contribute_to_class(auth_models.Group, 'description')


class Group(auth_models.Group):
    class Meta:
        proxy = True
        ordering = ('id',)


class Permission(auth_models.Permission):
    class Meta:
        proxy = True
        default_permissions = ()
        permissions = (
            ('view_permission', 'Can view permission'),
        )

    def natural_key(self):
        return {'id': self.pk, 'name': _(self.name),
                'content_type_name': _(self.content_type.name),
                'content_type_id': self.content_type.id,
                'codename': self.codename}
