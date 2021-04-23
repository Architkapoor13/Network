from django.contrib.auth.models import AbstractUser
from django.db import models
from django.template import defaultfilters
import pytz


class User(AbstractUser):
    followers = models.ManyToManyField("User", related_name="fllowers", blank=True)
    following = models.ManyToManyField("User", related_name="fllowing", blank=True)
    postsliked = models.ManyToManyField("Posts", related_name="likedposts", blank=True)
    pass

class Posts(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="user")
    postdata = models.TextField(blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField("User", related_name="likes", blank=True)

    def serialize(self):
        return {
            "id": self.id,
            "username": self.user.username,
            "data": self.postdata,
            "likes": self.likes.count(),
            "timeposted": self.timestamp.strftime("%b %d %Y, %I:%M %p")
        }
