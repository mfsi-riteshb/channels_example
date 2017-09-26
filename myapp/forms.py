
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from django.contrib.auth.models import User

from .models import Room, Screen
from registration.forms import RegistrationForm


class RoomForm(forms.ModelForm):

    class Meta:
        model = Room
        fields = ('name', 'description', 'image')


class RoomScreenForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget())
    class Meta:
        model = Screen
        fields = ('content',)