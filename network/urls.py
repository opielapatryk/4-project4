
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<int:user_id>", views.profile_view, name="profile_view"),
    # post people that I follow
    path("following", views.following_view, name="following"),

    # API Routes
    path("edit", views.edit_post, name="edit_post"),
    path("like", views.like_post, name="like_post"),
]
