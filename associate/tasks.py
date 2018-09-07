from device_activity.celery import app
from .api.serializers import ActivitySerializer


@app.task
def create(data):
    serializer = ActivitySerializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
