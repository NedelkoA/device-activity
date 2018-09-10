# https://django-filter.readthedocs.io/en/master/

import django_filters

from associate.models import Activity, Device

devices = sorted(set(Device.objects.values_list('name', flat=True)))
DEVICE_CHOICES = [
    ('{}'.format(device), '{}'.format(device))
    for device in devices
]

activities = sorted(set(Activity.objects.values_list('name', flat=True)))
ACTIVITY_CHOICES = [
    ('{}'.format(activity), '{}'.format(activity))
    for activity in activities
]

starts = Activity.objects.values_list('start', flat=True)
dates = sorted(set([
    start.date()
    for start in starts
]))
START_CHOICES = [
    ('{}'.format(dt), '{}'.format(dt))
    for dt in dates
]


class ActivityFilter(django_filters.FilterSet):
    device__name = django_filters.ChoiceFilter(
        choices=DEVICE_CHOICES,
    )
    name = django_filters.ChoiceFilter(
        choices=ACTIVITY_CHOICES,
    )
    start = django_filters.ChoiceFilter(
        choices=START_CHOICES,
        lookup_expr='icontains'
    )

    class Meta:
        model = Activity
        fields = ()




