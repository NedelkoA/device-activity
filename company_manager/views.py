from uuid import uuid4

from django.urls import reverse_lazy
from django.shortcuts import redirect, reverse
from django.views.generic import CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Invite, Company


class InviteView(LoginRequiredMixin, CreateView):
    model = Invite
    fields = (
        'email',
    )
    template_name = 'company_manager/invite.html'
    success_url = reverse_lazy('invite')

    def form_valid(self, form):
        form.instance.invite_creator = self.request.user
        invite_token = uuid4()
        form.instance.invite_token = str(invite_token).replace('-', '')
        # logic to send email with invite token
        return super().form_valid(form)


class RegisterCompanyView(LoginRequiredMixin, CreateView):
    model = Company
    fields = (
        'title',
    )
    template_name = 'company_manager/create_company.html'
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        user = request.user
        if not user.is_superuser and user.profile.invite_token and user.company:
            return redirect(reverse('company_info', kwargs={'pk': user.company.id}))
        return super().get(request, args, kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('company_info', kwargs={'pk': self.object.id})


class InfoCompanyView(LoginRequiredMixin, DetailView):
    model = Company
    template_name = 'company_manager/company_info.html'
    login_url = 'login'

    # logic for render activity info about associate
