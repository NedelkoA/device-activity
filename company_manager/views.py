from uuid import uuid4

from django.urls import reverse_lazy
from django.shortcuts import redirect, reverse
from django.views.generic import CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site

from .models import Invite, Company
from .tasks import send_invite_email
from .filters import ActivityFilter
from accounts.models import Profile
from associate.models import Activity, Device


class InviteView(LoginRequiredMixin, CreateView):
    model = Invite
    fields = (
        'email',
    )
    template_name = 'company_manager/invite.html'
    success_url = reverse_lazy('invite')
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect(reverse('profile'))
        elif request.user.is_staff and not request.user.profile.company:
            return redirect(reverse('create_company'))
        return super().get(request, args, kwargs)

    def form_valid(self, form):
        form.instance.invite_creator = self.request.user
        invite_token = uuid4()
        form.instance.invite_token = str(invite_token).replace('-', '')
        current_site = get_current_site(self.request)
        send_invite_email.delay(
            current_site.domain,
            form.cleaned_data.get('email'),
            form.instance.invite_token
        )
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
        if not user.is_superuser and user.is_staff and user.profile.company:
            return redirect(reverse('company_info', kwargs={'pk': user.profile.company.id}))
        elif not user.is_staff and not user.is_superuser:
            return redirect(reverse('profile'))
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['associate'] = Profile.objects.filter(company=self.get_object())
        return context


class PersonActivityView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'company_manager/person_activity.html'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()
        devices = Device.objects.filter(user=profile.user, is_active=True).values_list('id', flat=True)
        activities = Activity.objects.filter(device_id__in=devices).order_by('-start')
        context['filter'] = ActivityFilter(self.request.GET, queryset=activities)
        return context
