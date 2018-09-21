from datetime import timedelta
from uuid import uuid4

from django.conf import settings
from django.utils import timezone

from company_manager.models import Invite


class UserToken:
    def __init__(self, token):
        self._token = token

    def is_alive(self):
        current_date = timezone.now()
        current_lifetime = self._token.created_at + timedelta(days=settings.INVITE_LIFETIME)
        return current_date < current_lifetime

    def is_used(self):
        return bool(self._token.invited)

    @property
    def token(self):
        return self._token

    @classmethod
    def check_instance(cls, request):
        token = Invite.objects.filter(invite_token=request.GET.get('token', None))
        if token:
            return cls(token[0])
        return None

    @classmethod
    def create_token(cls):
        invite_token = uuid4()
        return str(invite_token).replace('-', '')
