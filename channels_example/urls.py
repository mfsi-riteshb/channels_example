"""channels_example URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin

from myapp.views import (
    custom_login,
    HomeView,
    RoomDetailView,
    RoomView,
    ScreenView,
)

urlpatterns = [
    url(
        r'^admin/',
        admin.site.urls
    ),
    url(
        r'login/$',
        custom_login,
        name='custom_login'
    ),
    url(
        r'^$',
        HomeView.as_view(),
        name='home'
    ),
    url(
        r'^',
        include('registration.backends.default.urls')
    ),
    url(
        r'^rooms/$',
        RoomView.as_view(),
        name="rooms_list"
    ),
    url(
        r'^room/(?P<pk>[0-9])/screens/$',
        ScreenView.as_view(),
        name="screen_list"
    ),
    url(
        r'^room/(?P<pk>[0-9])/$',
        RoomDetailView.as_view(),
        name="rooms_detail"
    ),
    url(
        r'^ckeditor/',
        include('ckeditor_uploader.urls')
    )
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
