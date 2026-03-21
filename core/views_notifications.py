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
    try:
        notifications = get_user_notifications(request.user, limit=20)
        
        notification_data = []
        for notification in notifications:
            try:
                notification_data.append({
                    'id': notification.id,
                    'title': notification.title,
                    'message': notification.message,
                    'priority': notification.priority,
                    'is_read': notification.is_read,
                    'created_at': notification.created_at.isoformat(),
                    'sender_name': notification.sender.get_full_name() if notification.sender else None,
                    'icon_class': notification.get_icon_class() if hasattr(notification, 'get_icon_class') else 'fas fa-info-circle text-blue-600',
                })
            except Exception as e:
                print(f"Error processing notification {notification.id}: {e}")
                continue
        
        return JsonResponse({
            'success': True,
            'notifications': notification_data,
            'unread_count': get_unread_notification_count(request.user)
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'notifications': [],
            'unread_count': 0
        }, status=500)


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
    try:
        # Get notifications from the last 30 seconds
        thirty_seconds_ago = timezone.now() - timezone.timedelta(seconds=30)
        notifications = get_user_notifications(request.user, limit=5)
        recent_notifications = notifications.filter(created_at__gte=thirty_seconds_ago)
        
        notification_data = []
        for notification in recent_notifications:
            try:
                notification_data.append({
                    'id': notification.id,
                    'title': notification.title,
                    'message': notification.message,
                    'priority': notification.priority,
                    'is_read': notification.is_read,
                    'created_at': notification.created_at.isoformat(),
                    'sender_name': notification.sender.get_full_name() if notification.sender else None,
                    'icon_class': notification.get_icon_class() if hasattr(notification, 'get_icon_class') else 'fas fa-info-circle text-blue-600',
                })
            except Exception as e:
                # Skip problematic notification but continue processing others
                print(f"Error processing notification {notification.id}: {e}")
                continue
        
        return JsonResponse({
            'success': True,
            'notifications': notification_data,
            'unread_count': get_unread_notification_count(request.user)
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'notifications': [],
            'unread_count': 0
        }, status=500)


@login_required
def notification_count(request):
    """API view to get unread notification count"""
    try:
        count = get_unread_notification_count(request.user)
        return JsonResponse({
            'success': True,
            'count': count
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'count': 0
        }, status=500)
