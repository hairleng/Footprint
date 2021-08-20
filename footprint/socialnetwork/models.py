from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Log(models.Model):
    log_title = models.CharField(blank=True, max_length=200)
    log_text = models.CharField(blank=True, max_length=20000000)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="log_creator")
    location = models.ForeignKey('Location', on_delete=models.PROTECT, related_name="log_location")
    creation_time = models.DateTimeField(auto_now_add=True)
    picture = models.FileField(blank=True, default="default_location_2.png")
    content_type = models.CharField(max_length=50, default="jpeg")
    visibility = models.BooleanField(default=True)
    liked_users = models.ManyToManyField('Profile', default=None, related_name='liked_users', symmetrical=False)

    def __str__(self):
        return 'id=' + str(self.id) + 'title=' + self.log_title + 'text=' + self.log_text + 'created_time=' + str(
            self.creation_time) + 'location_id=' + str(self.location_id) + 'visibility=' + str(self.visibility)


class Comment(models.Model):
    comment_content  = models.CharField(blank=True, max_length=200)
    created_by    = models.ForeignKey(User, on_delete=models.PROTECT, related_name="comment_creator")
    of_log       = models.ForeignKey(Log, on_delete=models.PROTECT, related_name="of_log")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return 'Comment(id=' + str(self.id) + ')'


class Location(models.Model):
    placeID = models.CharField(primary_key=True, max_length=200)
    location_name = models.CharField(blank=True, max_length=200)
    lat = models.FloatField()
    lng = models.FloatField()
    location_description = models.CharField(blank=True, max_length=500)

    # visited_users = models.ManyToManyField('Profile', default=None, related_name='visited_users', symmetrical=False)
    def __str__(self):
        return 'Comment(id=' + str(self.placeID) + ')'


class Profile(models.Model):
    user = models.OneToOneField(User, default=None, on_delete=models.CASCADE, related_name='profile')
    picture = models.FileField(default="profileimgs/default_avatar.png")
    bio = models.CharField(max_length=300, blank=True)
    content_type = models.CharField(max_length=50, default="jpeg")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    following = models.ManyToManyField('Profile', default=None, related_name='profile_following', symmetrical=False)
    follower = models.ManyToManyField('Profile', default=None, related_name='profile_follower', symmetrical=False)

    visited = models.ManyToManyField('Location', default=None, related_name='visited_location', symmetrical=False)
    bookmarked_logs = models.ManyToManyField('Log', default=None, related_name='bookmarked_logs', symmetrical=False)
    def __str__(self):
        return str(self.user.username) + ',' + str(self.bio)