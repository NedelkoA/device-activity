from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from .serializers import DeviceSerializer, ActivitySerializer
from ..models import Device, Activity
from ..tasks import create


class AddDeviceView(viewsets.GenericViewSet,
                    viewsets.mixins.CreateModelMixin):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


class GetActivitiesView(viewsets.GenericViewSet,
                        viewsets.mixins.CreateModelMixin):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        request.data['user'] = self.request.user.id
        create.delay(request.data)
        if 'device' in request.data:
            now = timezone.now()
            device = Device.objects.get(id=request.data['device'])
            device.last_synchronization = now
            device.save()
            user = self.request.user.profile
            user.last_synchronization = now
            user.save()
        return Response('Successfully', status=status.HTTP_201_CREATED)