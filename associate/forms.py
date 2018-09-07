from django import forms

from .models import Device


class DeleteForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = (
            'is_active',
        )
