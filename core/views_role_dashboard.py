from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.utils import timezone
from django.db.models import Q, Count, Avg, Sum
from django.contrib import messages
from django.core.paginator import Paginator

from .models import (
    User, StudentProfile, FacultyProfile, Announcement, 
    Attendance, StudentClass, CourseOffering, Enrollment, Grade,
    AdminProfile, HeadmasterProfile
)
from .utils import is_student, is_faculty, is_admin, is_headmaster
from .forms import AnnouncementForm, AttendanceForm
import json

@login_required
def student_unified_dashboard(request, page='overview'):
    """
    Student unified dashboard view that handles all student dashboard pages
    """
    user = request.user
    
    # Get student profile
    try:
        student_profile = user.student_profile
    except StudentProfile.DoesNotExist:
        student_profile = None
    
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
    
    context = {
        'user': user,
        'admin_profile': admin_profile,
        'current_page': page,
        'page_title': get_admin_page_title(page),
        'user_role_display': 'Administrator',
    }
    
    # Add page-specific context
    if page == 'overview':
        context.update(get_admin_overview_context(user, admin_profile))
    elif page == 'users':
        context.update(get_admin_users_context(user, admin_profile))
    elif page == 'students':
        context.update(get_admin_students_context(user, admin_profile))
    elif page == 'teachers':
        context.update(get_admin_teachers_context(user, admin_profile))
    elif page == 'courses':
        context.update(get_admin_courses_context(user, admin_profile))
    elif page == 'classes':
        context.update(get_admin_classes_context(user, admin_profile))
    elif page == 'subjects':
        context.update(get_admin_subjects_context(user, admin_profile))
    elif page == 'attendance':
        context.update(get_admin_attendance_context(user, admin_profile))
    elif page == 'grading':
        context.update(get_admin_grading_context(user, admin_profile))
    elif page == 'exams':
        context.update(get_admin_exams_context(user, admin_profile))
    elif page == 'announcements':
        context.update(get_admin_announcements_context(user, admin_profile))
    elif page == 'fees':
        context.update(get_admin_fees_context(user, admin_profile))
    elif page == 'reports':
        context.update(get_admin_reports_context(user, admin_profile))
    elif page == 'settings':
        context.update(get_admin_settings_context(user, admin_profile))
    elif page == 'logs':
        context.update(get_admin_logs_context(user, admin_profile))
    elif page == 'profile':
        context.update(get_admin_profile_context(user, admin_profile))
    
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
        'students': 'Students',
        'teachers': 'Teachers',
        'courses': 'Courses',
        'classes': 'Classes',
        'subjects': 'Subjects',
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
    context = {
        'total_users': User.objects.count(),
        'total_students': User.objects.filter(role='student').count(),
        'total_teachers': User.objects.filter(role='teacher').count(),
        'total_courses': CourseOffering.objects.count(),
        'pending_announcements': 3,  # Placeholder
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

# Placeholder context functions for other pages
def get_student_attendance_context(user, student_profile):
    return {'attendance_records': []}

def get_student_announcements_context(user, student_profile):
    return {'announcements': []}

def get_student_courses_context(user, student_profile):
    return {'courses': []}

def get_student_results_context(user, student_profile):
    return {'results': []}

def get_student_timetable_context(user, student_profile):
    return {'schedule': []}

def get_student_assignments_context(user, student_profile):
    return {'assignments': []}

def get_student_exams_context(user, student_profile):
    return {'exams': []}

def get_student_fees_context(user, student_profile):
    return {'fee_records': []}

def get_student_library_context(user, student_profile):
    return {'borrowed_books': []}

def get_student_messages_context(user, student_profile):
    return {'messages': []}

def get_student_profile_context(user, student_profile):
    return {'user_profile': user}

# Admin context functions
def get_admin_users_context(user, admin_profile):
    return {'users': []}

def get_admin_students_context(user, admin_profile):
    return {'students': []}

def get_admin_teachers_context(user, admin_profile):
    return {'teachers': []}

def get_admin_courses_context(user, admin_profile):
    return {'courses': []}

def get_admin_classes_context(user, admin_profile):
    return {'classes': []}

def get_admin_subjects_context(user, admin_profile):
    return {'subjects': []}

def get_admin_attendance_context(user, admin_profile):
    return {'attendance_data': []}

def get_admin_grading_context(user, admin_profile):
    return {'grading_data': []}

def get_admin_exams_context(user, admin_profile):
    return {'exam_data': []}

def get_admin_announcements_context(user, admin_profile):
    return {'announcements': []}

def get_admin_fees_context(user, admin_profile):
    return {'fee_data': []}

def get_admin_reports_context(user, admin_profile):
    return {'reports': []}

def get_admin_settings_context(user, admin_profile):
    return {'settings': {}}

def get_admin_logs_context(user, admin_profile):
    return {'logs': []}

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
