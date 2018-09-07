from django.db import models
from django.contrib.auth.models import User


class Company(models.Model):
    title = models.CharField(
        max_length=255,
        unique=True
    )


class Invite(models.Model):
    invite_token = models.UUIDField(
        unique=True
    )
    invite_creator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    invited = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name='invitation'
    )
    email = models.EmailField(
        unique=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = (
            'invite_token',
            'email',
        )
