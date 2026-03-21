from django.utils import timezone
from .models import User, Notification, StudentProfile, FacultyProfile, Announcement, CourseOffering


def create_notification(recipient, notification_type, title, message, 
                    sender=None, priority='medium', 
                    related_student=None, related_teacher=None, 
                    related_announcement=None, related_course=None):
    """
    Create a new notification
    
    Args:
        recipient: User who will receive the notification
        notification_type: Type of notification (from Notification.NOTIFICATION_TYPES)
        title: Notification title
        message: Notification message
        sender: User who sent the notification (optional)
        priority: Priority level (low, medium, high, urgent)
        related_student: Related StudentProfile (optional)
        related_teacher: Related FacultyProfile (optional)
        related_announcement: Related Announcement (optional)
        related_course: Related CourseOffering (optional)
    """
    return Notification.objects.create(
        recipient=recipient,
        sender=sender,
        type=notification_type,  # Use 'type' instead of 'notification_type'
        title=title,
        message=message,
        priority=priority,
        related_student=related_student,
        related_teacher=related_teacher,
        related_announcement=related_announcement,
        related_course=related_course
    )


def notify_student_registered(student_profile, sender=None):
    """Create notification when a new student is registered"""
    # Notify all admins
    admins = User.objects.filter(role='admin')
    for admin in admins:
        create_notification(
            recipient=admin,
            notification_type='student_registered',
            title=f'New Student Registered: {student_profile.user.get_full_name()}',
            message=f'{student_profile.user.get_full_name()} ({student_profile.get_form_display()}) has been registered in the system.',
            sender=sender,
            priority='medium',
            related_student=student_profile
        )


def notify_announcement_posted(announcement, target_users=None):
    """Create notifications when announcement is posted"""
    if target_users is None:
        # Get target users based on announcement audience
        if announcement.target_audience == 'All':
            target_users = User.objects.filter(role__in=['student', 'teacher', 'admin'])
        elif announcement.target_audience == 'Students':
            target_users = User.objects.filter(role='student')
        elif announcement.target_audience == 'Faculty':
            target_users = User.objects.filter(role='teacher')
        elif announcement.target_audience == 'Parents':
            target_users = User.objects.filter(role='parent')
        elif announcement.target_audience == 'Class' and announcement.target_class:
            # Get students in specific class
            target_users = User.objects.filter(
                studentprofile__student_class=announcement.target_class
            )
        else:
            target_users = User.objects.none()
    
    # Create notifications for all target users
    for user in target_users:
        create_notification(
            recipient=user,
            notification_type='announcement',
            title=announcement.title,
            message=f'New announcement: {announcement.title}',
            sender=announcement.created_by,
            priority='medium',
            related_announcement=announcement
        )


def notify_message_received(message):
    """Create notification when user receives a message"""
    create_notification(
        recipient=message.recipient,
        notification_type='message_received',
        title=f'New Message from {message.sender.get_full_name()}',
        message=message.subject,
        sender=message.sender,
        priority='medium'
    )


def notify_grade_submitted(grade):
    """Create notification when grade is submitted for student"""
    # Notify the student
    create_notification(
        recipient=grade.enrollment.student.user,
        notification_type='grade_submitted',
        title=f'Grade Posted: {grade.enrollment.course_offering.course.name}',
        message=f'Your grade for {grade.enrollment.course_offering.course.name} has been posted: {grade.grade}',
        sender=grade.enrollment.course_offering.faculty.user if grade.enrollment.course_offering.faculty else None,
        priority='medium',
        related_student=grade.enrollment.student,
        related_course=grade.enrollment.course_offering
    )


def notify_enrollment_completed(enrollment):
    """Create notification when student completes enrollment"""
    # Notify the student
    create_notification(
        recipient=enrollment.student.user,
        notification_type='enrollment_completed',
        title=f'Enrollment Completed: {enrollment.course_offering.course.name}',
        message=f'You have been successfully enrolled in {enrollment.course_offering.course.name}',
        priority='medium',
        related_student=enrollment.student,
        related_course=enrollment.course_offering
    )
    
    # Notify the teacher
    if enrollment.course_offering.faculty:
        create_notification(
            recipient=enrollment.course_offering.faculty.user,
            notification_type='enrollment_completed',
            title=f'New Enrollment: {enrollment.student.user.get_full_name()}',
            message=f'{enrollment.student.user.get_full_name()} has enrolled in {enrollment.course_offering.course.name}',
            priority='low',
            related_student=enrollment.student,
            related_course=enrollment.course_offering
        )


def notify_payment_received(payment):
    """Create notification when payment is received"""
    # Notify the student
    create_notification(
        recipient=payment.student.user,
        notification_type='payment_received',
        title=f'Payment Received: {payment.amount}',
        message=f'Your payment of {payment.amount} has been received and processed.',
        priority='medium',
        related_student=payment.student
    )
    
    # Notify admins
    admins = User.objects.filter(role='admin')
    for admin in admins:
        create_notification(
            recipient=admin,
            notification_type='payment_received',
            title=f'Payment Received: {payment.student.user.get_full_name()}',
            message=f'{payment.student.user.get_full_name()} has made a payment of {payment.amount}',
            priority='low',
            related_student=payment.student
        )


def notify_leave_request(leave_request):
    """Create notification when leave request is submitted"""
    # Notify the teacher
    if leave_request.course_offering.faculty:
        create_notification(
            recipient=leave_request.course_offering.faculty.user,
            notification_type='leave_request',
            title=f'Leave Request: {leave_request.student.user.get_full_name()}',
            message=f'{leave_request.student.user.get_full_name()} has requested leave from {leave_request.start_date} to {leave_request.end_date}',
            priority='high',
            related_student=leave_request.student,
            related_course=leave_request.course_offering
        )
    
    # Notify admins
    admins = User.objects.filter(role='admin')
    for admin in admins:
        create_notification(
            recipient=admin,
            notification_type='leave_request',
            title=f'Leave Request: {leave_request.student.user.get_full_name()}',
            message=f'{leave_request.student.user.get_full_name()} has requested leave from {leave_request.start_date} to {leave_request.end_date}',
            priority='medium',
            related_student=leave_request.student,
            related_course=leave_request.course_offering
        )


def get_user_notifications(user, unread_only=False, limit=10):
    """
    Get notifications for a user
    
    Args:
        user: User to get notifications for
        unread_only: If True, only return unread notifications
        limit: Maximum number of notifications to return
    
    Returns:
        QuerySet of notifications
    """
    notifications = Notification.objects.filter(recipient=user)
    
    if unread_only:
        notifications = notifications.filter(is_read=False)
    
    return notifications[:limit]


def mark_notifications_as_read(user, notification_ids=None):
    """
    Mark notifications as read for a user
    
    Args:
        user: User whose notifications to mark as read
        notification_ids: List of notification IDs to mark as read (optional)
                         If None, marks all unread notifications as read
    """
    notifications = Notification.objects.filter(recipient=user, is_read=False)
    
    if notification_ids:
        notifications = notifications.filter(id__in=notification_ids)
    
    # Update all notifications
    notifications.update(is_read=True, read_at=timezone.now())


def get_unread_notification_count(user):
    """Get count of unread notifications for a user"""
    return Notification.objects.filter(recipient=user, is_read=False).count()
