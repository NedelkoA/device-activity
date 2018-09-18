import logging

from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, reverse
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView


from .forms import RegistrationForm, TokenRegistrationForm
from .models import User
from .utils.tokens import UserToken

logger = logging.getLogger('raven')


class RegistrationView(CreateView):
    template_name = 'accounts/registration.html'
    success_url = reverse_lazy('profile')

    def get(self, request, *args, **kwargs):
        logger.error('There was some crazy error', exc_info=True, extra={
            'request': request,
        })
        if UserToken.check_instance(request):
            user_token = UserToken.check_instance(request)
            if not user_token.is_alive() or user_token.is_used():
                return redirect(reverse('registration'))
        return super().get(request, args, kwargs)

    def get_form_class(self):
        if UserToken.check_instance(self.request):
            return TokenRegistrationForm
        return RegistrationForm

    def form_valid(self, form):
        obj = form.save()
        if UserToken.check_instance(self.request):
            # Обработка регистрации юзера с токеном
            invite = UserToken.check_instance(self.request)
            if invite.is_used():
                return redirect(reverse('registration'))
            form.instance.email = invite.token.email
            # не сохраняет компанию в профайле юзера
            # obj.profile.company = invite.token.invite_creator.profile.company
            # obj.save()
            invite.token.invited = obj
            invite.token.save()
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
