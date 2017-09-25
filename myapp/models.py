from django.db import models
from django.contrib.auth.models import User
# Create your models here.
from ckeditor_uploader.fields import RichTextUploadingField

class Room(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    user = models.ForeignKey(User, related_name="rooms")
    created_at = models.DateTimeField(auto_now=True)
    image = models.FileField()
    current_screen = models.IntegerField(default=0)
    is_active = models.BooleanField(default=False)
    number_of_current_user = models.IntegerField(default=0)


class Screen(models.Model):
    content = RichTextUploadingField(max_length=50000)
    room = models.ForeignKey(Room, related_name='screens')
