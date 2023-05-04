from django.urls import path

from authserver import views
from rest_framework.authtoken import views as token_views
urlpatterns = [
    path("registration/", views.Authorization.as_view({"post": "create"})),
    path("token/", token_views.obtain_auth_token)
]
