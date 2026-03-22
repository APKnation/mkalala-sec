from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.decorators import csrf_exempt
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count, Avg, Sum
from django.core.paginator import Paginator
import json

from .models import (
    User, StudentProfile, FacultyProfile, Announcement, 
    Attendance, StudentClass, CourseOffering, Enrollment, Grade,
    AdminProfile, HeadmasterProfile, Message
)
from .utils import is_student, is_faculty, is_admin, is_headmaster
from .forms import AnnouncementForm, AttendanceForm

@login_required
@user_passes_test(is_student)
def student_unified_dashboard(request, page='overview'):
    """
    Student unified dashboard view that handles all student dashboard pages
    """
    user = request.user
    
    # Get student profile
    try:
        student_profile = user.student_profile
    except StudentProfile.DoesNotExist:
        return redirect('student_dashboard')
    
    # Handle message creation for messages page
    if page == 'messages' and request.method == 'POST':
        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            recipient_id = request.POST.get('recipient')
            subject = request.POST.get('subject')
            body = request.POST.get('body')
            
            if recipient_id and subject and body:
                try:
                    recipient = User.objects.get(id=recipient_id)
                    Message.objects.create(
                        sender=user,
                        recipient=recipient,
                        subject=subject,
                        body=body
                    )
                    return JsonResponse({
                        'success': True,
                        'message': 'Message sent successfully!'
                    })
                except User.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'message': 'Recipient not found.'
                    })
                except Exception as e:
                    return JsonResponse({
                        'success': False,
                        'message': f'Error sending message: {str(e)}'
                    })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Please fill in all fields.'
                })
    
    # Base context
    context = {
        'user': user,
        'student_profile': student_profile,
        'current_page': page,
        'page_title': get_student_page_title(page),
        'user_role_display': 'Student',
    }
    
    # Add page-specific context
    if page == 'overview':
        context.update(get_student_overview_context(user, student_profile))
    elif page == 'attendance':
        context.update(get_student_attendance_context(user, student_profile))
    elif page == 'announcements':
        context.update(get_student_announcements_context(user, student_profile))
    elif page == 'courses':
        context.update(get_student_courses_context(user, student_profile))
    elif page == 'results':
        context.update(get_student_results_context(user, student_profile))
    elif page == 'timetable':
        context.update(get_student_timetable_context(user, student_profile))
    elif page == 'assignments':
        context.update(get_student_assignments_context(user, student_profile))
    elif page == 'exams':
        context.update(get_student_exams_context(user, student_profile))
    elif page == 'fees':
        context.update(get_student_fees_context(user, student_profile))
    elif page == 'library':
        context.update(get_student_library_context(user, student_profile))
    elif page == 'messages':
        context.update(get_student_messages_context(user, student_profile))
    elif page == 'profile':
        context.update(get_student_profile_context(user, student_profile))
    
    return render(request, 'core/student_unified_dashboard.html', context)

@login_required
def admin_unified_dashboard(request, page='overview'):
    """
    Admin unified dashboard view that handles all admin dashboard pages
    """
    user = request.user
    
    # Get admin profile
    try:
        admin_profile = user.admin_profile
    except AdminProfile.DoesNotExist:
        admin_profile = None
    
    # Get pending users count for notification badge
    pending_users_count = User.objects.filter(is_active=False).count()
    
    context = {
        'user': user,
        'admin_profile': admin_profile,
        'current_page': page,
        'page_title': get_admin_page_title(page),
        'user_role_display': 'Administrator',
        'pending_users_count': pending_users_count,
    }
    
    # Add page-specific context
    if page == 'overview':
        context.update(get_admin_overview_context(user, admin_profile))
    elif page == 'users':
        context.update(get_admin_users_context(user, admin_profile))
    elif page == 'students':
        context.update(get_admin_students_context(request, user, admin_profile))
    elif page == 'teachers':
        context.update(get_admin_teachers_context(user, admin_profile))
    elif page == 'courses':
        context.update(get_admin_courses_context(user, admin_profile))
    elif page == 'classes':
        context.update(get_admin_classes_context(user, admin_profile))
    elif page == 'subjects':
        context.update(get_admin_subjects_context(user, admin_profile))
    elif page == 'add-subject':
        context_result = get_admin_add_subject_context(request, user, admin_profile)
        # Handle redirect responses
        if hasattr(context_result, 'status_code'):
            return context_result
        context.update(context_result)
    elif page == 'add-class':
        context_result = get_admin_add_class_context(request, user, admin_profile)
        # Handle redirect responses
        if hasattr(context_result, 'status_code'):
            return context_result
        context.update(context_result)
    elif page == 'edit-class':
        context_result = get_admin_edit_class_context(request, user, admin_profile)
        # Handle redirect responses
        if hasattr(context_result, 'status_code'):
            return context_result
        context.update(context_result)
    elif page == 'delete-class':
        context_result = get_admin_delete_class_context(request, user, admin_profile)
        # Handle redirect responses
        if hasattr(context_result, 'status_code'):
            return context_result
        context.update(context_result)
    elif page == 'mark-attendance':
        context_result = get_admin_mark_attendance_context(request, user, admin_profile)
        # Handle redirect responses (both redirect and HttpResponse)
        if hasattr(context_result, 'status_code'):
            return context_result
        context.update(context_result)
    elif page == 'export-attendance':
        context_result = get_admin_export_attendance_context(request, user, admin_profile)
        # Handle redirect responses (both redirect and HttpResponse)
        if hasattr(context_result, 'status_code'):
            return context_result
        context.update(context_result)
    elif page == 'view-attendance':
        context_result = get_admin_view_attendance_context(request, user, admin_profile)
        # Handle redirect responses
        if hasattr(context_result, 'status_code'):
            return context_result
        context.update(context_result)
    elif page == 'edit-attendance':
        context_result = get_admin_edit_attendance_context(request, user, admin_profile)
        # Handle redirect responses
        if hasattr(context_result, 'status_code'):
            return context_result
        context.update(context_result)
    elif page == 'delete-attendance':
        context_result = get_admin_delete_attendance_context(request, user, admin_profile)
        # Handle redirect responses
        if hasattr(context_result, 'status_code'):
            return context_result
        context.update(context_result)
    elif page == 'add-grade':
        context_result = get_admin_add_grade_context(request, user, admin_profile)
        if hasattr(context_result, 'status_code'):
            return context_result
        context.update(context_result)
    elif page == 'attendance':
        context.update(get_admin_attendance_context(user, admin_profile))
    elif page == 'grading':
        context.update(get_admin_grading_context(user, admin_profile))
    elif page == 'exams':
        context.update(get_admin_exams_context(user, admin_profile))
    elif page == 'create-exam':
        context.update(get_admin_exams_context(user, admin_profile))
    elif page == 'announcements':
        context.update(get_admin_announcements_context(user, admin_profile))
    elif page == 'fees':
        context.update(get_admin_fees_context(user, admin_profile))
    elif page == 'reports':
        context.update(get_admin_reports_context(user, admin_profile))
    elif page == 'timetable':
        context.update(get_admin_timetable_context(user, admin_profile))
    elif page == 'users':
        context.update(get_admin_users_context(user, admin_profile))
    elif page == 'create-user':
        context_result = get_admin_create_user_context(request, user, admin_profile)
        # Handle form submission for create-user
        if hasattr(context_result, 'status_code'):
            return context_result
        context.update(context_result)
    elif page == 'edit-user':
        context_result = get_admin_edit_user_context(request, user, admin_profile)
        # Handle form submission for edit-user
        if hasattr(context_result, 'status_code'):
            return context_result
        context.update(context_result)
    elif page == 'create-student':
        context.update(get_admin_create_student_context(request, user, admin_profile))
    elif page == 'delete-user':
        context_result = get_admin_delete_user_context(request, user, admin_profile)
        # Handle form submission for delete-user
        if hasattr(context_result, 'status_code'):
            return context_result
        context.update(context_result)
    elif page == 'settings':
        context.update(get_admin_settings_context(user, admin_profile))
    elif page == 'logs':
        context.update(get_admin_logs_context(user, admin_profile))
    elif page == 'profile':
        context.update(get_admin_profile_context(user, admin_profile))
    elif page == 'pending-users':
        context.update(get_admin_pending_users_context(user, admin_profile))
    
    return render(request, 'core/admin_unified_dashboard.html', context)

@login_required
def headmaster_unified_dashboard(request, page='overview'):
    """
    Headmaster unified dashboard view that handles all headmaster dashboard pages
    """
    user = request.user
    
    # Get headmaster profile
    try:
        headmaster_profile = user.headmaster_profile
    except HeadmasterProfile.DoesNotExist:
        headmaster_profile = None
    
    context = {
        'user': user,
        'headmaster_profile': headmaster_profile,
        'current_page': page,
        'page_title': get_headmaster_page_title(page),
        'user_role_display': 'Headmaster',
    }
    
    # Add page-specific context
    if page == 'overview':
        context.update(get_headmaster_overview_context(user, headmaster_profile))
    elif page == 'staff':
        context.update(get_headmaster_staff_context(user, headmaster_profile))
    elif page == 'performance':
        context.update(get_headmaster_performance_context(user, headmaster_profile))
    elif page == 'discipline':
        context.update(get_headmaster_discipline_context(user, headmaster_profile))
    elif page == 'reports':
        context.update(get_headmaster_reports_context(user, headmaster_profile))
    elif page == 'attendance':
        context.update(get_headmaster_attendance_context(user, headmaster_profile))
    elif page == 'grading':
        context.update(get_headmaster_grading_context(user, headmaster_profile))
    elif page == 'exams':
        context.update(get_headmaster_exams_context(user, headmaster_profile))
    elif page == 'announcements':
        context.update(get_headmaster_announcements_context(user, headmaster_profile))
    elif page == 'events':
        context.update(get_headmaster_events_context(user, headmaster_profile))
    elif page == 'fees':
        context.update(get_headmaster_fees_context(user, headmaster_profile))
    elif page == 'messages':
        context.update(get_headmaster_messages_context(user, headmaster_profile))
    elif page == 'profile':
        context.update(get_headmaster_profile_context(user, headmaster_profile))
    
    return render(request, 'core/headmaster_unified_dashboard.html', context)

