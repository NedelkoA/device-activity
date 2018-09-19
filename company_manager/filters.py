# https://django-filter.readthedocs.io/en/master/

import django_filters

from associate.models import Activity, Device


class ActivityFilter(django_filters.FilterSet):
    def __init__(self, data=None, *args, **kwargs):
        devices = Device.objects.filter(
            user=kwargs.pop('user'),
            is_active=True
        )
        activities = sorted(set(
            kwargs['queryset'].values_list('name', flat=True)
        ))
        activity_choices = [
            ('{}'.format(activity), '{}'.format(activity))
            for activity in activities
        ]
        dates = sorted(set([
            start.date()
            for start in kwargs['queryset'].values_list('start', flat=True)
        ]))
        date_choices = [
            ('{}'.format(dt), '{}'.format(dt))
            for dt in dates
        ]
        self.base_filters['device_id'] = django_filters.ModelChoiceFilter(
            field_name='device_id',
            queryset=devices
        )
        self.base_filters['name'] = django_filters.ChoiceFilter(
            field_name='name',
            choices=activity_choices
        )
        self.base_filters['start'] = django_filters.ChoiceFilter(
            field_name='start',
            choices=date_choices,
            lookup_expr='icontains',
            label='Date'
        )
        super().__init__(data, *args, **kwargs)

    class Meta:
        model = Activity
        fields = (
            'device_id',
        )
