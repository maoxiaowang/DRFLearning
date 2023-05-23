from django.db import models
from django.utils.translation import gettext_lazy as _

__all__ = [
    'Server',
    'ServerGroup'
]


class Server(models.Model):
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=200, blank=True)
    ip_address = models.CharField(max_length=64)
    is_alive = models.BooleanField(default=False)
    group = models.ForeignKey('ServerGroup', models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    creator = models.OneToOneField('User', models.SET_NULL, null=True)

    class Meta:
        db_table = 'main_server'
        ordering = ('-id',)


class ServerGroup(models.Model):
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'main_server_group'
        ordering = ('-id',)
        default_permissions = ()
        permissions = (
            ('view_server_group', _('Can view server group')),
            ('add_server_group', _('Can add server group')),
            ('change_server_group', _('Can change server group')),
            ('delete_server_group', _('Can delete server group')),
        )
