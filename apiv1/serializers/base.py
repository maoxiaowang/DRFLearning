from rest_framework import serializers

from main.models import ServerGroup


class ServerGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = ServerGroup
        fields = ('id', 'name', 'description')
