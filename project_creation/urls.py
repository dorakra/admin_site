"""project_creation URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path

from erhtv import views

def custom_i18n_patterns(*urls, prefix_default_language=False):
    """
    Add URL pattern without the language code prefix.
    """
    return list(urls)


urlpatterns = custom_i18n_patterns(
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    prefix_default_language=False
)