# AJAX Load Functions
@login_required
def load_student_dashboard_page(request, page):
    """AJAX endpoint to load student dashboard page content"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request'})
    
    user = request.user
    
    try:
        # Get page-specific content
        context = {
            'user': user,
            'current_page': page,
        }
        
        if page == 'overview':
            try:
                student_profile = user.student_profile
                context.update(get_student_overview_context(user, student_profile))
            except:
                pass
            template = 'core/student_parts/overview.html'
        elif page == 'attendance':
            template = 'core/student_parts/attendance.html'
        elif page == 'announcements':
            template = 'core/student_parts/announcements.html'
        elif page == 'courses':
            template = 'core/student_parts/courses.html'
        elif page == 'results':
            template = 'core/student_parts/results.html'
        elif page == 'timetable':
            template = 'core/student_parts/timetable.html'
        elif page == 'assignments':
            template = 'core/student_parts/assignments.html'
        elif page == 'exams':
            template = 'core/student_parts/exams.html'
        elif page == 'fees':
            template = 'core/student_parts/fees.html'
        elif page == 'library':
            template = 'core/student_parts/library.html'
        elif page == 'messages':
            template = 'core/student_parts/messages.html'
        elif page == 'profile':
            template = 'core/student_parts/profile.html'
        else:
            return JsonResponse({'success': False, 'error': 'Page not found'})
        
        # Render template content
        content = render(request, template, context).content.decode('utf-8')
        
        return JsonResponse({
            'success': True,
            'content': content,
            'notifications': get_student_notification_counts(user)
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def load_admin_dashboard_page(request, page):
    """AJAX endpoint to load admin dashboard page content"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request'})
    
    user = request.user
    
    try:
        context = {
            'user': user,
            'current_page': page,
        }
        
        # Get page-specific template
        templates = {
            'overview': 'core/admin_parts/overview.html',
            'users': 'core/admin_parts/users.html',
            'students': 'core/admin_parts/students.html',
            'teachers': 'core/admin_parts/teachers.html',
            'courses': 'core/admin_parts/courses.html',
            'classes': 'core/admin_parts/classes.html',
            'subjects': 'core/admin_parts/subjects.html',
            'attendance': 'core/admin_parts/attendance.html',
            'grading': 'core/admin_parts/grading.html',
            'exams': 'core/admin_parts/exams.html',
            'announcements': 'core/admin_parts/announcements.html',
            'fees': 'core/admin_parts/fees.html',
            'reports': 'core/admin_parts/reports.html',
            'settings': 'core/admin_parts/settings.html',
            'logs': 'core/admin_parts/logs.html',
            'profile': 'core/admin_parts/profile.html',
        }
        
        template = templates.get(page)
        if not template:
            return JsonResponse({'success': False, 'error': 'Page not found'})
        
        # Render template content
        content = render(request, template, context).content.decode('utf-8')
        
        return JsonResponse({
            'success': True,
            'content': content,
            'notifications': get_admin_notification_counts(user)
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def load_headmaster_dashboard_page(request, page):
    """AJAX endpoint to load headmaster dashboard page content"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request'})
    
    user = request.user
    
    try:
        context = {
            'user': user,
            'current_page': page,
        }
        
        # Get page-specific template
        templates = {
            'overview': 'core/headmaster_parts/overview.html',
            'staff': 'core/headmaster_parts/staff.html',
            'performance': 'core/headmaster_parts/performance.html',
            'discipline': 'core/headmaster_parts/discipline.html',
            'reports': 'core/headmaster_parts/reports.html',
            'attendance': 'core/headmaster_parts/attendance.html',
            'grading': 'core/headmaster_parts/grading.html',
            'exams': 'core/headmaster_parts/exams.html',
            'announcements': 'core/headmaster_parts/announcements.html',
            'events': 'core/headmaster_parts/events.html',
            'fees': 'core/headmaster_parts/fees.html',
            'messages': 'core/headmaster_parts/messages.html',
            'profile': 'core/headmaster_parts/profile.html',
        }
        
        template = templates.get(page)
        if not template:
            return JsonResponse({'success': False, 'error': 'Page not found'})
        
        # Render template content
        content = render(request, template, context).content.decode('utf-8')
        
        return JsonResponse({
            'success': True,
            'content': content,
            'notifications': get_headmaster_notification_counts(user)
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# Notification Functions
@login_required
def get_student_notifications(request):
    """AJAX endpoint to get student notification counts"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request'})
    
    try:
        notifications = get_student_notification_counts(request.user)
        return JsonResponse({'success': True, 'notifications': notifications})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def get_admin_notifications(request):
    """AJAX endpoint to get admin notification counts"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request'})
    
    try:
        notifications = get_admin_notification_counts(request.user)
        return JsonResponse({'success': True, 'notifications': notifications})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def get_headmaster_notifications(request):
    """AJAX endpoint to get headmaster notification counts"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request'})
    
    try:
        notifications = get_headmaster_notification_counts(request.user)
        return JsonResponse({'success': True, 'notifications': notifications})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# Helper Functions
def get_student_page_title(page):
    titles = {
        'overview': 'Student Dashboard',
        'attendance': 'My Attendance',
        'announcements': 'Announcements',
        'courses': 'My Courses',
        'results': 'Results & Grades',
        'timetable': 'My Schedule',
        'assignments': 'Assignments',
        'exams': 'Exams',
        'fees': 'Fees',
        'library': 'Library',
        'messages': 'Messages',
        'profile': 'Profile Settings'
    }
    return titles.get(page, 'Student Dashboard')

def get_admin_page_title(page):
    titles = {
        'overview': 'Admin Dashboard',
        'users': 'User Management',
        'create-user': 'Create User',
        'edit-user': 'Edit User',
        'students': 'Students',
        'teachers': 'Teachers',
        'courses': 'Courses',
        'classes': 'Classes',
        'subjects': 'Subjects',
        'add-subject': 'Add Subject',
        'add-class': 'Add Class',
        'edit-class': 'Edit Class',
        'delete-class': 'Delete Class',
        'mark-attendance': 'Mark Attendance',
        'export-attendance': 'Export Attendance',
        'view-attendance': 'View Attendance',
        'edit-attendance': 'Edit Attendance',
        'delete-attendance': 'Delete Attendance',
        'add-grade': 'Add Grade',
        'attendance': 'Attendance',
        'grading': 'Grading',
        'exams': 'Exams',
        'announcements': 'Announcements',
        'fees': 'Fees',
        'library': 'Library',
        'reports': 'Reports',
        'settings': 'System Settings',
        'logs': 'Activity Logs',
        'profile': 'Profile Settings'
    }
    return titles.get(page, 'Admin Dashboard')

def get_headmaster_page_title(page):
    titles = {
        'overview': 'Headmaster Dashboard',
        'staff': 'Staff Management',
        'performance': 'School Performance',
        'discipline': 'Discipline',
        'reports': 'Reports',
        'attendance': 'Attendance Overview',
        'grading': 'Grading Analytics',
        'exams': 'Exam Results',
        'announcements': 'School Announcements',
        'events': 'Events & Calendar',
        'facilities': 'Facilities',
        'fees': 'Financial Overview',
        'messages': 'Messages',
        'parent-portal': 'Parent Portal',
        'profile': 'Profile Settings'
    }
    return titles.get(page, 'Headmaster Dashboard')

# Context Functions
def get_student_overview_context(user, student_profile):
    """Get student overview page context"""
    context = {}
    
    if student_profile:
        context.update({
            'my_courses': student_profile.enrolled_subjects.count(),
            'attendance_rate': 85,  # Placeholder
            'average_grade': 'B+',  # Placeholder
            'pending_assignments': 3,  # Placeholder
            'unread_announcements': 2,  # Placeholder
            'unread_messages': 1,  # Placeholder
        })
    else:
        context.update({
            'my_courses': 0,
            'attendance_rate': 0,
            'average_grade': 'N/A',
            'pending_assignments': 0,
            'unread_announcements': 0,
            'unread_messages': 0,
        })
    
    return context

def get_admin_overview_context(user, admin_profile):
    """Get admin overview page context"""
    from django.utils import timezone
    from datetime import timedelta, date
    
    # Import notification utilities
    from .notification_utils import get_user_notifications, get_unread_notification_count
    
    # Get current date and date ranges for monthly trends
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)
    
    # Monthly trends data
    monthly_trends = {
        'student_growth': {
            'this_month': StudentProfile.objects.filter(
                user__date_joined__gte=this_month_start
            ).count(),
            'last_month': StudentProfile.objects.filter(
                user__date_joined__gte=last_month_start,
                user__date_joined__lt=this_month_start
            ).count(),
        },
        'fee_collection': {
            'this_month': 0,  # Placeholder - no payment data in overview
            'last_month': 0,  # Placeholder - no payment data in overview
        },
    }
    
    # Get teacher statistics for template compatibility
    teachers = User.objects.filter(role='teacher').select_related('faculty_profile').order_by('first_name', 'last_name')
    
    # Get additional statistics
    from core.models import Department, Subject, StudentClass, Announcement, Enrollment, Grade
    
    # Get real notifications
    notifications = get_user_notifications(user, limit=10)
    unread_notifications = get_unread_notification_count(user)
    
    context = {
        'total_users': User.objects.count(),
        'total_students': User.objects.filter(role='student').count(),
        'total_teachers': User.objects.filter(role='teacher').count(),
        'total_courses': CourseOffering.objects.count(),
        'pending_announcements': Announcement.objects.filter(is_active=False).count(),
        'monthly_trends': monthly_trends,
        # Add teacher statistics for template compatibility
        'teachers': teachers,
        'total_teachers': teachers.count(),
        'active_teachers': teachers.filter(is_active=True).count(),
        
        # New enhanced statistics
        'total_classes': StudentClass.objects.count(),
        'total_departments': Department.objects.count(),
        'total_subjects': Subject.objects.count(),
        'new_users_today': User.objects.filter(date_joined__date=today).count(),
        'active_sessions': 15,  # Placeholder - would need session tracking
        'pending_tasks': Announcement.objects.filter(is_active=False).count() + 3,  # Placeholder
        
        # Recent activity data (simplified for now)
        'recent_enrollments': Enrollment.objects.order_by('-enrollment_date')[:5],
        'recent_grades': Grade.objects.order_by('-awarded_on')[:5],
        'recent_announcements': Announcement.objects.order_by('-created_at')[:5],
        
        # Real notifications
        'notifications': notifications,
        'unread_notifications': unread_notifications,
    }
    
    return context

def get_admin_pending_users_context(user, admin_profile):
    """Get admin pending users page context"""
    # Get pending users (inactive users who need approval)
    pending_users = User.objects.filter(is_active=False).select_related(
        'student_profile', 'faculty_profile', 'admin_profile', 'headmaster_profile'
    ).order_by('-date_joined')
    
    # Get teacher statistics for template compatibility (same as overview)
    teachers = User.objects.filter(role='teacher').select_related('faculty_profile').order_by('first_name', 'last_name')
    
    context = {
        'pending_users': pending_users,
        'pending_users_count': pending_users.count(),
        # Add teacher statistics for template compatibility
        'teachers': teachers,
        'total_teachers': teachers.count(),
        'active_teachers': teachers.filter(is_active=True).count(),
        'total_users': User.objects.count(),
        'total_students': User.objects.filter(role='student').count(),
    }
    
    return context

def get_headmaster_overview_context(user, headmaster_profile):
    """Get headmaster overview page context"""
    context = {
        'total_students': User.objects.filter(role='student').count(),
        'total_teachers': User.objects.filter(role='teacher').count(),
        'attendance_rate': 92,  # Placeholder
        'discipline_cases': 2,  # Placeholder
        'urgent_messages': 1,  # Placeholder
    }
    
    return context

def get_student_overview_context(user, student_profile):
    """Get student overview page context"""
    enrollments = Enrollment.objects.filter(student=student_profile).select_related('course_offering', 'course_offering__course', 'course_offering__faculty')
    attendance_count = Attendance.objects.filter(enrollment__student=student_profile).count()
    
    return {
        'my_courses': enrollments.count(),
        'pending_tasks': Enrollment.objects.filter(student=student_profile, grade__isnull=True).count(),
        'attendance_rate': 85,  # Calculate actual attendance rate
        'recent_grades': Grade.objects.filter(enrollment__student=student_profile).order_by('-awarded_on')[:5],
        'enrollments': enrollments,
        'attendance_count': attendance_count,
    }

def get_student_attendance_context(user, student_profile):
    """Get student attendance page context"""
    attendance_records = Attendance.objects.filter(enrollment__student=student_profile).select_related('enrollment', 'enrollment__course_offering').order_by('-date')
    
    return {
        'attendance_records': attendance_records[:50],
        'total_records': attendance_records.count(),
        'present_count': attendance_records.filter(status='P').count(),
        'absent_count': attendance_records.filter(status='A').count(),
        'late_count': attendance_records.filter(status='L').count(),
    }

def get_student_announcements_context(user, student_profile):
    """Get student announcements page context"""
    # Get announcements for student's courses
    student_courses = CourseOffering.objects.filter(enrollments__student=student_profile)
    announcements = Announcement.objects.filter(
        Q(target_class__in=student_courses.values_list('id', flat=True)) | Q(target_class__isnull=True)
    ).filter(is_active=True).order_by('-created_at')[:20]
    
    return {
        'announcements': announcements,
        'total_announcements': announcements.count(),
        'unread_announcements': announcements.count(),  # You may need to add read status tracking
    }

def get_student_courses_context(user, student_profile):
    """Get student courses page context"""
    enrollments = Enrollment.objects.filter(student=student_profile).select_related(
        'course_offering', 'course_offering__course', 'course_offering__faculty'
    ).order_by('course_offering__course__name')
    
    return {
        'enrollments': enrollments,
        'my_courses': enrollments.count(),
    }

def get_student_results_context(user, student_profile):
    """Get student results page context"""
    grades = Grade.objects.filter(enrollment__student=student_profile).select_related(
        'enrollment', 'enrollment__course_offering', 'enrollment__course_offering__course'
    ).order_by('-awarded_on')
    
    return {
        'grades': grades,
        'total_grades': grades.count(),
        'average_grade': grades.aggregate(avg=Avg('points'))['avg'] or 0,
        'latest_grades': grades[:10],
    }

def get_student_timetable_context(user, student_profile):
    """Get student timetable page context"""
    # Get student's enrolled courses
    enrollments = Enrollment.objects.filter(student=student_profile).select_related('course_offering')
    
    return {
        'enrollments': enrollments,
        'courses': enrollments.values_list('course_offering__course__name', 'course_offering__course__code'),
    }

def get_student_assignments_context(user, student_profile):
    """Get student assignments page context"""
    # Placeholder for assignment data - you may need to add Assignment model
    return {
        'assignments': [],
        'pending_assignments': 3,  # Calculate from actual data
        'completed_assignments': 5,  # Calculate from actual data
    }

def get_student_exams_context(user, student_profile):
    """Get student exams page context"""
    # Placeholder for exam data
    return {
        'exams': [],
        'upcoming_exams': 0,
        'completed_exams': 0,
    }

def get_student_fees_context(user, student_profile):
    """Get student fees page context"""
    # Placeholder for fee data
    return {
        'fee_records': [],
        'total_fees': 0,
        'paid_fees': 0,
        'pending_fees': 0,
    }

def get_student_library_context(user, student_profile):
    """Get student library page context"""
    # Placeholder for library data
    return {
        'library_items': [],
        'borrowed_books': 0,
        'reserved_books': 0,
    }

def get_student_messages_context(user, student_profile):
    """Get student messages page context"""
    from .models import User, Message
    from django.utils import timezone
    
    print("=== GET STUDENT MESSAGES CONTEXT CALLED ===")
    print(f"User: {user.username} (ID: {user.id})")
    
    # Get received messages
    received_messages = Message.objects.filter(
        recipient=user
    ).select_related('sender').order_by('-sent_at')
    
    # Get sent messages
    sent_messages = Message.objects.filter(
        sender=user
    ).select_related('recipient').order_by('-sent_at')
    
    # Count unread messages
    unread_count = received_messages.filter(is_read=False).count()
    
    # Calculate total messages
    total_messages = received_messages.count() + sent_messages.count()
    
    # Add helper methods to messages
    for message in received_messages:
        message.days_ago = (timezone.now().date() - message.sent_at.date()).days
        message.is_recent = message.sent_at.date() >= timezone.now().date() - timezone.timedelta(days=7)
        message.sender_name = message.sender.get_full_name() or message.sender.username
        message.sender_role = 'Teacher' if message.sender.role == 'teacher' else ('Headmaster' if message.sender.role == 'headmaster' else ('Admin' if message.sender.is_staff and not message.sender.is_superuser else 'Staff'))
    
    for message in sent_messages:
        message.days_ago = (timezone.now().date() - message.sent_at.date()).days
        message.is_recent = message.sent_at.date() >= timezone.now().date() - timezone.timedelta(days=7)
        message.recipient_name = message.recipient.get_full_name() or message.recipient.username
        message.recipient_role = 'Teacher' if message.recipient.role == 'teacher' else ('Headmaster' if message.recipient.role == 'headmaster' else ('Admin' if message.recipient.is_staff and not message.recipient.is_superuser else 'Staff'))
    
    # Debug: Check all users and their roles
    all_users = User.objects.all()
    print(f"Total users in database: {all_users.count()}")
    for user_obj in all_users:
        print(f"User: {user_obj.username} - Role: {user_obj.role} - Staff: {user_obj.is_staff} - Superuser: {user_obj.is_superuser}")
    
    # Get teachers - users with role='teacher'
    teachers = User.objects.filter(role='teacher').exclude(id=user.id).order_by('first_name', 'last_name')
    print(f"Found {teachers.count()} teachers:")
    for teacher in teachers:
        print(f"  - {teacher.username} ({teacher.get_full_name()})")
    
    # Get headmasters - users with role='headmaster'  
    headmasters = User.objects.filter(role='headmaster').exclude(id=user.id).order_by('first_name', 'last_name')
    print(f"Found {headmasters.count()} headmasters:")
    for headmaster in headmasters:
        print(f"  - {headmaster.username} ({headmaster.get_full_name()})")
    
    # Get admins - more inclusive approach: staff users who are not students, teachers, or headmasters
    admins = User.objects.filter(
        is_staff=True
    ).exclude(
        id=user.id
    ).exclude(
        role__in=['student', 'teacher', 'headmaster']
    ).order_by('first_name', 'last_name')
    
    # Also try alternative: superusers who are not students/teachers/headmasters
    superusers = User.objects.filter(
        is_superuser=True
    ).exclude(
        id=user.id
    ).exclude(
        role__in=['student', 'teacher', 'headmaster']
    ).order_by('first_name', 'last_name')
    
    # Combine admins and superusers, removing duplicates
    all_admins = (admins | superusers).distinct().order_by('first_name', 'last_name')
    
    print(f"Found {admins.count()} staff admins:")
    for admin in admins:
        print(f"  - {admin.username} ({admin.get_full_name()}) - Staff: {admin.is_staff}, Superuser: {admin.is_superuser}")
    
    print(f"Found {superusers.count()} superuser admins:")
    for su in superusers:
        print(f"  - {su.username} ({su.get_full_name()}) - Staff: {su.is_staff}, Superuser: {su.is_superuser}")
    
    print(f"Total combined admins: {all_admins.count()}")
    for admin in all_admins:
        print(f"  - {admin.username} ({admin.get_full_name()}) - Role: {admin.role}, Staff: {admin.is_staff}, Superuser: {admin.is_superuser}")
    
    # Use the combined list
    admins = all_admins
    
    print("=== CONTEXT DATA FOR TEMPLATE ===")
    print(f"Teachers count: {len(teachers)}")
    print(f"Headmasters count: {len(headmasters)}")
    print(f"Admins count: {len(admins)}")
    print(f"Teachers: {[str(t) for t in teachers]}")
    print(f"Headmasters: {[str(h) for h in headmasters]}")
    print(f"Admins: {[str(a) for a in admins]}")
    print("=== END CONTEXT DATA ===")
    
    return {
        'student': student_profile,
        'received_messages': received_messages,
        'sent_messages': sent_messages,
        'unread_count': unread_count,
        'total_messages': total_messages,
        'teachers': teachers,
        'headmasters': headmasters,
        'admins': admins,
        'today': timezone.now().date(),
        'yesterday': timezone.now().date() - timezone.timedelta(days=1),
    }

def get_student_profile_context(user, student_profile):
    return {'user_profile': user}

def get_admin_users_context(user, admin_profile):
    """Get admin users page context"""
    from django.utils import timezone
    from datetime import timedelta
    
    # Get current date and date ranges for monthly trends
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)
    
    # Monthly trends data
    monthly_trends = {
        'student_growth': {
            'this_month': StudentProfile.objects.filter(
                user__date_joined__gte=this_month_start
            ).count(),
            'last_month': StudentProfile.objects.filter(
                user__date_joined__gte=last_month_start,
                user__date_joined__lt=this_month_start
            ).count(),
        },
        'fee_collection': {
            'this_month': 0,  # Placeholder - no payment data in users context
            'last_month': 0,  # Placeholder - no payment data in users context
        },
    }
    
    users = User.objects.all().order_by('-date_joined')[:20]
    
    # Get pending users for approval
    pending_users = User.objects.filter(is_active=False)
    
    # Get teacher statistics for template compatibility
    teachers = User.objects.filter(role='teacher').select_related('faculty_profile').order_by('first_name', 'last_name')
    
    return {
        'users': users,
        'total_users': users.count(),
        'students_count': User.objects.filter(role='student').count(),
        'teachers_count': User.objects.filter(role='teacher').count(),
        'admins_count': User.objects.filter(role='admin').count(),
        'pending_users': pending_users,
        'pending_users_count': pending_users.count(),
        'pending_students_count': pending_users.filter(role='student').count(),
        'pending_teachers_count': pending_users.filter(role='teacher').count(),
        'pending_admins_count': pending_users.filter(role='admin').count(),
        'teachers': teachers,
        'total_teachers': teachers.count(),
        'active_teachers': teachers.filter(is_active=True).count(),
        'monthly_trends': monthly_trends,  # Add monthly trends for reports template
    }

