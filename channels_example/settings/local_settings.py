from .staging import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'channel_example',
        'USER': 'root',
        'PASSWORD': 'mindfire',
        'HOST': 'localhost',
        'PORT': '3306'
    }
}

ALLOWED_HOSTS = ['localhost']
