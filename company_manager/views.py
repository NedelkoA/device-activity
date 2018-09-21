from django.urls import reverse_lazy
from django.shortcuts import redirect, reverse
from django.views.generic import CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Count
from django.http import HttpResponseNotFound

from .models import Invite, Company
from .tasks import send_invite_email
from .filters import ActivityFilter
from accounts.models import Profile
from associate.models import Activity, Device
from .utils.person_info import average_duration_activity
from accounts.utils.tokens import UserToken


class StaffRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponseNotFound('Page not found')
        return super().dispatch(request, *args, **kwargs)


class InviteView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Invite
    fields = (
        'email',
    )
    template_name = 'company_manager/invite.html'
    success_url = reverse_lazy('invite')
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        if request.user.is_staff and not request.user.profile.company:
            return redirect(reverse('create_company'))
        return super().get(request, args, kwargs)

    def form_valid(self, form):
        form.instance.invite_creator = self.request.user
        form.instance.invite_token = UserToken.create_token()
        current_site = get_current_site(self.request)
        send_invite_email.delay(
            current_site.domain,
            form.cleaned_data.get('email'),
            form.instance.invite_token
        )
        return super().form_valid(form)


class RegisterCompanyView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Company
    fields = (
        'title',
    )
    template_name = 'company_manager/create_company.html'
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        if request.user.is_staff and request.user.profile.company:
            return redirect(reverse('company_info', kwargs={'pk': request.user.profile.company.id}))
        return super().get(request, args, kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('company_info', kwargs={'pk': self.object.id})


class InfoCompanyView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    model = Company
    template_name = 'company_manager/company_info.html'
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        company = request.user.profile.company
        if company and company.id == obj.id:
            return super().get(request, args, kwargs)
        return HttpResponseNotFound('Page not found')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['associate'] = Profile.objects.filter(company=self.get_object())
        return context


class PersonActivityView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    model = Profile
    template_name = 'company_manager/person_activity.html'
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        company = request.user.profile.company
        if company and company.id == obj.company.id:
            return super().get(request, args, kwargs)
        return HttpResponseNotFound('Page not found')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()
        devices = Device.objects.filter(user=profile.user, is_active=True)
        activities = Activity.objects.filter(user=profile.user).order_by('-start')
        context['filter'] = ActivityFilter(self.request.GET, queryset=activities, user=profile.user)
        context['duration'] = average_duration_activity(profile.user)
        context['devices'] = devices.aggregate(Count('id'))['id__count']
        if self.request.GET.get('device_id', ''):
            context['last_sync'] = Device.objects.get(id=self.request.GET.get('device_id')).last_synchronization
        context['last_sync_user'] = profile.last_synchronization
        return context