def get_admin_students_context(request, user, admin_profile):
    """Get admin students page context"""
    from .models import Department
    from django.db.models import Q
    from django.utils import timezone
    from datetime import timedelta
    
    # Get current date and date ranges for monthly trends
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)
    
    # Monthly trends data
    monthly_trends = {
        'student_growth': {
            'this_month': StudentProfile.objects.filter(
                user__date_joined__gte=this_month_start
            ).count(),
            'last_month': StudentProfile.objects.filter(
                user__date_joined__gte=last_month_start,
                user__date_joined__lt=this_month_start
            ).count(),
        },
        'fee_collection': {
            'this_month': 0,  # Placeholder - no payment data in students context
            'last_month': 0,  # Placeholder - no payment data in students context
        },
    }
    
    # Get all students with related data
    students = StudentProfile.objects.select_related(
        'user', 'department'
    ).prefetch_related(
        'enrollments__course_offering__course',
        'enrollments__attendances'
    ).order_by('-user__date_joined')
    
    # Get departments for filter
    departments = Department.objects.all()
    
    # Apply filters from request
    search_query = request.GET.get('search', '')
    department_filter = request.GET.get('department', '')
    status_filter = request.GET.get('status', '')
    
    if search_query:
        students = students.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(roll_number__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    if department_filter:
        students = students.filter(department_id=department_filter)
    
    if status_filter:
        if status_filter == 'active':
            students = students.filter(user__is_active=True)
        elif status_filter == 'inactive':
            students = students.filter(user__is_active=False)
    
    # Get teacher statistics for template compatibility
    teachers = User.objects.filter(role='teacher').select_related('faculty_profile').order_by('first_name', 'last_name')
    
    return {
        'students': students,
        'departments': departments,
        'total_students': students.count(),
        'active_students': students.filter(user__is_active=True).count(),
        'inactive_students': students.filter(user__is_active=False).count(),
        'active_students_percentage': (students.filter(user__is_active=True).count() * 100) // students.count() if students.count() > 0 else 0,
        'inactive_students_percentage': (students.filter(user__is_active=False).count() * 100) // students.count() if students.count() > 0 else 0,
        'new_students_this_month': 0,  # TODO: Calculate from Enrollment model if needed
        'search_query': search_query,
        'department_filter': department_filter,
        'status_filter': status_filter,
        'monthly_trends': monthly_trends,  # Add monthly trends for reports template
        # Add teacher statistics for template compatibility
        'teachers': teachers,
        'total_teachers': teachers.count(),
        'active_teachers': teachers.filter(is_active=True).count(),
    }

def get_admin_teachers_context(user, admin_profile):
    """Get admin teachers page context"""
    from django.utils import timezone
    from datetime import timedelta
    
    # Get current date and date ranges for monthly trends
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)
    
    # Monthly trends data
    monthly_trends = {
        'student_growth': {
            'this_month': StudentProfile.objects.filter(
                user__date_joined__gte=this_month_start
            ).count(),
            'last_month': StudentProfile.objects.filter(
                user__date_joined__gte=last_month_start,
                user__date_joined__lt=this_month_start
            ).count(),
        },
        'fee_collection': {
            'this_month': 0,  # Placeholder - no payment data in teachers context
            'last_month': 0,  # Placeholder - no payment data in teachers context
        },
    }
    
    teachers = User.objects.filter(role='teacher').select_related('faculty_profile').order_by('first_name', 'last_name')
    return {
        'teachers': teachers,
        'total_teachers': teachers.count(),
        'active_teachers': teachers.filter(is_active=True).count(),
        'monthly_trends': monthly_trends,  # Add monthly trends for reports template
    }

def get_admin_courses_context(user, admin_profile):
    """Get admin courses page context"""
    from .models import CourseOffering, Subject, Department
    from django.utils import timezone
    from datetime import timedelta
    
    courses = CourseOffering.objects.all().select_related('course', 'faculty').order_by('course__name')
    subjects = Subject.objects.all().order_by('name')
    departments = Department.objects.all().order_by('name')
    
    # Get teacher statistics for template compatibility
    teachers = User.objects.filter(role='teacher').select_related('faculty_profile').order_by('first_name', 'last_name')
    
    # Get current date and date ranges for monthly trends
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)
    
    # Monthly trends data
    monthly_trends = {
        'student_growth': {
            'this_month': StudentProfile.objects.filter(
                user__date_joined__gte=this_month_start
            ).count(),
            'last_month': StudentProfile.objects.filter(
                user__date_joined__gte=last_month_start,
                user__date_joined__lt=this_month_start
            ).count(),
        },
        'fee_collection': {
            'this_month': 0,  # Placeholder - no payment data in courses context
            'last_month': 0,  # Placeholder - no payment data in courses context
        },
    }
    
    return {
        'courses': courses,
        'total_courses': courses.count(),
        'active_offerings': courses.count(),  # All offerings are considered active
        'total_subjects': subjects.count(),
        'total_departments': departments.count(),
        # Add teacher statistics for template compatibility
        'teachers': teachers,
        'total_teachers': teachers.count(),
        'active_teachers': teachers.filter(is_active=True).count(),
        # Add monthly trends for template compatibility
        'monthly_trends': monthly_trends,
    }

def get_admin_classes_context(user, admin_profile):
    """Get admin classes page context"""
    from django.utils import timezone
    from datetime import timedelta
    
    classes = StudentClass.objects.all().order_by('form_level', 'name')
    
    # Get teacher statistics for template compatibility
    teachers = User.objects.filter(role='teacher').select_related('faculty_profile').order_by('first_name', 'last_name')
    
    # Get current date and date ranges for monthly trends
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)
    
    # Monthly trends data
    monthly_trends = {
        'student_growth': {
            'this_month': StudentProfile.objects.filter(
                user__date_joined__gte=this_month_start
            ).count(),
            'last_month': StudentProfile.objects.filter(
                user__date_joined__gte=last_month_start,
                user__date_joined__lt=this_month_start
            ).count(),
        },
        'fee_collection': {
            'this_month': 0,  # Placeholder - no payment data in classes context
            'last_month': 0,  # Placeholder - no payment data in classes context
        },
    }
    
    return {
        'classes': classes,
        'total_classes': classes.count(),
        'active_classes': classes.filter(is_active=True).count(),
        'total_students': classes.aggregate(total=Sum('current_students'))['total'] or 0,
        # Add teacher statistics for template compatibility
        'teachers': teachers,
        'total_teachers': teachers.count(),
        'active_teachers': teachers.filter(is_active=True).count(),
        # Add monthly trends for template compatibility
        'monthly_trends': monthly_trends,
    }

def get_admin_subjects_context(user, admin_profile):
    """Get admin subjects page context"""
    from .models import Subject, Department
    from django.utils import timezone
    from datetime import timedelta
    
    subjects = Subject.objects.all().order_by('name')
    departments = Department.objects.all().order_by('name')
    
    # Calculate core vs elective subjects
    core_subjects = subjects.filter(is_core=True)
    elective_subjects = subjects.filter(is_core=False)
    
    # Get teacher statistics for template compatibility
    teachers = User.objects.filter(role='teacher').select_related('faculty_profile').order_by('first_name', 'last_name')
    
    # Get current date and date ranges for monthly trends
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)
    
    # Monthly trends data
    monthly_trends = {
        'student_growth': {
            'this_month': StudentProfile.objects.filter(
                user__date_joined__gte=this_month_start
            ).count(),
            'last_month': StudentProfile.objects.filter(
                user__date_joined__gte=last_month_start,
                user__date_joined__lt=this_month_start
            ).count(),
        },
        'fee_collection': {
            'this_month': 0,  # Placeholder - no payment data in subjects context
            'last_month': 0,  # Placeholder - no payment data in subjects context
        },
    }
    
    return {
        'subjects': subjects,
        'total_subjects': subjects.count(),
        'core_subjects': core_subjects.count(),
        'elective_subjects': elective_subjects.count(),
        'total_departments': departments.count(),
        # Add teacher statistics for template compatibility
        'teachers': teachers,
        'total_teachers': teachers.count(),
        'active_teachers': teachers.filter(is_active=True).count(),
        # Add monthly trends for template compatibility
        'monthly_trends': monthly_trends,
    }

