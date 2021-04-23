
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<str:username>/page=<int:pnumber>", views.profile, name="profile"),
    path("followingposts/page=<int:pnumber>", views.followingposts, name="followingposts"),

   # API urls
    path("postapi", views.posts, name="postapi"),
    path("allpostsapi", views.allposts, name="allposts"),
    path("profilepostsapi/<str:profilename>", views.profileposts, name="profileposts"),
    path("followtoggle/<str:username>", views.followtoggle, name="followtoggle"),
    path("followingpostsapi", views.followingpostsapi, name="followingpostsapi"),
    path("editpost/<int:postid>", views.editpost, name="edit"),
    path("liketoggle/<int:postid>", views.likes, name="likes")
]
