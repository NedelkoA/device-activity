from rest_framework import serializers
from ..models import Device, Activity


class DeviceSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
        write_only=True
    )

    class Meta:
        model = Device
        fields = (
            'id',
            'user',
            'name',
            'is_active',
        )


class ActivitySerializer(serializers.ModelSerializer):
    device = serializers.PrimaryKeyRelatedField(
        queryset=Device.objects.all(),
        write_only=True
    )

    class Meta:
        model = Activity
        fields = (
            'id',
            'start',
            'end',
            'created_at',
            'name',
            'device',
        )