def get_admin_add_subject_context(request, user, admin_profile):
    """Get admin add subject page context"""
    from .forms import SubjectForm
    
    # Handle form submission
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            from django.contrib import messages
            messages.success(request, f'Subject "{form.instance.name}" has been created successfully!')
            # Redirect back to subjects page
            from django.shortcuts import redirect
            return redirect('admin_unified_dashboard', 'subjects')
    else:
        form = SubjectForm()
    
    # Get teacher statistics for template compatibility
    teachers = User.objects.filter(role='teacher').select_related('faculty_profile').order_by('first_name', 'last_name')
    
    # Get current date and date ranges for monthly trends
    from django.utils import timezone
    from datetime import timedelta
    
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)
    
    # Monthly trends data
    monthly_trends = {
        'student_growth': {
            'this_month': StudentProfile.objects.filter(
                user__date_joined__gte=this_month_start
            ).count(),
            'last_month': StudentProfile.objects.filter(
                user__date_joined__gte=last_month_start,
                user__date_joined__lt=this_month_start
            ).count(),
        },
        'fee_collection': {
            'this_month': 0,  # Placeholder - no payment data in add subject context
            'last_month': 0,  # Placeholder - no payment data in add subject context
        },
    }
    
    return {
        'form': form,
        # Add teacher statistics for template compatibility
        'teachers': teachers,
        'total_teachers': teachers.count(),
        'active_teachers': teachers.filter(is_active=True).count(),
        # Add monthly trends for template compatibility
        'monthly_trends': monthly_trends,
    }

def get_admin_add_class_context(request, user, admin_profile):
    """Get admin add class page context"""
    from django import forms
    from .models import StudentClass, FacultyProfile, Department
    
    # Create a simple form for StudentClass
    class StudentClassForm(forms.ModelForm):
        class Meta:
            model = StudentClass
            fields = ['name', 'form_level', 'class_teacher', 'department', 'max_students', 'current_students', 'academic_year', 'is_active']
            widgets = {
                'name': forms.TextInput(attrs={
                    'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
                    'placeholder': 'Enter class name (e.g., Form 1A, Form 2B)'
                }),
                'form_level': forms.Select(attrs={
                    'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200'
                }),
                'class_teacher': forms.Select(attrs={
                    'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200'
                }),
                'department': forms.Select(attrs={
                    'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200'
                }),
                'max_students': forms.NumberInput(attrs={
                    'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
                    'placeholder': 'Maximum number of students',
                    'min': '1'
                }),
                'current_students': forms.NumberInput(attrs={
                    'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
                    'placeholder': 'Current number of students',
                    'min': '0'
                }),
                'academic_year': forms.NumberInput(attrs={
                    'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
                    'placeholder': 'Academic year (e.g., 2026)',
                    'min': '2020',
                    'max': '2030'
                }),
                'is_active': forms.CheckboxInput(attrs={
                    'class': 'w-4 h-4 text-primary-600 border-neutral-300 rounded focus:ring-primary-500'
                })
            }
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Filter class_teacher queryset to only include teachers
            self.fields['class_teacher'].queryset = FacultyProfile.objects.filter(user__role='teacher')
            self.fields['class_teacher'].empty_label = "Select a class teacher (optional)"
            
            # Set current academic year as default
            if not self.instance.pk:  # Only for new instances
                from django.utils import timezone
                current_year = timezone.now().year
                self.fields['academic_year'].initial = current_year
    
    # Handle form submission
    if request.method == 'POST':
        form = StudentClassForm(request.POST)
        if form.is_valid():
            form.save()
            from django.contrib import messages
            messages.success(request, f'Class "{form.instance.name}" has been created successfully!')
            # Redirect back to classes page
            from django.shortcuts import redirect
            return redirect('admin_unified_dashboard', 'classes')
    else:
        form = StudentClassForm()
    
    # Get teacher statistics for template compatibility
    teachers = User.objects.filter(role='teacher').select_related('faculty_profile').order_by('first_name', 'last_name')
    
    # Get current date and date ranges for monthly trends
    from django.utils import timezone
    from datetime import timedelta
    
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)
    
    # Monthly trends data
    monthly_trends = {
        'student_growth': {
            'this_month': StudentProfile.objects.filter(
                user__date_joined__gte=this_month_start
            ).count(),
            'last_month': StudentProfile.objects.filter(
                user__date_joined__gte=last_month_start,
                user__date_joined__lt=this_month_start
            ).count(),
        },
        'fee_collection': {
            'this_month': 0,  # Placeholder - no payment data in add class context
            'last_month': 0,  # Placeholder - no payment data in add class context
        },
    }
    
    return {
        'form': form,
        # Add teacher statistics for template compatibility
        'teachers': teachers,
        'total_teachers': teachers.count(),
        'active_teachers': teachers.filter(is_active=True).count(),
        # Add monthly trends for template compatibility
        'monthly_trends': monthly_trends,
    }

def get_admin_edit_class_context(request, user, admin_profile):
    """Get admin edit class page context"""
    from django import forms
    from django.shortcuts import get_object_or_404
    from .models import StudentClass, FacultyProfile, Department
    
    # Get class ID from URL parameter
    class_id = request.GET.get('class_id')
    if not class_id:
        # Redirect to classes page if no class ID provided
        from django.shortcuts import redirect
        return redirect('admin_unified_dashboard', 'classes')
    
    # Get the class to edit
    class_obj = get_object_or_404(StudentClass, id=class_id)
    
    # Create a simple form for StudentClass
    class StudentClassForm(forms.ModelForm):
        class Meta:
            model = StudentClass
            fields = ['name', 'form_level', 'class_teacher', 'department', 'max_students', 'current_students', 'academic_year', 'is_active']
            widgets = {
                'name': forms.TextInput(attrs={
                    'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
                    'placeholder': 'Enter class name (e.g., Form 1A, Form 2B)'
                }),
                'form_level': forms.Select(attrs={
                    'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200'
                }),
                'class_teacher': forms.Select(attrs={
                    'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200'
                }),
                'department': forms.Select(attrs={
                    'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200'
                }),
                'max_students': forms.NumberInput(attrs={
                    'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
                    'placeholder': 'Maximum number of students',
                    'min': '1'
                }),
                'current_students': forms.NumberInput(attrs={
                    'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
                    'placeholder': 'Current number of students',
                    'min': '0'
                }),
                'academic_year': forms.NumberInput(attrs={
                    'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
                    'placeholder': 'Academic year (e.g., 2026)',
                    'min': '2020',
                    'max': '2030'
                }),
                'is_active': forms.CheckboxInput(attrs={
                    'class': 'w-4 h-4 text-primary-600 border-neutral-300 rounded focus:ring-primary-500'
                })
            }
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Filter class_teacher queryset to only include teachers
            self.fields['class_teacher'].queryset = FacultyProfile.objects.filter(user__role='teacher')
            self.fields['class_teacher'].empty_label = "Select a class teacher (optional)"
    
    # Handle form submission
    if request.method == 'POST':
        form = StudentClassForm(request.POST, instance=class_obj)
        if form.is_valid():
            form.save()
            from django.contrib import messages
            messages.success(request, f'Class "{form.instance.name}" has been updated successfully!')
            # Redirect back to classes page
            from django.shortcuts import redirect
            return redirect('admin_unified_dashboard', 'classes')
    else:
        form = StudentClassForm(instance=class_obj)
    
    # Get teacher statistics for template compatibility
    teachers = User.objects.filter(role='teacher').select_related('faculty_profile').order_by('first_name', 'last_name')
    
    # Get current date and date ranges for monthly trends
    from django.utils import timezone
    from datetime import timedelta
    
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)
    
    # Monthly trends data
    monthly_trends = {
        'student_growth': {
            'this_month': StudentProfile.objects.filter(
                user__date_joined__gte=this_month_start
            ).count(),
            'last_month': StudentProfile.objects.filter(
                user__date_joined__gte=last_month_start,
                user__date_joined__lt=this_month_start
            ).count(),
        },
        'fee_collection': {
            'this_month': 0,  # Placeholder - no payment data in edit class context
            'last_month': 0,  # Placeholder - no payment data in edit class context
        },
    }
    
    return {
        'form': form,
        'class_obj': class_obj,
        # Add teacher statistics for template compatibility
        'teachers': teachers,
        'total_teachers': teachers.count(),
        'active_teachers': teachers.filter(is_active=True).count(),
        # Add monthly trends for template compatibility
        'monthly_trends': monthly_trends,
    }

def get_admin_delete_class_context(request, user, admin_profile):
    """Get admin delete class page context"""
    from django.shortcuts import get_object_or_404
    from .models import StudentClass
    
    # Get class ID from URL parameter
    class_id = request.GET.get('class_id')
    if not class_id:
        # Redirect to classes page if no class ID provided
        from django.shortcuts import redirect
        return redirect('admin_unified_dashboard', 'classes')
    
    # Get the class to delete
    class_obj = get_object_or_404(StudentClass, id=class_id)
    
    # Handle deletion
    if request.method == 'POST':
        class_name = class_obj.name
        class_obj.delete()
        from django.contrib import messages
        messages.success(request, f'Class "{class_name}" has been deleted successfully!')
        # Redirect back to classes page
        from django.shortcuts import redirect
        return redirect('admin_unified_dashboard', 'classes')
    
    # Get teacher statistics for template compatibility
    teachers = User.objects.filter(role='teacher').select_related('faculty_profile').order_by('first_name', 'last_name')
    
    # Get current date and date ranges for monthly trends
    from django.utils import timezone
    from datetime import timedelta
    
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)
    
    # Monthly trends data
    monthly_trends = {
        'student_growth': {
            'this_month': StudentProfile.objects.filter(
                user__date_joined__gte=this_month_start
            ).count(),
            'last_month': StudentProfile.objects.filter(
                user__date_joined__gte=last_month_start,
                user__date_joined__lt=this_month_start
            ).count(),
        },
        'fee_collection': {
            'this_month': 0,  # Placeholder - no payment data in delete class context
            'last_month': 0,  # Placeholder - no payment data in delete class context
        },
    }
    
    return {
        'class_obj': class_obj,
        # Add teacher statistics for template compatibility
        'teachers': teachers,
        'total_teachers': teachers.count(),
        'active_teachers': teachers.filter(is_active=True).count(),
        # Add monthly trends for template compatibility
        'monthly_trends': monthly_trends,
    }

def get_admin_mark_attendance_context(request, user, admin_profile):
    """Get admin mark attendance page context"""
    from django import forms
    from .models import Attendance, Enrollment, CourseOffering, AttendanceSession
    from django.utils import timezone
    
    # Handle form submission - redirect immediately if successful
    if request.method == 'POST':
        from django.shortcuts import redirect
        
        class AttendanceMarkingForm(forms.Form):
            course_offering = forms.ModelChoiceField(
                queryset=CourseOffering.objects.all().select_related('course'),
                empty_label="Select Course"
            )
            date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
            
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                if not self.initial.get('date'):
                    self.initial['date'] = timezone.now().date()
        
        form = AttendanceMarkingForm(request.POST)
        if form.is_valid():
            course_offering = form.cleaned_data['course_offering']
            date = form.cleaned_data['date']
            
            # Get all enrollments for this course
            enrollments = Enrollment.objects.filter(course_offering=course_offering).select_related('student', 'student__user')
            
            # Create attendance records for each student
            attendance_records = []
            for enrollment in enrollments:
                attendance, created = Attendance.objects.get_or_create(
                    enrollment=enrollment,
                    date=date,
                    defaults={'status': 'P'}
                )
                attendance_records.append(attendance)
            
            from django.contrib import messages
            messages.success(request, f'Attendance marked for {len(attendance_records)} students in {course_offering.course.name}')
            
            # Return redirect directly - this will be handled in the main view
            return redirect('admin_unified_dashboard', 'attendance')
    
    # Create form for GET requests
    class AttendanceMarkingForm(forms.Form):
        course_offering = forms.ModelChoiceField(
            queryset=CourseOffering.objects.all().select_related('course'),
            empty_label="Select Course",
            widget=forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200'
            })
        )
        date = forms.DateField(
            widget=forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200'
            })
        )
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Set default date to today
            if not self.initial.get('date'):
                self.initial['date'] = timezone.now().date()
    
    form = AttendanceMarkingForm()
    
    # Get teacher statistics for template compatibility
    teachers = User.objects.filter(role='teacher').select_related('faculty_profile').order_by('first_name', 'last_name')
    
    # Get current date and date ranges for monthly trends
    from datetime import timedelta
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)
    
    # Monthly trends data
    monthly_trends = {
        'student_growth': {
            'this_month': StudentProfile.objects.filter(
                user__date_joined__gte=this_month_start
            ).count(),
            'last_month': StudentProfile.objects.filter(
                user__date_joined__gte=last_month_start,
                user__date_joined__lt=this_month_start
            ).count(),
        },
        'fee_collection': {
            'this_month': 0,  # Placeholder - no payment data in mark attendance context
            'last_month': 0,  # Placeholder - no payment data in mark attendance context
        },
    }
    
    return {
        'form': form,
        # Add teacher statistics for template compatibility
        'teachers': teachers,
        'total_teachers': teachers.count(),
        'active_teachers': teachers.filter(is_active=True).count(),
        # Add monthly trends for template compatibility
        'monthly_trends': monthly_trends,
    }

