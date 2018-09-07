from django.conf.urls import url
from django.contrib.auth.views import LogoutView, LoginView

from . import views

urlpatterns = [
    url(r'login/$', LoginView.as_view(
        template_name='accounts/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    url(r'logout/$', LogoutView.as_view(next_page='login'), name='logout'),
    url(r'registration/$', views.RegistrationView.as_view(), name='registration'),
    url(r'profile/$', views.ProfileView.as_view(), name='profile'),
]
