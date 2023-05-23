from django.urls import path, include

urlpatterns = [
    path('auth/', include('apiv1.urls.auth')),
    path('base/', include('apiv1.urls.base')),
]
