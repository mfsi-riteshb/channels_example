
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms

from .models import Room, Screen
from registration.forms import RegistrationFormUniqueEmail
from django.contrib.auth.forms import AuthenticationForm as BaseAuthenticationForm
from django.utils.translation import ugettext_lazy as _


attrs_dict = {'class': 'required form-control'}


class RoomForm(forms.ModelForm):

    class Meta:
        model = Room
        fields = ('name', 'description', 'image')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }


class RoomScreenForm(forms.ModelForm):
    image = forms.ImageField()

    class Meta:
        model = Screen
        fields = ('image',)


class MyRegistrationFormUniqueEmail(RegistrationFormUniqueEmail):
    username = forms.RegexField(
        regex=r'^[\w.@+-]+$',
        max_length=30,
        widget=forms.TextInput(attrs=attrs_dict),
        label=_("Username"),
        error_messages={
            'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")
        }
    )
    email = forms.EmailField(widget=forms.TextInput(
        attrs=dict(attrs_dict, maxlength=75)),
        label=_("E-mail")
    )
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict),
                                label=_("Password"))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict,),
                                label=_("Password (again)"))


class AuthenticationForm(BaseAuthenticationForm):
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
