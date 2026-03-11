from django.urls import path
from . import views_notifications

app_name = 'notifications'

urlpatterns = [
    path('', views_notifications.notification_list, name='notification_list'),
    path('latest/', views_notifications.latest_notifications, name='latest_notifications'),
    path('count/', views_notifications.notification_count, name='notification_count'),
    path('<int:notification_id>/mark-read/', views_notifications.mark_notification_read, name='mark_notification_read'),
    path('mark-all-read/', views_notifications.mark_all_notifications_read, name='mark_all_notifications_read'),
]