def get_admin_export_attendance_context(request, user, admin_profile):
    """Get admin export attendance page context"""
    from django import forms
    from .models import Attendance, CourseOffering
    from django.utils import timezone
    from datetime import timedelta
    import csv
    from django.http import HttpResponse
    
    # Debug: Print request method
    print(f"Export attendance request method: {request.method}")
    
    # Handle form submission - return response immediately if successful
    if request.method == 'POST':
        try:
            class AttendanceExportForm(forms.Form):
                course_offering = forms.ModelChoiceField(
                    queryset=CourseOffering.objects.all().select_related('course'),
                    empty_label="All Courses",
                    required=False
                )
                start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
                end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
                export_format = forms.ChoiceField(
                    choices=[
                        ('excel', 'Excel'),
                        ('pdf', 'PDF'),
                    ],
                    initial='excel'
                )
                
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    # Set default date range to last 30 days
                    if not self.initial.get('start_date'):
                        self.initial['start_date'] = (timezone.now().date() - timedelta(days=30))
                    if not self.initial.get('end_date'):
                        self.initial['end_date'] = timezone.now().date()
            
            form = AttendanceExportForm(request.POST)
            if form.is_valid():
                course_offering = form.cleaned_data['course_offering']
                start_date = form.cleaned_data['start_date']
                end_date = form.cleaned_data['end_date']
                export_format = form.cleaned_data['export_format']
                
                # Debug: Print form data
                print(f"Export form valid: course={course_offering}, start={start_date}, end={end_date}, format={export_format}")
                
                # Query attendance records
                attendance_records = Attendance.objects.filter(
                    Q(date__gte=start_date) & Q(date__lte=end_date)
                )
                if course_offering:
                    attendance_records = attendance_records.filter(
                        student__enrollment__course_offering=course_offering
                    )
                
                print(f"Found {len(attendance_records)} attendance records")
                
                # Create response based on format
                if export_format == 'excel':
                    # Create Excel-compatible CSV response
                    response = HttpResponse(content_type='application/vnd.ms-excel')
                    response['Content-Disposition'] = f'attachment; filename="attendance_report_{start_date}_to_{end_date}.xls"'
                    
                    writer = csv.writer(response)
                    writer.writerow(['Student Name', 'Roll Number', 'Course', 'Date', 'Status', 'Check In', 'Check Out', 'Notes'])
                    
                    for record in attendance_records:
                        writer.writerow([
                            record.student.user.get_full_name(),
                            record.student.roll_number or '',
                            record.student.enrollment.course_offering.course.name,
                            record.date,
                            record.get_status_display(),
                            record.check_in_time or '',
                            record.check_out_time or '',
                            record.notes or ''
                        ])
                    
                    print(f"Created Excel response with {len(attendance_records)} records")
                    return response
                    
                elif export_format == 'pdf':
                    # Create PDF response
                    from reportlab.lib.pagesizes import letter, A4
                    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
                    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                    from reportlab.lib import colors
                    from reportlab.lib.units import inch
                    
                    response = HttpResponse(content_type='application/pdf')
                    response['Content-Disposition'] = f'attachment; filename="attendance_report_{start_date}_to_{end_date}.pdf"'
                    
                    # Create PDF document
                    doc = SimpleDocTemplate(response, pagesize=A4)
                    styles = getSampleStyleSheet()
                    story = []
                    
                    # Title
                    title_style = ParagraphStyle(
                        'CustomTitle',
                        parent=styles['Heading1'],
                        fontSize=18,
                        spaceAfter=30,
                        alignment=1  # Center alignment
                    )
                    story.append(Paragraph("Attendance Report", title_style))
                    story.append(Paragraph(f"Period: {start_date} to {end_date}", styles['Normal']))
                    story.append(Spacer(1, 12))
                    
                    # Table data
                    table_data = [['Student Name', 'Roll Number', 'Course', 'Date', 'Status', 'Check In', 'Check Out']]
                    for record in attendance_records:
                        table_data.append([
                            record.enrollment.student.user.get_full_name(),
                            record.enrollment.student.roll_number or '',
                            record.enrollment.course_offering.course.name,
                            str(record.date),
                            record.get_status_display(),
                            str(record.check_in_time) if record.check_in_time else '',
                            str(record.check_out_time) if record.check_out_time else ''
                        ])
                    
                    # Create table
                    table = Table(table_data, repeatRows=1)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ]))
                    
                    story.append(table)
                    doc.build(story)
                    
                    print(f"Created PDF response with {len(attendance_records)} records")
                    return response
                
            else:
                print(f"Form invalid: {form.errors}")
                
        except Exception as e:
            print(f"Exception in export: {str(e)}")
            # If there's an error, create a simple error response
            from django.contrib import messages
            messages.error(request, f'Error exporting attendance: {str(e)}')
            # Return a simple redirect on error
            from django.shortcuts import redirect
            return redirect('admin_unified_dashboard', 'export-attendance')
    
    # Create form for GET requests
    class AttendanceExportForm(forms.Form):
        course_offering = forms.ModelChoiceField(
            queryset=CourseOffering.objects.all().select_related('course'),
            empty_label="All Courses",
            required=False,
            widget=forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200'
            })
        )
        start_date = forms.DateField(
            widget=forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200'
            })
        )
        end_date = forms.DateField(
            widget=forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200'
            })
        )
        export_format = forms.ChoiceField(
            choices=[
                ('excel', 'Excel'),
                ('pdf', 'PDF'),
            ],
            initial='excel',
            widget=forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200'
            })
        )
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Set default date range to last 30 days
            if not self.initial.get('start_date'):
                self.initial['start_date'] = (timezone.now().date() - timedelta(days=30))
            if not self.initial.get('end_date'):
                self.initial['end_date'] = timezone.now().date()
    
    form = AttendanceExportForm()
    
    # Get teacher statistics for template compatibility
    teachers = User.objects.filter(role='teacher').select_related('faculty_profile').order_by('first_name', 'last_name')
    
    # Get current date and date ranges for monthly trends
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)
    
    # Monthly trends data
    monthly_trends = {
        'student_growth': {
            'this_month': StudentProfile.objects.filter(
                user__date_joined__gte=this_month_start
            ).count(),
            'last_month': StudentProfile.objects.filter(
                user__date_joined__gte=last_month_start,
                user__date_joined__lt=this_month_start
            ).count(),
        },
        'fee_collection': {
            'this_month': 0,  # Placeholder - no payment data in export attendance context
            'last_month': 0,  # Placeholder - no payment data in export attendance context
        },
    }
    
    return {
        'form': form,
        # Add teacher statistics for template compatibility
        'teachers': teachers,
        'total_teachers': teachers.count(),
        'active_teachers': teachers.filter(is_active=True).count(),
        # Add monthly trends for template compatibility
        'monthly_trends': monthly_trends,
    }

def get_admin_attendance_context(user, admin_profile):
    """Get admin attendance page context"""
    attendance_records = Attendance.objects.all().select_related('enrollment', 'enrollment__student', 'enrollment__course_offering').order_by('-date')[:50]
    
    # Get teacher statistics for template compatibility
    teachers = User.objects.filter(role='teacher').select_related('faculty_profile').order_by('first_name', 'last_name')
    
    # Get current date and date ranges for monthly trends
    from django.utils import timezone
    from datetime import timedelta
    
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)
    
    # Monthly trends data
    monthly_trends = {
        'student_growth': {
            'this_month': StudentProfile.objects.filter(
                user__date_joined__gte=this_month_start
            ).count(),
            'last_month': StudentProfile.objects.filter(
                user__date_joined__gte=last_month_start,
                user__date_joined__lt=this_month_start
            ).count(),
        },
        'fee_collection': {
            'this_month': 0,  # Placeholder - no payment data in attendance context
            'last_month': 0,  # Placeholder - no payment data in attendance context
        },
    }
    
    return {
        'attendance_records': attendance_records,
        'total_records': attendance_records.count(),
        'today_records': Attendance.objects.filter(date=timezone.now().date()).count(),
        'present_count': Attendance.objects.filter(status='P').count(),
        'absent_count': Attendance.objects.filter(status='A').count(),
        'late_count': Attendance.objects.filter(status='L').count(),
        # Add teacher statistics for template compatibility
        'teachers': teachers,
        'total_teachers': teachers.count(),
        'active_teachers': teachers.filter(is_active=True).count(),
        # Add monthly trends for template compatibility
        'monthly_trends': monthly_trends,
    }

def get_admin_grading_context(user, admin_profile):
    """Get admin grading page context"""
    from django.db.models import Avg
    grades = Grade.objects.all().select_related('enrollment', 'enrollment__student', 'enrollment__course_offering').order_by('-awarded_on')[:50]
    
    # Get teacher statistics for template compatibility
    teachers = User.objects.filter(role='teacher').select_related('faculty_profile').order_by('first_name', 'last_name')
    
    # Get current date and date ranges for monthly trends
    from django.utils import timezone
    from datetime import timedelta
    
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)
    
    # Monthly trends data
    monthly_trends = {
        'student_growth': {
            'this_month': StudentProfile.objects.filter(
                user__date_joined__gte=this_month_start
            ).count(),
            'last_month': StudentProfile.objects.filter(
                user__date_joined__gte=last_month_start,
                user__date_joined__lt=this_month_start
            ).count(),
        },
        'fee_collection': {
            'this_month': 0,  # Placeholder - no payment data in grading context
            'last_month': 0,  # Placeholder - no payment data in grading context
        },
    }
    
    return {
        'grades': grades,
        'total_grades': grades.count(),
        'average_grade': grades.aggregate(avg=Avg('points'))['avg'] or 0,
        # Add teacher statistics for template compatibility
        'teachers': teachers,
        'total_teachers': teachers.count(),
        'active_teachers': teachers.filter(is_active=True).count(),
        # Add monthly trends for template compatibility
        'monthly_trends': monthly_trends,
    }

def get_admin_exams_context(user, admin_profile):
    """Get admin exams page context"""
    from .models import ExamSchedule, CourseOffering, StudentClass, Grade
    from django.db.models import Count, Avg
    from django.utils import timezone
    
    # Get all exam schedules with related data
    exam_schedules = ExamSchedule.objects.select_related(
        'course', 'course__department'
    ).order_by('-date')
    
    # Calculate statistics
    total_exams = exam_schedules.count()
    upcoming_exams = exam_schedules.filter(date__gt=timezone.now().date()).count()
    completed_exams = exam_schedules.filter(date__lt=timezone.now().date()).count()
    
    # Get recent grades for performance analysis
    recent_grades = Grade.objects.select_related(
        'enrollment', 'enrollment__student', 'enrollment__student__user',
        'enrollment__course_offering', 'enrollment__course_offering__course'
    ).order_by('-awarded_on')[:20]
    
    # Calculate average grade
    average_grade = Grade.objects.aggregate(avg=Avg('points'))['avg'] or 0
    
    # Get course offerings for dropdown
    course_offerings = CourseOffering.objects.select_related('course', 'faculty', 'faculty__user').order_by('course__name')
    
    # Get classes for dropdown
    classes = StudentClass.objects.all().order_by('form_level', 'name')
    
    # Exam statistics by type
    exam_stats = {
        'total': total_exams,
        'upcoming': upcoming_exams,
        'completed': completed_exams,
        'today': exam_schedules.filter(date=timezone.now().date()).count(),
    }
    
    # Performance statistics
    performance_stats = {
        'total_grades': Grade.objects.count(),
        'average_grade': average_grade,
        'recent_grades': recent_grades.count(),
        'unique_students': Grade.objects.values('enrollment__student').distinct().count(),
    }
    
    return {
        'exams': exam_schedules[:50],  # Limit to 50 for performance
        'recent_grades': recent_grades,
        'course_offerings': course_offerings,
        'classes': classes,
        'exam_stats': exam_stats,
        'performance_stats': performance_stats,
        'total_exams': total_exams,
        'upcoming_exams': upcoming_exams,
        # Add teacher statistics for template compatibility
        'teachers': User.objects.filter(role='teacher').select_related('faculty_profile').order_by('first_name', 'last_name'),
        'total_teachers': User.objects.filter(role='teacher').count(),
        'active_teachers': User.objects.filter(role='teacher', is_active=True).count(),
    }

@login_required
@user_passes_test(is_admin)
def admin_edit_exam(request, exam_id):
    """Admin edit exam page"""
    from .models import ExamSchedule, Course
    from django.shortcuts import get_object_or_404, redirect, render
    from django.contrib import messages
    
    exam = get_object_or_404(ExamSchedule, id=exam_id)
    
    if request.method == 'POST':
        form_data = request.POST
        exam.exam_type = form_data.get('exam_type', exam.exam_type)
        exam.date = form_data.get('date', exam.date)
        exam.start_time = form_data.get('start_time', exam.start_time)
        exam.end_time = form_data.get('end_time', exam.end_time)
        exam.venue = form_data.get('venue', exam.venue)
        
        try:
            exam.save()
            messages.success(request, f'Exam "{exam.course.name} {exam.exam_type}" has been updated successfully!')
            return redirect('admin_unified_dashboard', 'exams')
        except Exception as e:
            messages.error(request, f'Error updating exam: {str(e)}')
            return redirect('admin_unified_dashboard', 'edit-exam', exam_id=exam_id)
    
    context = {
        'exam': exam,
        'courses': Course.objects.all(),
        'exam_types': ExamSchedule.EXAM_TYPE_CHOICES,
    }
    
    return render(request, 'core/admin_parts/edit_exam.html', context)

@login_required
@user_passes_test(is_admin)
def admin_delete_exam(request, exam_id):
    """Admin delete exam"""
    from .models import ExamSchedule
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages
    
    exam = get_object_or_404(ExamSchedule, id=exam_id)
    
    if request.method == 'POST':
        exam_name = f"{exam.course.name} {exam.exam_type}"
        exam.delete()
        messages.success(request, f'Exam "{exam_name}" has been deleted successfully!')
        return redirect('admin_unified_dashboard', 'exams')
    
    # For GET request, just redirect back to exams page
    return redirect('admin_unified_dashboard', 'exams')

