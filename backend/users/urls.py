from django.urls import path, include
from .views import Me, UserList, UserDetail, CustomUserCreateView

urlpatterns = [
    path("me", Me.as_view(), name="me"),
    path(route="users", view=UserList.as_view(), name="user_list"),
    path(route="users/<int:user_id>", view=UserDetail.as_view(), name="user_detail"),
    path("users/create", CustomUserCreateView.as_view(), name="custom_user_create"),
    path("auth/", include("dj_rest_auth.urls")),
]