from rest_framework import viewsets, permissions

from .serializers import DeviceSerializer, ActivitySerializer
from ..models import Device, Activity
from ..tasks import create


class AddDeviceView(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ['post']

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


class GetActivitiesView(viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        create.delay(request.data)
        if 'device' in request.data:
            device = Device.objects.get(id=request.data['device'])
            device.update_last_synchronization()
            device.save()
            user = self.request.user.profile
            user.update_last_synchronization()
            user.save()
        return super().create(request, args, kwargs)
