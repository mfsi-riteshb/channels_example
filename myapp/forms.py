
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms

from .models import Room, Screen
from registration.forms import RegistrationFormUniqueEmail


class RoomForm(forms.ModelForm):

    class Meta:
        model = Room
        fields = ('name', 'description', 'image')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'validate'}),
            'description': forms.Textarea(attrs={'class': 'validate'}),
        }


class RoomScreenForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = Screen
        fields = ('content',)


class MyRegistrationFormUniqueEmail(RegistrationFormUniqueEmail):
    class Meta(RegistrationFormUniqueEmail.Meta):
        widgets = {
            'username': forms.TextInput(attrs={'class': 'validate'}),
            'email': forms.TextInput(attrs={'class': 'validate'}),
            'password1': forms.PasswordInput(attrs={'class': 'validate'}),
            'password2': forms.PasswordInput(attrs={'class': 'validate'})
        }
