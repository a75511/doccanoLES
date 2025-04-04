from django.urls import path, include
from .views import Me, Users, CustomUserCreateView

urlpatterns = [
    path("me", Me.as_view(), name="me"),
    path("users", Users.as_view(), name="user_list"),
    path("users/create", CustomUserCreateView.as_view(), name="custom_user_create"),
    path("auth/", include("dj_rest_auth.urls")),
]