def get_admin_timetable_context(user, admin_profile):
    """Get admin timetable page context"""
    from .models import TimeTable, CourseOffering, StudentClass, FacultyProfile
    from django.db.models import Count
    
    # Get all timetable entries with related data
    timetable_entries = TimeTable.objects.select_related(
        'course_offering', 'course_offering__course', 'course_offering__faculty', 
        'course_offering__faculty__user', 'semester'
    ).order_by('day', 'start_time')
    
    # Get statistics
    total_entries = timetable_entries.count()
    entries_by_day = timetable_entries.values('day').annotate(count=Count('id')).order_by('day')
    
    # Get course offerings for dropdown
    course_offerings = CourseOffering.objects.select_related('course', 'faculty', 'faculty__user').order_by('course__name')
    
    # Get classes for dropdown
    classes = StudentClass.objects.all().order_by('form_level', 'name')
    
    # Get teachers for dropdown (as User objects for template compatibility)
    teachers = User.objects.filter(role='teacher').select_related('faculty_profile').order_by('first_name', 'last_name')
    
    # Schedule statistics
    schedule_stats = {
        'total_entries': total_entries,
        'unique_courses': timetable_entries.values('course_offering__course').distinct().count(),
        'unique_teachers': timetable_entries.values('course_offering__faculty').distinct().count(),
        'unique_rooms': timetable_entries.values('room').distinct().count(),
    }
    
    return {
        'timetable_entries': timetable_entries,
        'entries_by_day': entries_by_day,
        'course_offerings': course_offerings,
        'classes': classes,
        'teachers': teachers,
        'total_teachers': teachers.count(),
        'active_teachers': teachers.filter(is_active=True).count(),
        'schedule_stats': schedule_stats,
        'total_entries': total_entries,
    }

@login_required
@user_passes_test(is_admin)
def admin_create_announcement(request):
    """Create a new announcement"""
    from .forms import AnnouncementForm
    
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, user=request.user)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.created_by = request.user
            announcement.save()
            
            from django.contrib import messages
            messages.success(request, f'Announcement "{announcement.title}" has been created successfully!')
            return redirect('admin_unified_dashboard', page='announcements')
        else:
            from django.contrib import messages
            messages.error(request, 'Failed to create announcement. Please check the form for errors.')
    
    else:
        form = AnnouncementForm(user=request.user)
    
    # Get announcements context for template compatibility
    admin_profile = getattr(request.user, 'adminprofile', None)
    context = get_admin_announcements_context(request.user, admin_profile)
    context.update({
        'form': form,
        'page_title': 'Create Announcement'
    })
    
    return render(request, 'core/admin/create_announcement.html', context)

@login_required
@user_passes_test(is_admin)
def admin_edit_announcement(request, announcement_id):
    """Edit an existing announcement"""
    from .forms import AnnouncementForm
    from django.http import JsonResponse
    
    try:
        announcement = Announcement.objects.get(id=announcement_id)
    except Announcement.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Announcement not found.'}, status=404)
        from django.contrib import messages
        messages.error(request, 'Announcement not found.')
        return redirect('admin_unified_dashboard', page='announcements')
    
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=announcement)
        if form.is_valid():
            updated_announcement = form.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Announcement "{updated_announcement.title}" has been updated successfully!'
                })
            
            from django.contrib import messages
            messages.success(request, f'Announcement "{updated_announcement.title}" has been updated successfully!')
            return redirect('admin_unified_dashboard', page='announcements')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'Failed to update announcement. Please check the form for errors.'
                }, status=400)
            
            from django.contrib import messages
            messages.error(request, 'Failed to update announcement. Please check the form for errors.')
    
    elif request.method == 'GET':
        # Handle AJAX request for getting announcement data
        # More permissive AJAX detection for debugging
        is_ajax = (
            request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
            request.GET.get('ajax') == '1' or
            'application/json' in request.headers.get('Accept', '')
        )
        
        if is_ajax:
            try:
                return JsonResponse({
                    'id': announcement.id,
                    'title': announcement.title,
                    'message': announcement.message,
                    'target_audience': announcement.target_audience,
                    'target_class': announcement.target_class.id if announcement.target_class else None,
                    'expires_at': announcement.expires_at.strftime('%Y-%m-%dT%H:%M') if announcement.expires_at else '',
                    'is_active': announcement.is_active
                })
            except Exception as e:
                return JsonResponse({
                    'error': f'Server error: {str(e)}'
                }, status=500)
    
    # Get announcements context for the page (for regular form submission)
    admin_profile = getattr(request.user, 'adminprofile', None)
    context = get_admin_announcements_context(request.user, admin_profile)
    context.update({
        'form': AnnouncementForm(instance=announcement),
        'announcement': announcement,
        'page_title': 'Edit Announcement'
    })
    return render(request, 'core/admin_unified_dashboard.html', context)

@login_required
@user_passes_test(is_admin)
@csrf_exempt
def admin_delete_announcement(request, announcement_id):
    """Delete an announcement"""
    from django.http import JsonResponse
    
    # Only allow AJAX requests
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from django.contrib import messages
        messages.error(request, 'Invalid request method.')
        return redirect('admin_unified_dashboard', page='announcements')
    
    try:
        announcement = Announcement.objects.get(id=announcement_id)
        title = announcement.title
        announcement.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Announcement "{title}" has been deleted successfully!'
        })
    except Announcement.DoesNotExist:
        error_msg = 'Announcement not found.'
        return JsonResponse({'success': False, 'error': error_msg}, status=404)
    except Exception as e:
        error_msg = 'Failed to delete announcement.'
        return JsonResponse({'success': False, 'error': error_msg}, status=500)

def get_admin_announcements_context(user, admin_profile):
    """Get admin announcements page context"""
    from .forms import AnnouncementForm
    
    announcements = Announcement.objects.all().order_by('-created_at')
    classes = StudentClass.objects.all().order_by('name')
    
    return {
        'announcements': announcements[:20],
        'total_announcements': announcements.count(),
        'active_announcements': announcements.filter(is_active=True).count(),
        'pending_announcements': announcements.filter(is_active=False).count(),
        'classes': classes,  # Add classes for edit modal
        'form': AnnouncementForm(user=user),  # Add form for creation modal
        # Add teacher statistics for template compatibility
        'active_teachers': User.objects.filter(role='teacher', is_active=True).count(),
        'total_teachers': User.objects.filter(role='teacher').count(),
        'new_teachers_this_month': User.objects.filter(role='teacher', date_joined__month=timezone.now().month).count(),
    }

def get_admin_fees_context(user, admin_profile):
    """Get admin fees page context"""
    from .models import Fee, StudentProfile, Payment
    from django.db.models import Sum, Q
    from django.utils import timezone
    
    # Get all fee records with related student data
    fee_records = Fee.objects.select_related('student', 'student__user').order_by('-due_date')
    
    # Calculate statistics
    total_fees = fee_records.aggregate(total=Sum('amount'))['total'] or 0
    collected_amount = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0
    pending_fees = fee_records.filter(is_paid=False).aggregate(total=Sum('amount'))['total'] or 0
    
    # Get recent payments
    recent_payments = Payment.objects.select_related('fee', 'fee__student', 'fee__student__user').order_by('-payment_date')[:10]
    
    # Fee statistics by status
    fee_stats = {
        'total': fee_records.count(),
        'paid': fee_records.filter(is_paid=True).count(),
        'pending': fee_records.filter(is_paid=False).count(),
        'overdue': fee_records.filter(is_paid=False, due_date__lt=timezone.now().date()).count(),
    }
    
    return {
        'fee_records': fee_records[:50],  # Limit to 50 for performance
        'recent_payments': recent_payments,
        'total_fees': total_fees,
        'collected_amount': collected_amount,
        'pending_fees': pending_fees,
        'fee_stats': fee_stats,
        'total_students': StudentProfile.objects.count(),
        # Add teacher statistics for template compatibility
        'teachers': User.objects.filter(role='teacher').select_related('faculty_profile').order_by('first_name', 'last_name'),
        'total_teachers': User.objects.filter(role='teacher').count(),
        'active_teachers': User.objects.filter(role='teacher', is_active=True).count(),
    }

def get_admin_library_context(user, admin_profile):
    """Get admin library page context"""
    # Placeholder for library data - you may need to add Library models
    return {
        'library_items': [],
        'total_books': 0,
    }

def get_admin_settings_context(user, admin_profile):
    """Get admin settings page context"""
    from .models import SystemSetting, SchoolInfo, User, StudentProfile, FacultyProfile, HeadmasterProfile
    from django.db.models import Count
    
    # Get system settings
    system_settings = SystemSetting.objects.all().order_by('category', 'key')
    
    # Get school information
    try:
        school_info = SchoolInfo.objects.first()
    except:
        school_info = None
    
    # User statistics for settings
    user_stats = {
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'students': StudentProfile.objects.count(),
        'teachers': FacultyProfile.objects.count(),
        'headmasters': HeadmasterProfile.objects.count(),
        'admins': User.objects.filter(is_superuser=True).count(),
    }
    
    # Settings by category
    settings_by_category = {}
    for setting in system_settings:
        if setting.category not in settings_by_category:
            settings_by_category[setting.category] = []
        settings_by_category[setting.category].append(setting)
    
    # Recent user activity (last 30 days)
    from django.utils import timezone
    from datetime import timedelta
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    recent_users = User.objects.filter(
        date_joined__gte=thirty_days_ago
    ).order_by('-date_joined')[:10]
    
    return {
        'system_settings': system_settings,
        'school_info': school_info,
        'user_stats': user_stats,
        'settings_by_category': settings_by_category,
        'recent_users': recent_users,
        'total_settings': system_settings.count(),
    }

def get_admin_reports_context(user, admin_profile):
    """Get admin reports page context"""
    from .models import StudentProfile, Grade, Fee, Payment, ExamSchedule, CourseOffering, Attendance, FacultyProfile
    from django.db.models import Count, Avg, Sum, Q
    from django.utils import timezone
    from datetime import timedelta
    
    # Get current date and date ranges
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)
    
    # Teacher statistics
    total_teachers = FacultyProfile.objects.count()
    active_teachers = FacultyProfile.objects.filter(user__is_active=True).count()
    new_teachers_this_month = FacultyProfile.objects.filter(
        user__date_joined__gte=this_month_start
    ).count()
    
    # Student statistics
    total_students = StudentProfile.objects.count()
    active_students = StudentProfile.objects.filter(user__is_active=True).count()
    new_students_this_month = StudentProfile.objects.filter(
        user__date_joined__gte=this_month_start
    ).count()
    
    # Academic performance statistics
    grades_data = Grade.objects.aggregate(
        total_grades=Count('id'),
        avg_grade=Avg('points'),
        excellent_grades=Count('id', filter=Q(points__gte=4.0)),
        good_grades=Count('id', filter=Q(points__gte=3.0, points__lt=4.0)),
        passing_grades=Count('id', filter=Q(points__gte=2.0)),
    )
    
    # Fee statistics
    fee_data = Fee.objects.aggregate(
        total_fees=Sum('amount'),
        pending_fees=Sum('amount', filter=Q(is_paid=False)),
        collected_fees=Sum('amount', filter=Q(is_paid=True)),
    )
    
    payment_data = Payment.objects.filter(
        payment_date__gte=this_month_start
    ).aggregate(
        monthly_collected=Sum('amount'),
        payment_count=Count('id'),
    )
    
    # Attendance statistics
    attendance_data = Attendance.objects.aggregate(
        total_sessions=Count('id'),
        present_sessions=Count('id', filter=Q(status='P')),
        absent_sessions=Count('id', filter=Q(status='A')),
        late_sessions=Count('id', filter=Q(status='L')),
    )
    
    # Recent activity
    recent_grades = Grade.objects.select_related(
        'enrollment__student__user', 'enrollment__course_offering__course'
    ).order_by('-awarded_on')[:10]
    
    recent_payments = Payment.objects.select_related(
        'fee__student__user', 'fee'
    ).order_by('-payment_date')[:10]
    
    recent_exams = ExamSchedule.objects.select_related(
        'course', 'course__department'
    ).order_by('-date')[:10]
    
    # Course enrollment statistics
    course_stats = CourseOffering.objects.annotate(
        enrollment_count=Count('enrollments')
    ).order_by('-enrollment_count')[:10]
    
    # Monthly trends
    monthly_trends = {
        'student_growth': {
            'this_month': new_students_this_month,
            'last_month': StudentProfile.objects.filter(
                user__date_joined__gte=last_month_start,
                user__date_joined__lt=this_month_start
            ).count(),
        },
        'fee_collection': {
            'this_month': payment_data['monthly_collected'] or 0,
            'last_month': Payment.objects.filter(
                payment_date__gte=last_month_start,
                payment_date__lt=this_month_start
            ).aggregate(total=Sum('amount'))['total'] or 0,
        },
    }
    
    return {
        'total_students': total_students,
        'active_students': active_students,
        'new_students_this_month': new_students_this_month,
        'grades_data': grades_data,
        'fee_data': fee_data,
        'payment_data': payment_data,
        'attendance_data': attendance_data,
        'recent_grades': recent_grades,
        'recent_payments': recent_payments,
        'recent_exams': recent_exams,
        'course_stats': course_stats,
        'monthly_trends': monthly_trends,
        'total_teachers': total_teachers,
        'active_teachers': active_teachers,
        'new_teachers_this_month': new_teachers_this_month,
        'generated_reports': 0,  # Placeholder for generated reports count
    }

