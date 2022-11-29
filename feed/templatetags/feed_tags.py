from django import template
from feed.models import Notifications

register = template.Library()


@register.inclusion_tag('feed/notifications.html', takes_context=True)
def display_notifications(context):
    request_user = context['request'].user
    notifications = Notifications.objects.filter(recieving_user=request_user).exclude(has_seen=True).order_by('-recency')
    return {'notifications': notifications}
