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
        context.update(get_admin_add_subject_context(request, user, admin_profile))
    elif page == 'add-class':
        context.update(get_admin_add_class_context(request, user, admin_profile))
    elif page == 'edit-class':
        context.update(get_admin_edit_class_context(request, user, admin_profile))
    elif page == 'delete-class':
        context.update(get_admin_delete_class_context(request, user, admin_profile))
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
    elif page == 'users':
        context.update(get_admin_users_context(user, admin_profile))
    elif page == 'edit-user':
        context.update(get_admin_edit_user_context(request, user, admin_profile))
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
            'this_month': 0,  # Placeholder - no payment data in overview
            'last_month': 0,  # Placeholder - no payment data in overview
        },
    }
    
    context = {
        'total_users': User.objects.count(),
        'total_students': User.objects.filter(role='student').count(),
        'total_teachers': User.objects.filter(role='teacher').count(),
        'total_courses': CourseOffering.objects.count(),
        'pending_announcements': 3,  # Placeholder
        'monthly_trends': monthly_trends,  # Add monthly trends for reports template
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
    # Placeholder for message data - you may need to add Message model
    return {
        'messages': [],
        'unread_messages': 1,  # Calculate from actual data
        'sent_messages': 0,
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
    grades = Grade.objects.all().select_related('enrollment', 'enrollment__student', 'enrollment__course_offering').order_by('-awarded_on')[:50]
    
    return {
        'grades': grades,
        'total_grades': grades.count(),
        'average_grade': grades.aggregate(avg=Avg('points'))['avg'] or 0,
    }

def get_admin_exams_context(user, admin_profile):
    """Get admin exams page context"""
    from .models import Exam, CourseOffering, StudentClass, Grade
    from django.db.models import Count, Avg
    from django.utils import timezone
    
    # Get all exams with related data
    exams = Exam.objects.select_related(
        'course_offering', 'course_offering__course', 'course_offering__faculty', 
        'course_offering__faculty__user', 'student_class'
    ).order_by('-exam_date')
    
    # Calculate statistics
    total_exams = exams.count()
    upcoming_exams = exams.filter(exam_date__gt=timezone.now().date()).count()
    completed_exams = exams.filter(exam_date__lt=timezone.now().date()).count()
    
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
        'today': exams.filter(exam_date=timezone.now().date()).count(),
    }
    
    # Performance statistics
    performance_stats = {
        'total_grades': Grade.objects.count(),
        'average_grade': average_grade,
        'recent_grades': recent_grades.count(),
        'unique_students': Grade.objects.values('enrollment__student').distinct().count(),
    }
    
    return {
        'exams': exams[:50],  # Limit to 50 for performance
        'recent_grades': recent_grades,
        'course_offerings': course_offerings,
        'classes': classes,
        'exam_stats': exam_stats,
        'performance_stats': performance_stats,
        'total_exams': total_exams,
        'upcoming_exams': upcoming_exams,
    }

def get_admin_timetable_context(user, admin_profile):
    """Get admin timetable page context"""
    from .models import TimetableEntry, CourseOffering, StudentClass, FacultyProfile
    from django.db.models import Count
    
    # Get all timetable entries with related data
    timetable_entries = TimetableEntry.objects.select_related(
        'course_offering', 'course_offering__course', 'course_offering__faculty', 
        'course_offering__faculty__user', 'student_class'
    ).order_by('day', 'start_time')
    
    # Get statistics
    total_entries = timetable_entries.count()
    entries_by_day = timetable_entries.values('day').annotate(count=Count('id')).order_by('day')
    
    # Get course offerings for dropdown
    course_offerings = CourseOffering.objects.select_related('course', 'faculty', 'faculty__user').order_by('course__name')
    
    # Get classes for dropdown
    classes = StudentClass.objects.all().order_by('form_level', 'name')
    
    # Get teachers for dropdown
    teachers = FacultyProfile.objects.select_related('user').order_by('user__first_name', 'user__last_name')
    
    # Schedule statistics
    schedule_stats = {
        'total_entries': total_entries,
        'unique_courses': timetable_entries.values('course_offering__course').distinct().count(),
        'unique_teachers': timetable_entries.values('course_offering__faculty').distinct().count(),
        'unique_classes': timetable_entries.values('student_class').distinct().count(),
    }
    
    return {
        'timetable_entries': timetable_entries,
        'entries_by_day': entries_by_day,
        'course_offerings': course_offerings,
        'classes': classes,
        'teachers': teachers,
        'schedule_stats': schedule_stats,
        'total_entries': total_entries,
    }

def get_admin_announcements_context(user, admin_profile):
    """Get admin announcements page context"""
    announcements = Announcement.objects.all().order_by('-created_at')
    
    return {
        'announcements': announcements[:20],
        'total_announcements': announcements.count(),
        'active_announcements': announcements.filter(is_active=True).count(),
        'pending_announcements': announcements.filter(is_active=False).count(),
    }

def get_admin_fees_context(user, admin_profile):
    """Get admin fees page context"""
    from .models import Fee, StudentProfile, Payment
    from django.db.models import Sum, Q
    
    # Get all fee records with related student data
    fee_records = Fee.objects.select_related('student', 'student__user').order_by('-due_date')
    
    # Calculate statistics
    total_fees = fee_records.aggregate(total=Sum('amount'))['total'] or 0
    collected_amount = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0
    pending_fees = fee_records.filter(status='pending').aggregate(total=Sum('amount'))['total'] or 0
    
    # Get recent payments
    recent_payments = Payment.objects.select_related('fee', 'fee__student', 'fee__student__user').order_by('-payment_date')[:10]
    
    # Fee statistics by status
    fee_stats = {
        'total': fee_records.count(),
        'paid': fee_records.filter(status='paid').count(),
        'pending': fee_records.filter(status='pending').count(),
        'overdue': fee_records.filter(status='overdue').count(),
    }
    
    return {
        'fee_records': fee_records[:50],  # Limit to 50 for performance
        'recent_payments': recent_payments,
        'total_fees': total_fees,
        'collected_amount': collected_amount,
        'pending_fees': pending_fees,
        'fee_stats': fee_stats,
        'total_students': StudentProfile.objects.count(),
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
    from .models import StudentProfile, Grade, Fee, Payment, Exam, CourseOffering, Attendance
    from django.db.models import Count, Avg, Sum, Q
    from django.utils import timezone
    from datetime import timedelta
    
    # Get current date and date ranges
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)
    
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
        pending_fees=Sum('amount', filter=Q(status='pending')),
        collected_fees=Sum('amount', filter=Q(status='paid')),
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
    
    recent_exams = Exam.objects.select_related(
        'course_offering__course', 'student_class'
    ).order_by('-exam_date')[:10]
    
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
