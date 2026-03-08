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

def get_admin_users_context(user, admin_profile):
    """Get admin users page context"""
    users = User.objects.all().order_by('-date_joined')[:20]
    return {
        'users': users,
        'total_users': users.count(),
        'students_count': User.objects.filter(role='student').count(),
        'teachers_count': User.objects.filter(role='teacher').count(),
        'admins_count': User.objects.filter(role='admin').count(),
    }

def get_admin_students_context(user, admin_profile):
    """Get admin students page context"""
    from .models import Department
    from django.db.models import Q
    
    # Get all students with related data
    students = StudentProfile.objects.select_related(
        'user', 'department'
    ).prefetch_related(
        'enrollments__course_offering__course',
        'enrollments__attendances'
    ).order_by('-date_enrolled')
    
    # Get departments for filter
    departments = Department.objects.all()
    
    # Apply filters from request
    search_query = user.request.GET.get('search', '')
    department_filter = user.request.GET.get('department', '')
    status_filter = user.request.GET.get('status', '')
    
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
        'new_students_this_month': students.filter(
            date_enrolled__month=timezone.now().month,
            date_enrolled__year=timezone.now().year
        ).count(),
        'search_query': search_query,
        'department_filter': department_filter,
        'status_filter': status_filter,
    }

def get_admin_teachers_context(user, admin_profile):
    """Get admin teachers page context"""
    teachers = User.objects.filter(role='teacher').select_related('faculty_profile').order_by('first_name', 'last_name')
    return {
        'teachers': teachers,
        'total_teachers': teachers.count(),
        'active_teachers': teachers.filter(is_active=True).count(),
    }

def get_admin_courses_context(user, admin_profile):
    """Get admin courses page context"""
    courses = CourseOffering.objects.all().select_related('course', 'faculty').order_by('course__name')
    return {
        'courses': courses,
        'total_courses': courses.count(),
    }

def get_admin_classes_context(user, admin_profile):
    """Get admin classes page context"""
    classes = StudentClass.objects.all().order_by('form_level', 'name')
    return {
        'classes': classes,
        'total_classes': classes.count(),
        'active_classes': classes.filter(is_active=True).count(),
        'total_students': classes.aggregate(total=Sum('current_students'))['total'] or 0,
    }

def get_admin_subjects_context(user, admin_profile):
    """Get admin subjects page context"""
    subjects = CourseOffering.objects.values('course__name', 'course__code').distinct().order_by('course__name')
    return {
        'subjects': subjects,
        'total_subjects': subjects.count(),
    }

def get_admin_attendance_context(user, admin_profile):
    """Get admin attendance page context"""
    attendance_records = Attendance.objects.all().select_related('enrollment', 'enrollment__student', 'enrollment__course_offering').order_by('-date')[:50]
    
    return {
        'attendance_records': attendance_records,
        'total_records': attendance_records.count(),
        'today_records': Attendance.objects.filter(date=timezone.now().date()).count(),
        'present_count': Attendance.objects.filter(status='P').count(),
        'absent_count': Attendance.objects.filter(status='A').count(),
        'late_count': Attendance.objects.filter(status='L').count(),
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
    # Placeholder for exam data - you may need to add Exam model
    return {
        'exams': [],
        'total_exams': 0,
        'upcoming_exams': 0,
    }

def get_admin_timetable_context(user, admin_profile):
    """Get admin timetable page context"""
    # Placeholder for timetable data
    return {
        'timetable_entries': [],
        'total_entries': 0,
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
    # Placeholder for fees data - you may need to add Fee model
    return {
        'fee_records': [],
        'total_collected': 0,
        'pending_fees': 0,
    }

def get_admin_library_context(user, admin_profile):
    """Get admin library page context"""
    # Placeholder for library data - you may need to add Library models
    return {
        'library_items': [],
        'total_books': 0,
        'borrowed_books': 0,
    }

def get_admin_reports_context(user, admin_profile):
    """Get admin reports page context"""
    # Placeholder for reports data
    return {
        'reports': [],
        'generated_reports': 0,
    }

def get_admin_settings_context(user, admin_profile):
    """Get admin settings page context"""
    # Placeholder for settings data
    return {
        'settings': {},
        'system_settings': {},
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
