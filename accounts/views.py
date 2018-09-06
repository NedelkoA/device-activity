from django.shortcuts import redirect, reverse
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404

from .forms import RegistrationForm, TokenRegistrationForm
from .models import User
from company_manager.models import Invite


class RegistrationView(CreateView):
    template_name = 'accounts/registration.html'
    success_url = reverse_lazy('profile')

    def get_form_class(self):
        if 'token' in self.request.GET and self.request.GET['token']:
            return TokenRegistrationForm
        return RegistrationForm

    def get(self, request, *args, **kwargs):
        return super().get(request, args, kwargs)

    def form_valid(self, form):
        if 'token' in self.request.GET:
            # Обработка регистрации юзера с токеном
            invite = get_object_or_404(Invite, invite_token=self.request.GET['token'])
            if not invite.invited:
                form.instance.email = invite.email
                obj = form.save()
                invite.invited = obj
                invite.save()
            else:
                return redirect(reverse('registration'))
        else:
            form.instance.is_staff = True
        valid = super().form_valid(form)
        user = authenticate(
            username=form.cleaned_data.get('username'),
            password=form.cleaned_data.get('password1')
        )
        login(self.request, user)
        return valid


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
