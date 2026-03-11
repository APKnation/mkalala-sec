from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .notification_utils import get_user_notifications, mark_notifications_as_read, get_unread_notification_count
import json


@login_required
def notification_list(request):
    """API view to get user notifications"""
    notifications = get_user_notifications(request.user, limit=20)
    
    notification_data = []
    for notification in notifications:
        notification_data.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'priority': notification.priority,
            'is_read': notification.is_read,
            'created_at': notification.created_at.isoformat(),
            'sender_name': notification.sender.get_full_name() if notification.sender else None,
            'icon_class': notification.get_icon_class(),
        })
    
    return JsonResponse({
        'success': True,
        'notifications': notification_data,
        'unread_count': get_unread_notification_count(request.user)
    })


@login_required
@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    """API view to mark a single notification as read"""
    try:
        mark_notifications_as_read(request.user, [notification_id])
        return JsonResponse({
            'success': True,
            'message': 'Notification marked as read'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@login_required
@require_http_methods(["POST"])
def mark_all_notifications_read(request):
    """API view to mark all notifications as read"""
    try:
        mark_notifications_as_read(request.user)
        return JsonResponse({
            'success': True,
            'message': 'All notifications marked as read'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@login_required
def latest_notifications(request):
    """API view to get latest notifications for auto-refresh"""
    # Get notifications from the last 30 seconds
    thirty_seconds_ago = timezone.now() - timezone.timedelta(seconds=30)
    notifications = get_user_notifications(request.user, limit=5)
    recent_notifications = notifications.filter(created_at__gte=thirty_seconds_ago)
    
    notification_data = []
    for notification in recent_notifications:
        notification_data.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'priority': notification.priority,
            'is_read': notification.is_read,
            'created_at': notification.created_at.isoformat(),
            'sender_name': notification.sender.get_full_name() if notification.sender else None,
            'icon_class': notification.get_icon_class(),
        })
    
    return JsonResponse({
        'success': True,
        'notifications': notification_data,
        'unread_count': get_unread_notification_count(request.user)
    })


@login_required
def notification_count(request):
    """API view to get unread notification count"""
    count = get_unread_notification_count(request.user)
    return JsonResponse({
        'success': True,
        'count': count
    })
