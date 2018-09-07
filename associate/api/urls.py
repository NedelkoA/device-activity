from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'device', views.AddDeviceView)
router.register(r'activities', views.GetActivitiesView)

urlpatterns = [
    url(r'', include(router.urls)),
]