def get_admin_logs_context(user, admin_profile):
    """Get admin logs page context"""
    # Placeholder for logs data - you may need to add ActivityLog model
    return {
        'logs': [],
        'total_logs': 0,
    }

def get_admin_profile_context(user, admin_profile):
    return {'user_profile': user}

# Headmaster context functions
def get_headmaster_staff_context(user, headmaster_profile):
    return {'staff': []}

def get_headmaster_performance_context(user, headmaster_profile):
    return {'performance_data': []}

def get_headmaster_discipline_context(user, headmaster_profile):
    return {'discipline_cases': []}

def get_headmaster_reports_context(user, headmaster_profile):
    return {'reports': []}

def get_headmaster_attendance_context(user, headmaster_profile):
    return {'attendance_overview': []}

def get_headmaster_grading_context(user, headmaster_profile):
    return {'grading_analytics': []}

def get_headmaster_exams_context(user, headmaster_profile):
    return {'exam_results': []}

def get_headmaster_announcements_context(user, headmaster_profile):
    return {'announcements': []}

def get_headmaster_events_context(user, headmaster_profile):
    return {'events': []}

def get_headmaster_fees_context(user, headmaster_profile):
    return {'financial_overview': []}

def get_headmaster_messages_context(user, headmaster_profile):
    return {'messages': []}

def get_headmaster_profile_context(user, headmaster_profile):
    return {'user_profile': user}

# Notification count functions
def get_student_notification_counts(user):
    return {
        'announcements': 2,  # Placeholder
        'messages': 1,  # Placeholder
        'assignments': 3,  # Placeholder
    }

def get_admin_notification_counts(user):
    return {
        'announcements': 3,  # Placeholder
    'users': 0,  # Placeholder
    'students': 0,  # Placeholder
    'teachers': 0,  # Placeholder
    'discipline': 0,  # Placeholder
        'messages': 0,  # Placeholder
    }

def get_headmaster_notification_counts(user):
    return {
        'discipline': 2,  # Placeholder
        'messages': 1,  # Placeholder
        'announcements': 0,  # Placeholder
    }

def get_admin_edit_user_context(request, user, admin_profile):
    """Get admin edit user page context"""
    from django.shortcuts import get_object_or_404
    from .forms import UserUpdateForm
    from django.utils import timezone
    from datetime import timedelta
    
    # Get user ID from URL parameter
    user_id = request.GET.get('user_id')
    if not user_id:
        # Redirect to users page if no user ID provided
        from django.shortcuts import redirect
        return redirect('admin_unified_dashboard', 'users')
    
    # Get the user to edit
    edit_user = get_object_or_404(User, id=user_id)
    
    # Handle form submission
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=edit_user)
        if form.is_valid():
            form.save()
            from django.contrib import messages
            messages.success(request, f'User "{edit_user.get_full_name()}" has been updated successfully!')
            # Redirect back to users page
            from django.shortcuts import redirect
            return redirect('admin_unified_dashboard', 'users')
    else:
        form = UserUpdateForm(instance=edit_user)
    
    # Get teacher statistics for template compatibility
    teachers = User.objects.filter(role='teacher').select_related('faculty_profile').order_by('first_name', 'last_name')
    
    # Get current date and date ranges for monthly trends
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)
    
    # Monthly trends data
    monthly_trends = {
        'student_growth': {
            'this_month': StudentProfile.objects.filter(
                user__date_joined__gte=this_month_start
            ).count(),
            'last_month': StudentProfile.objects.filter(
                user__date_joined__gte=last_month_start,
                user__date_joined__lt=this_month_start
            ).count(),
        },
        'fee_collection': {
            'this_month': 0,  # Placeholder - no payment data in edit user context
            'last_month': 0,  # Placeholder - no payment data in edit user context
        },
    }
    
    return {
        'edit_user': edit_user,
        'form': form,
        'user_id': user_id,
        # Add teacher statistics for template compatibility
        'teachers': teachers,
        'total_teachers': teachers.count(),
        'active_teachers': teachers.filter(is_active=True).count(),
        # Add monthly trends for template compatibility
        'monthly_trends': monthly_trends,
    }

def get_admin_view_attendance_context(request, user, admin_profile):
    """Get admin view attendance page context"""
    from django import forms
    from .models import Attendance
    
    # Get attendance ID from query parameters
    attendance_id = request.GET.get('attendance_id')
    
    if not attendance_id:
        from django.contrib import messages
        messages.error(request, 'Attendance ID is required')
        from django.shortcuts import redirect
        return redirect('admin_unified_dashboard', 'attendance')
    
    try:
        attendance = Attendance.objects.get(id=attendance_id)
    except Attendance.DoesNotExist:
        from django.contrib import messages
        messages.error(request, 'Attendance record not found')
        from django.shortcuts import redirect
        return redirect('admin_unified_dashboard', 'attendance')
    
    # Get teacher statistics for template compatibility
    teachers = User.objects.filter(role='teacher').select_related('faculty_profile').order_by('first_name', 'last_name')
    
    # Get current date and date ranges for monthly trends
    from django.utils import timezone
    from datetime import timedelta
    
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)
    
    # Monthly trends data
    monthly_trends = {
        'student_growth': {
            'this_month': StudentProfile.objects.filter(
                user__date_joined__gte=this_month_start
            ).count(),
            'last_month': StudentProfile.objects.filter(
                user__date_joined__gte=last_month_start,
                user__date_joined__lt=this_month_start
            ).count(),
        },
        'fee_collection': {
            'this_month': 0,  # Placeholder - no payment data in view attendance context
            'last_month': 0,  # Placeholder - no payment data in view attendance context
        },
    }
    
    return {
        'attendance': attendance,
        'teachers': teachers,
        'total_teachers': teachers.count(),
        'active_teachers': teachers.filter(is_active=True).count(),
        'monthly_trends': monthly_trends,
    }

def get_admin_edit_attendance_context(request, user, admin_profile):
    """Get admin edit attendance page context"""
    from django import forms
    from .models import Attendance
    
    # Get attendance ID from query parameters
    attendance_id = request.GET.get('attendance_id')
    
    if not attendance_id:
        from django.contrib import messages
        messages.error(request, 'Attendance ID is required')
        from django.shortcuts import redirect
        return redirect('admin_unified_dashboard', 'attendance')
    
    try:
        attendance = Attendance.objects.get(id=attendance_id)
    except Attendance.DoesNotExist:
        from django.contrib import messages
        messages.error(request, 'Attendance record not found')
        from django.shortcuts import redirect
        return redirect('admin_unified_dashboard', 'attendance')
    
    # Create form for editing attendance
    class AttendanceEditForm(forms.Form):
        STATUS_CHOICES = [
            ('P', 'Present'),
            ('A', 'Absent'),
            ('L', 'Late'),
            ('E', 'Excused'),
        ]
        
        status = forms.ChoiceField(
            choices=STATUS_CHOICES,
            initial=attendance.status,
            widget=forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200'
            })
        )
        check_in_time = forms.TimeField(
            required=False,
            initial=attendance.check_in_time,
            widget=forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200'
            })
        )
        check_out_time = forms.TimeField(
            required=False,
            initial=attendance.check_out_time,
            widget=forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200'
            })
        )
        notes = forms.CharField(
            required=False,
            initial=attendance.notes,
            widget=forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200'
            })
        )
    
    # Handle form submission
    if request.method == 'POST':
        form = AttendanceEditForm(request.POST)
        if form.is_valid():
            attendance.status = form.cleaned_data['status']
            attendance.check_in_time = form.cleaned_data['check_in_time']
            attendance.check_out_time = form.cleaned_data['check_out_time']
            attendance.notes = form.cleaned_data['notes']
            attendance.save()
            
            from django.contrib import messages
            messages.success(request, f'Attendance record for {attendance.enrollment.student.user.get_full_name()} has been updated successfully!')
            
            from django.shortcuts import redirect
            return redirect('admin_unified_dashboard', 'attendance')
    else:
        form = AttendanceEditForm()
    
    # Get teacher statistics for template compatibility
    teachers = User.objects.filter(role='teacher').select_related('faculty_profile').order_by('first_name', 'last_name')
    
    # Get current date and date ranges for monthly trends
    from django.utils import timezone
    from datetime import timedelta
    
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)
    
    # Monthly trends data
    monthly_trends = {
        'student_growth': {
            'this_month': StudentProfile.objects.filter(
                user__date_joined__gte=this_month_start
            ).count(),
            'last_month': StudentProfile.objects.filter(
                user__date_joined__gte=last_month_start,
                user__date_joined__lt=this_month_start
            ).count(),
        },
        'fee_collection': {
            'this_month': 0,  # Placeholder - no payment data in edit attendance context
            'last_month': 0,  # Placeholder - no payment data in edit attendance context
        },
    }
    
    return {
        'attendance': attendance,
        'form': form,
        'teachers': teachers,
        'total_teachers': teachers.count(),
        'active_teachers': teachers.filter(is_active=True).count(),
        'monthly_trends': monthly_trends,
    }

def get_admin_delete_attendance_context(request, user, admin_profile):
    """Get admin delete attendance page context"""
    from django import forms
    from .models import Attendance
    
    # Get attendance ID from query parameters
    attendance_id = request.GET.get('attendance_id')
    
    if not attendance_id:
        from django.contrib import messages
        messages.error(request, 'Attendance ID is required')
        from django.shortcuts import redirect
        return redirect('admin_unified_dashboard', 'attendance')
    
    try:
        attendance = Attendance.objects.get(id=attendance_id)
    except Attendance.DoesNotExist:
        from django.contrib import messages
        messages.error(request, 'Attendance record not found')
        from django.shortcuts import redirect
        return redirect('admin_unified_dashboard', 'attendance')
    
    # Handle form submission
    if request.method == 'POST':
        confirm_text = request.POST.get('confirm_text', '').strip()
        
        if confirm_text != 'DELETE':
            from django.contrib import messages
            messages.error(request, 'Invalid confirmation. Please type DELETE exactly to confirm.')
            from django.shortcuts import redirect
            return redirect('admin_unified_dashboard', 'delete-attendance') + f'?attendance_id={attendance_id}'
        
        student_name = attendance.enrollment.student.user.get_full_name()
        attendance_date = attendance.date
        
        # Delete the attendance record
        attendance.delete()
        
        from django.contrib import messages
        messages.success(request, f'Attendance record for {student_name} on {attendance_date} has been deleted successfully!')
        
        from django.shortcuts import redirect
        return redirect('admin_unified_dashboard', 'attendance')
    
    # Get teacher statistics for template compatibility
    teachers = User.objects.filter(role='teacher').select_related('faculty_profile').order_by('first_name', 'last_name')
    
    # Get current date and date ranges for monthly trends
    from django.utils import timezone
    from datetime import timedelta
    
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)
    
    # Monthly trends data
    monthly_trends = {
        'student_growth': {
            'this_month': StudentProfile.objects.filter(
                user__date_joined__gte=this_month_start
            ).count(),
            'last_month': StudentProfile.objects.filter(
                user__date_joined__gte=last_month_start,
                user__date_joined__lt=this_month_start
            ).count(),
        },
        'fee_collection': {
            'this_month': 0,  # Placeholder - no payment data in delete attendance context
            'last_month': 0,  # Placeholder - no payment data in delete attendance context
        },
    }
    
    return {
        'attendance': attendance,
        'teachers': teachers,
        'total_teachers': teachers.count(),
        'active_teachers': teachers.filter(is_active=True).count(),
        'monthly_trends': monthly_trends,
    }

