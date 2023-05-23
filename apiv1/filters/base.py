from django_filters.rest_framework import filterset, filters

from main.models import ServerGroup


class ServerGroupFilter(filterset.FilterSet):
    ordering = filters.OrderingFilter(
        fields=['id']
    )

    class Meta:
        model = ServerGroup
        fields = {
            'name': ['contains']
        }
