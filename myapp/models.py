# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

from ckeditor_uploader.fields import RichTextUploadingField


class Room(models.Model):
    """Room model."""

    class Meta:
        """Meta Room."""

        verbose_name = "Room"
        verbose_name_plural = "Rooms"

    name = models.CharField(max_length=50)
    description = models.TextField()
    user = models.ForeignKey(User, related_name="rooms")
    created_at = models.DateTimeField(auto_now=True)
    image = models.FileField(upload_to='room_thumbnails')
    current_screen = models.IntegerField(default=0)
    is_active = models.BooleanField(default=False)
    number_of_current_user = models.IntegerField(default=0)


class Screen(models.Model):
    """Screen model."""

    class Meta:
        """Meta Screen."""

        verbose_name = "Screen"
        verbose_name_plural = "Screens"

    content = RichTextUploadingField(max_length=50000)
    room = models.ForeignKey(Room, related_name='screens')


class RoomActiveUser(models.Model):
    """RoomActiveUserModel."""

    class Meta:
        """RoomActiveUser Meta."""

        unique_together = (("room", "user"),)

    user = models.ForeignKey(User, related_name='active_rooms')
    room = models.ForeignKey(Room, related_name='active_rooms')
