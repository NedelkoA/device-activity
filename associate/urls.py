from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'devices/$', views.DeviceView.as_view(), name='devices'),
    url(r'devices/(?P<pk>[0-9a-f\-]+)/delete$', views.DeleteDeviceView.as_view(), name='delete_device'),
    url(r'devices/(?P<pk>[0-9a-f\-]+)/activity$', views.ActivitiesView.as_view(), name='activity_device'),
]
