from django.urls import path

from apiv1.views import auth as views

urlpatterns = [
    path('token/', views.GetToken.as_view(), name='auth_token'),
]
