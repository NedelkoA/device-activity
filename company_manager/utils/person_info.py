from django.db.models import Avg, ExpressionWrapper, F, fields

from associate.models import Activity


def average_duration_activity(user):
    expr_duration = ExpressionWrapper(F('end') - F('start'), output_field=fields.DurationField())
    each_durations = Activity.objects.filter(user=user).annotate(duration=expr_duration)
    return each_durations.aggregate(Avg('duration'))['duration__avg']


def last_synchronization(devices):
    for device in devices:
        activities = Activity.objects.filter(device_id=device.id).order_by('-end')
        if activities:
            device.last_synchronization = activities[0]
            device.save()


