from datetime import timedelta
import logging

from django.shortcuts import redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.utils import timezone

from .forms import RegistrationForm, TokenRegistrationForm
from .models import User
from company_manager.models import Invite

logger = logging.getLogger('raven')


class RegistrationView(CreateView):
    template_name = 'accounts/registration.html'
    success_url = reverse_lazy('profile')

    def get(self, request, *args, **kwargs):
        logger.error('There was some crazy error', exc_info=True, extra={
            # Optionally pass a request and we'll grab any information we can
            'request': request,
        })
        # Проверка времени жизни токена
        if self.request.GET.get('token') is not None:
            invite = get_object_or_404(Invite, invite_token=self.request.GET['token'])
            current_date = timezone.now()
            current_lifetime = invite.created_at + timedelta(days=settings.INVITE_LIFETIME)
            if current_date > current_lifetime:
                return redirect(reverse('registration'))
        return super().get(request, args, kwargs)

    def get_form_class(self):
        if self.request.GET.get('token') is not None:
            return TokenRegistrationForm
        return RegistrationForm

    def form_valid(self, form):
        if 'token' in self.request.GET:
            # Обработка регистрации юзера с токеном
            invite = get_object_or_404(Invite, invite_token=self.request.GET['token'])
            if not invite.invited:
                form.instance.email = invite.email
                form.instance.company = invite.invite_creator.company
                obj = form.save()
                invite.invited = obj
                invite.save()
            else:
                return redirect(reverse('registration'))
        else:
            form.instance.is_staff = True
        user = authenticate(
            username=form.cleaned_data.get('username'),
            password=form.cleaned_data.get('password1')
        )
        login(self.request, user)
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    fields = (
        'first_name',
        'last_name',
        'email',
    )
    template_name = 'accounts/profile.html'
    login_url = 'login'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return get_object_or_404(User, pk=self.request.user.id)
