from django.shortcuts import reverse, get_object_or_404, redirect
from django.views.generic import ListView, UpdateView
from django.views.generic.edit import FormMixin
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Device, Activity
from .forms import DeleteForm


class DeviceView(LoginRequiredMixin, ListView, FormMixin):
    model = Device
    template_name = 'associate/devices.html'
    form_class = DeleteForm
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        if request.user.is_staff:
            return redirect(reverse('profile'))
        return super().get(request, args, kwargs)

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

    def get(self, request, *args, **kwargs):
        device = get_object_or_404(Device, pk=kwargs['pk'])
        if request.user == device.user and not request.user.is_staff:
            return super().get(request, args, kwargs)
        elif request.user.is_staff:
            return redirect(reverse(
                'company_info',
                kwargs={'pk': request.user.profile.company.id}
            ))
        return redirect(reverse('devices'))

    def form_valid(self, form):
        device = Device.objects.get(id=self.kwargs['pk'])
        device.is_active = False
        device.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('devices')


class ActivitiesView(LoginRequiredMixin, ListView):
    model = Activity
    template_name = 'associate/activities.html'
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        device = get_object_or_404(Device, pk=kwargs['pk'])
        if request.user == device.user and not request.user.is_staff:
            return super().get(request, args, kwargs)
        elif request.user.is_staff:
            return redirect(reverse(
                'company_info',
                kwargs={'pk': request.user.profile.company.id}
            ))
        return redirect(reverse('devices'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activities'] = Activity.objects.filter(
            device=Device.objects.get(pk=self.kwargs['pk']))
        return context
