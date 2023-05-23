from apiv1.serializers import base as base_serializers
from common.views import generics
from main.models import ServerGroup
from apiv1.filters import base as base_filters


class ListCreateServerGroup(generics.ListCreateAPIView):
    serializer_class = base_serializers.ServerGroupSerializer
    queryset = ServerGroup.objects.all()
    filterset_class = base_filters.ServerGroupFilter


class RetrieveUpdateDestroyServerGroup(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = base_serializers.ServerGroupSerializer
    queryset = ServerGroup.objects.all()
