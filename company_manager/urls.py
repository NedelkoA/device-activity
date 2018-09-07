from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'invite/$', views.InviteView.as_view(), name='invite'),
    url(r'create/$', views.RegisterCompanyView.as_view(), name='create_company'),
    url(r'(?P<pk>[0-9]+)/info/$', views.InfoCompanyView.as_view(), name='company_info'),
    url(r'person/(?P<pk>[0-9]+)/activity/$', views.PersonActivityView.as_view(), name='person_activity'),
]
