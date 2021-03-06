"""device_activity URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from django.views.generic import RedirectView
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    url('^$', RedirectView.as_view(url='/account/login')),
    url(r'^account/', include('accounts.urls')),
    url(r'^company/', include('company_manager.urls')),
    url(r'^associate/', include('associate.urls')),
    url(r'^api/', include('associate.api.urls')),
]

# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns = [
#         url('__debug__/', include(debug_toolbar.urls)),
#     ] + urlpatterns
