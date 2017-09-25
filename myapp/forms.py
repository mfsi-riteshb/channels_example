
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from .models import Room, Screen


class RoomForm(forms.ModelForm):

    class Meta:
        model = Room
        fields = ('name', 'description', 'image')


class RoomScreenForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget())
    class Meta:
        model = Screen
        fields = ('content',)