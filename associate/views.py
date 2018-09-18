from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotFound
from django.shortcuts import reverse
from django.views.generic import ListView, UpdateView
from django.views.generic.edit import FormMixin

from .forms import DeleteForm
from .models import Activity, Device


class UserRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_staff:
            return HttpResponseNotFound('Page not found')
        return super().dispatch(request, *args, **kwargs)


class DeviceView(LoginRequiredMixin, UserRequiredMixin, ListView, FormMixin):
    model = Device
    template_name = 'associate/devices.html'
    form_class = DeleteForm
    login_url = 'login'

    def get_queryset(self):
        return Device.objects.filter(
            user=self.request.user,
            is_active=True,
        )


class DeleteDeviceView(LoginRequiredMixin, UpdateView):
    model = Device
    form_class = DeleteForm
    template_name = 'associate/devices.html'
    login_url = 'login'
    http_method_names = ['post']

    def form_valid(self, form):
        device = Device.objects.get(id=self.kwargs['pk'])
        device.is_active = False
        device.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('devices')


class ActivitiesView(LoginRequiredMixin, UserRequiredMixin, ListView):
    model = Activity
    template_name = 'associate/activities.html'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activities'] = Activity.objects.filter(
            device=Device.objects.get(pk=self.kwargs['pk']))
        return context
