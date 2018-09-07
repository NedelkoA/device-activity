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
        create.delay(request.data)
        return Response('Successfully', status=status.HTTP_201_CREATED)
