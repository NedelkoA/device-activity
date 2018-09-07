import uuid

from django.db import models
from django.contrib.auth.models import User


class Device(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='device'
    )
    name = models.CharField(
        max_length=255
    )
    is_active = models.BooleanField(
        default=True,
    )


class Activity(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    start = models.DateTimeField()
    end = models.DateTimeField()
    name = models.CharField(
        max_length=255
    )
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name='activity'
    )