def get_admin_add_grade_context(request, user, admin_profile):
    """Get admin add grade page context"""
    from django import forms
    from .models import Grade, Enrollment, CourseOffering
    from django.utils import timezone
    from datetime import timedelta
    
    # Handle form submission
    if request.method == 'POST':
        class GradeForm(forms.Form):
            enrollment = forms.ModelChoiceField(
                queryset=Enrollment.objects.all().select_related('student__user', 'course_offering__course'),
                widget=forms.Select(attrs={
                    'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200'
                })
            )
            points = forms.IntegerField(
                min_value=0,
                max_value=100,
                widget=forms.NumberInput(attrs={
                    'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200'
                })
            )
            remarks = forms.CharField(
                required=False,
                widget=forms.Textarea(attrs={
                    'rows': 3,
                    'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200'
                })
            )
        
        form = GradeForm(request.POST)
        if form.is_valid():
            # Calculate letter grade based on points using model's grade scale
            points = form.cleaned_data['points']
            if points >= 90:
                letter_grade = 'A+'
            elif points >= 85:
                letter_grade = 'A'
            elif points >= 80:
                letter_grade = 'A-'
            elif points >= 75:
                letter_grade = 'B+'
            elif points >= 70:
                letter_grade = 'B'
            elif points >= 65:
                letter_grade = 'B-'
            elif points >= 60:
                letter_grade = 'C+'
            elif points >= 55:
                letter_grade = 'C'
            elif points >= 50:
                letter_grade = 'C-'
            elif points >= 45:
                letter_grade = 'D'
            else:
                letter_grade = 'F'
            
            enrollment = form.cleaned_data['enrollment']
            
            # Check if grade already exists for this enrollment
            try:
                grade = Grade.objects.get(enrollment=enrollment)
                # Update existing grade
                grade.points = points
                grade.grade = letter_grade
                grade.remarks = form.cleaned_data['remarks']
                grade.save()
                
                from django.contrib import messages
                messages.success(request, f'Grade updated to {grade.points} ({grade.grade}) for {grade.enrollment.student.user.get_full_name()} in {grade.enrollment.course_offering.course.name}!')
                
            except Grade.DoesNotExist:
                # Create new grade
                grade = Grade.objects.create(
                    enrollment=enrollment,
                    points=points,
                    grade=letter_grade,
                    remarks=form.cleaned_data['remarks'],
                    awarded_on=timezone.now().date()
                )
                
                from django.contrib import messages
                messages.success(request, f'Grade {grade.points} ({grade.grade}) has been successfully assigned to {grade.enrollment.student.user.get_full_name()} for {grade.enrollment.course_offering.course.name}!')
            
            from django.shortcuts import redirect
            return redirect('admin_unified_dashboard', 'grading')
    else:
        class GradeForm(forms.Form):
            enrollment = forms.ModelChoiceField(
                queryset=Enrollment.objects.all().select_related('student__user', 'course_offering__course'),
                widget=forms.Select(attrs={
                    'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200'
                })
            )
            points = forms.IntegerField(
                min_value=0,
                max_value=100,
                widget=forms.NumberInput(attrs={
                    'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200'
                })
            )
            remarks = forms.CharField(
                required=False,
                widget=forms.Textarea(attrs={
                    'rows': 3,
                    'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200'
                })
            )
        
        form = GradeForm()
    
    # Calculate statistics for template
    enrollments = Enrollment.objects.all().select_related('student', 'course_offering__course')
    total_students = enrollments.values('student').distinct().count()
    total_courses = enrollments.values('course_offering__course').distinct().count()
    total_enrollments = enrollments.count()
    
    # Get teacher statistics for template compatibility
    teachers = User.objects.filter(role='teacher').select_related('faculty_profile').order_by('first_name', 'last_name')
    
    # Get current date and date ranges for monthly trends
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)
    
    # Monthly trends data
    monthly_trends = {
        'student_growth': {
            'this_month': StudentProfile.objects.filter(
                user__date_joined__gte=this_month_start
            ).count(),
            'last_month': StudentProfile.objects.filter(
                user__date_joined__gte=last_month_start,
                user__date_joined__lt=this_month_start
            ).count(),
        },
        'fee_collection': {
            'this_month': 0,  # Placeholder - no payment data in add grade context
            'last_month': 0,  # Placeholder - no payment data in add grade context
        },
    }
    
    return {
        'form': form,
        'total_students': total_students,
        'total_courses': total_courses,
        'total_enrollments': total_enrollments,
        'teachers': teachers,
        'total_teachers': teachers.count(),
        'active_teachers': teachers.filter(is_active=True).count(),
        'monthly_trends': monthly_trends,
    }

def get_admin_edit_user_context(request, user, admin_profile):
    """Get admin edit user page context"""
    from django.shortcuts import get_object_or_404
    from django.http import HttpResponseRedirect
    from django.urls import reverse
    
    user_id = request.GET.get('user_id')
    if not user_id:
        from django.contrib import messages
        messages.error(request, "User ID not provided.")
        return {}
    
    try:
        edit_user = get_object_or_404(User, pk=user_id)
        
        if request.method == 'POST':
            # Use the same form as the separate edit view
            from .forms import UserUpdateForm
            form = UserUpdateForm(request.POST, instance=edit_user)
            
            if form.is_valid():
                form.save()
                from django.contrib import messages
                messages.success(request, f'User "{form.instance.get_full_name()}" has been updated successfully!')
                return HttpResponseRedirect(reverse('admin_unified_dashboard', page='users'))
            else:
                from django.contrib import messages
                messages.error(request, 'Failed to update user. Please check the form for errors.')
        
        # Use the same form as the separate edit view
        from .forms import UserUpdateForm
        form = UserUpdateForm(instance=edit_user)
        
        return {
            'edit_user': edit_user,
            'form': form,
            'user_role_display': 'Administrator',
            'current_page': 'edit-user',
            # Add teacher statistics for template compatibility
            'teachers': User.objects.filter(role='teacher'),
            'total_teachers': User.objects.filter(role='teacher').count(),
            'active_teachers': User.objects.filter(role='teacher', is_active=True).count(),
            # Add monthly trends for template compatibility with nested structure
            'monthly_trends': {
                'student_growth': {
                    'this_month': 0,  # Placeholder for current month
                    'last_month': 0,   # Placeholder for last month
                },
                'fee_collection': {
                    'this_month': 0,  # Placeholder for current month
                    'last_month': 0,   # Placeholder for last month
                },
                'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            },
        }
    except User.DoesNotExist:
        from django.contrib import messages
        messages.error(request, "User not found.")
        return {}

def get_admin_create_student_context(request, user, admin_profile):
    """Get admin create student page context"""
    from .forms_admin import PublicUserRegistrationForm
    
    if request.method == 'POST':
        # Use the same form as public registration
        from .forms_admin import PublicUserRegistrationForm
        form = PublicUserRegistrationForm(request.POST)
        
        if form.is_valid():
            # Save the user with student role
            new_user = form.save(commit=False)
            new_user.role = 'student'
            new_user.save()
            
            from django.contrib import messages
            messages.success(request, f'Student "{form.cleaned_data.get("first_name")} {form.cleaned_data.get("last_name")}" has been created successfully!')
            return HttpResponseRedirect(reverse('admin_unified_dashboard', page='users'))
        else:
            from django.contrib import messages
            messages.error(request, 'Failed to create student. Please check the form for errors.')
    
    # Use the same form as public registration for GET requests
    from .forms_admin import PublicUserRegistrationForm
    form = PublicUserRegistrationForm()
    
    return {
        'form': form,
        'user_role_display': 'Administrator',
        'current_page': 'create-student',
        # Add teacher statistics for template compatibility
        'teachers': User.objects.filter(role='teacher'),
        'total_teachers': User.objects.filter(role='teacher').count(),
        'active_teachers': User.objects.filter(role='teacher', is_active=True).count(),
        # Add monthly trends for template compatibility
        'monthly_trends': {
            'student_growth': {
                'this_month': 0,  # Placeholder for current month
                'last_month': 0,   # Placeholder for last month
            },
            'fee_collection': {
                'this_month': 0,  # Placeholder for current month
                'last_month': 0,   # Placeholder for last month
            },
            'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']  # Month labels
        },
    }

def get_admin_delete_user_context(request, user, admin_profile):
    """Get admin delete user page context"""
    from django.shortcuts import get_object_or_404
    from django.http import HttpResponseRedirect
    from django.urls import reverse
    from django.contrib import messages
    
    user_id = request.GET.get('user_id')
    if not user_id:
        messages.error(request, "User ID not provided.")
        return {}
    
    try:
        delete_user = get_object_or_404(User, pk=user_id)
        
        if request.method == 'POST':
            # Prevent deletion of self
            if delete_user == request.user:
                messages.error(request, "You cannot delete your own account.")
                return {'delete_user': delete_user}
            
            # Check if user has permission
            if not request.user.is_staff:
                messages.error(request, "You don't have permission to delete users.")
                return {'delete_user': delete_user}
            
            try:
                user_name = delete_user.get_full_name() or delete_user.username
                delete_user.delete()
                messages.success(request, f'User "{user_name}" has been deleted successfully.')
                return HttpResponseRedirect(reverse('admin_unified_dashboard', page='users'))
            except Exception as e:
                messages.error(request, f'Error deleting user: {str(e)}')
                return {'deleted': False, 'error': str(e)}
        
        return {
            'delete_user': delete_user,
            'user_role_display': 'Administrator',
            'current_page': 'delete-user',
            # Add teacher statistics for template compatibility
            'teachers': User.objects.filter(role='teacher'),
            'total_teachers': User.objects.filter(role='teacher').count(),
            'active_teachers': User.objects.filter(role='teacher', is_active=True).count(),
            # Add monthly trends for template compatibility with nested structure
            'monthly_trends': {
                'student_growth': {
                    'this_month': 0,  # Placeholder for current month
                    'last_month': 0,   # Placeholder for last month
                },
                'fee_collection': {
                    'this_month': 0,  # Placeholder for current month
                    'last_month': 0,   # Placeholder for last month
                },
                'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            },
        }
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return {}

def get_admin_create_user_context(request, user, admin_profile):
    """Get admin create user page context with dynamic role selection"""
    from django.contrib import messages
    from django.http import HttpResponseRedirect
    from django.urls import reverse
    from .forms_admin import (
        AdminCreateStudentForm, 
        AdminCreateTeacherForm, 
        AdminCreateHeadmasterForm
    )
    from datetime import datetime, timedelta
    
    # Get selected role from URL parameter or POST data
    selected_role = request.POST.get('role') or request.GET.get('role')
    
    # Calculate monthly trends data (same as other admin pages)
    this_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_start = this_month_start - timedelta(days=32)
    last_month_start = last_month_start.replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)
    
    # Monthly trends data
    monthly_trends = {
        'student_growth': {
            'this_month': StudentProfile.objects.filter(
                user__date_joined__gte=this_month_start
            ).count(),
            'last_month': StudentProfile.objects.filter(
                user__date_joined__gte=last_month_start,
                user__date_joined__lt=last_month_end
            ).count()
        },
        'fee_collection': {
            'this_month': 0,  # Placeholder - no fee data for create user page
            'last_month': 0   # Placeholder - no fee data for create user page
        }
    }
    
    if request.method == 'POST':
        if not selected_role:
            from django.contrib import messages
            messages.error(request, 'Please select a user role.')
            return {
                'selected_role': selected_role,
                'student_form': AdminCreateStudentForm(),
                'teacher_form': AdminCreateTeacherForm(),
                'headmaster_form': AdminCreateHeadmasterForm(),
                'user_role_display': 'Administrator',
                'current_page': 'create-user',
                # Add teacher statistics for template compatibility
                'teachers': User.objects.filter(role='teacher'),
                'total_teachers': User.objects.filter(role='teacher').count(),
                'active_teachers': User.objects.filter(role='teacher', is_active=True).count(),
                # Add monthly trends for template compatibility
                'monthly_trends': {
                    'student_growth': {
                        'this_month': 0,
                        'last_month': 0,
                    },
                    'fee_collection': {
                        'this_month': 0,
                        'last_month': 0,
                    },
                    'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                }
            }
        
        if selected_role == 'student':
            form = AdminCreateStudentForm(request.POST)
        elif selected_role == 'teacher':
            form = AdminCreateTeacherForm(request.POST)
        elif selected_role == 'headmaster':
            form = AdminCreateHeadmasterForm(request.POST)
        else:
            from django.contrib import messages
            messages.error(request, 'Invalid user role selected.')
            return {
                'selected_role': selected_role,
                'student_form': AdminCreateStudentForm(),
                'teacher_form': AdminCreateTeacherForm(),
                'headmaster_form': AdminCreateHeadmasterForm(),
                'user_role_display': 'Administrator',
                'current_page': 'create-user',
                'monthly_trends': monthly_trends,  # Add monthly trends for template compatibility
                # Add teacher statistics for template compatibility
                'teachers': User.objects.filter(role='teacher'),
                'total_teachers': User.objects.filter(role='teacher').count(),
                'active_teachers': User.objects.filter(role='teacher', is_active=True).count(),
            }
        
        if form.is_valid():
            # Save the user with the selected role
            new_user = form.save(commit=False)
            if selected_role:
                new_user.role = selected_role
            new_user.save()
            
            from django.contrib import messages
            role_display = selected_role.title() if selected_role else 'User'
            messages.success(request, f'{role_display} "{new_user.get_full_name()}" has been created successfully!')
            return HttpResponseRedirect(reverse('admin_unified_dashboard', page='users'))
        else:
            from django.contrib import messages
            role_display = selected_role.title() if selected_role else 'User'
            messages.error(request, f'Failed to create {role_display}. Please check the form for errors.')
            return {
                'selected_role': selected_role,
                'student_form': AdminCreateStudentForm() if selected_role != 'student' else form,
                'teacher_form': AdminCreateTeacherForm() if selected_role != 'teacher' else form,
                'headmaster_form': AdminCreateHeadmasterForm() if selected_role != 'headmaster' else form,
                'user_role_display': 'Administrator',
                'current_page': 'create-user',
                'monthly_trends': monthly_trends,  # Add monthly trends for template compatibility
                # Add teacher statistics for template compatibility
                'teachers': User.objects.filter(role='teacher'),
                'total_teachers': User.objects.filter(role='teacher').count(),
                'active_teachers': User.objects.filter(role='teacher', is_active=True).count(),
            }
    
    # GET request - show all forms or specific form if role is selected
    if selected_role:
        return {
            'selected_role': selected_role,
            'student_form': AdminCreateStudentForm(),
            'teacher_form': AdminCreateTeacherForm(),
            'headmaster_form': AdminCreateHeadmasterForm(),
            'user_role_display': 'Administrator',
            'current_page': 'create-user',
            'monthly_trends': monthly_trends,  # Add monthly trends for template compatibility
            # Add teacher statistics for template compatibility
            'teachers': User.objects.filter(role='teacher'),
            'total_teachers': User.objects.filter(role='teacher').count(),
            'active_teachers': User.objects.filter(role='teacher', is_active=True).count(),
        }
    else:
        return {
            'selected_role': None,
            'student_form': AdminCreateStudentForm(),
            'teacher_form': AdminCreateTeacherForm(),
            'headmaster_form': AdminCreateHeadmasterForm(),
            'user_role_display': 'Administrator',
            'current_page': 'create-user',
            'monthly_trends': monthly_trends,  # Add monthly trends for template compatibility
            # Add teacher statistics for template compatibility
            'teachers': User.objects.filter(role='teacher'),
            'total_teachers': User.objects.filter(role='teacher').count(),
            'active_teachers': User.objects.filter(role='teacher', is_active=True).count(),
        }
