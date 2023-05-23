from django.urls import path

from apiv1.views import base as views

urlpatterns = [
    path('server/groups/', views.ListCreateServerGroup.as_view(), name='server_groups'),  # 创建、列表,
    path('server/group/<int:pk>/', views.RetrieveUpdateDestroyServerGroup.as_view(),
         name='server_group'),  # 详情，更新，删除
]
