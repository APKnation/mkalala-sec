from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import User, StudentProfile, Announcement, Message, Grade, Enrollment, Payment, LeaveRequest
from .notification_utils import (
    notify_student_registered,
    notify_announcement_posted,
    notify_message_received,
    notify_grade_submitted,
    notify_enrollment_completed,
    notify_payment_received,
    notify_leave_request
)


@receiver(post_save, sender=StudentProfile)
def student_registered_signal(sender, instance, created, **kwargs):
    """Signal to trigger notification when student is registered"""
    if created:
        notify_student_registered(instance)


@receiver(post_save, sender=Announcement)
def announcement_posted_signal(sender, instance, created, **kwargs):
    """Signal to trigger notification when announcement is posted"""
    if created and instance.is_active:
        notify_announcement_posted(instance)


@receiver(post_save, sender=Message)
def message_received_signal(sender, instance, created, **kwargs):
    """Signal to trigger notification when message is sent"""
    if created:
        notify_message_received(instance)


@receiver(post_save, sender=Grade)
def grade_submitted_signal(sender, instance, created, **kwargs):
    """Signal to trigger notification when grade is submitted"""
    if created:
        notify_grade_submitted(instance)


@receiver(post_save, sender=Enrollment)
def enrollment_completed_signal(sender, instance, created, **kwargs):
    """Signal to trigger notification when enrollment is completed"""
    if created:
        notify_enrollment_completed(instance)


@receiver(post_save, sender=Payment)
def payment_received_signal(sender, instance, created, **kwargs):
    """Signal to trigger notification when payment is received"""
    if created:
        notify_payment_received(instance)


@receiver(post_save, sender=LeaveRequest)
def leave_request_signal(sender, instance, created, **kwargs):
    """Signal to trigger notification when leave request is submitted"""
    if created:
        notify_leave_request(instance)
