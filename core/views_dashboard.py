from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.utils import timezone
from django.db.models import Q, Count, Avg
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.contrib import messages
from .utils import is_student, is_faculty, is_admin
from .forms import AnnouncementForm, AttendanceForm
from .models import (
    User, StudentProfile, FacultyProfile, Announcement, 
    Attendance, StudentClass, CourseOffering, Enrollment, Grade, Message
)
import json

@login_required
def unified_dashboard(request, page='overview'):
    """
    Unified dashboard view that handles all dashboard pages
    """
    user = request.user
    # Get unread messages count for all pages
    try:
        from .models import Message
        unread_messages = Message.objects.filter(recipient=user, is_read=False).count()
    except:
        unread_messages = 0
    
    context = {
        'user': user,
        'current_page': page,
        'page_title': get_page_title(page),
        'user_role_display': get_user_role_display(user),
        'unread_messages': unread_messages,
    }
    
    # Add page-specific context
    if page == 'overview':
        context.update(get_overview_context(user))
    elif page == 'attendance':
        context.update(get_attendance_context(user))
    elif page == 'announcements':
        context.update(get_announcements_context(user))
    elif page == 'messages':
        context.update(get_messages_context(user))
    elif page == 'courses':
        context.update(get_courses_context(user))
    elif page == 'grading':
        context.update(get_grading_context(user))
    elif page == 'timetable':
        context.update(get_timetable_context(user))
    elif page == 'fees':
        context.update(get_fees_context(user))
    elif page == 'library':
        context.update(get_library_context(user))
    elif page == 'profile':
        context.update(get_profile_context(user))
    
    return render(request, 'core/unified_dashboard.html', context)

@login_required
def load_dashboard_page(request, page):
    """
    AJAX endpoint to load dashboard page content
    """
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request'})
    
    user = request.user
    context = {
        'user': user,
        'current_page': page,
    }
    
    try:
        # Get page-specific content
        if page == 'overview':
            context.update(get_overview_context(user))
            template = 'core/dashboard_parts/overview.html'
        elif page == 'attendance':
            context.update(get_attendance_context(user))
            template = 'core/dashboard_parts/attendance.html'
        elif page == 'announcements':
            context.update(get_announcements_context(user))
            template = 'core/dashboard_parts/announcements.html'
        elif page == 'messages':
            context.update(get_messages_context(user))
            template = 'core/dashboard_parts/messages.html'
        elif page == 'courses':
            context.update(get_courses_context(user))
            template = 'core/dashboard_parts/courses.html'
        elif page == 'grading':
            context.update(get_grading_context(user))
            template = 'core/dashboard_parts/grading.html'
        elif page == 'timetable':
            context.update(get_timetable_context(user))
            template = 'core/dashboard_parts/timetable.html'
        elif page == 'fees':
            context.update(get_fees_context(user))
            template = 'core/dashboard_parts/fees.html'
        elif page == 'library':
            context.update(get_library_context(user))
            template = 'core/dashboard_parts/library.html'
        elif page == 'profile':
            context.update(get_profile_context(user))
            template = 'core/dashboard_parts/profile.html'
        else:
            return JsonResponse({'success': False, 'error': 'Page not found'})
        
        # Render template content
        content = render(request, template, context).content.decode('utf-8')
        
        return JsonResponse({
            'success': True,
            'content': content,
            'notifications': get_notification_counts(user)
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def get_notifications(request):
    """
    AJAX endpoint to get notification counts
    """
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request'})
    
    try:
        notifications = get_notification_counts(request.user)
        return JsonResponse({'success': True, 'notifications': notifications})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# Helper functions
def get_page_title(page):
    titles = {
        'overview': 'Dashboard',
        'attendance': 'Attendance',
        'announcements': 'Announcements',
        'messages': 'Messages',
        'courses': 'My Classes',
        'grading': 'Grading',
        'timetable': 'My Schedule',
        'fees': 'Fees',
        'library': 'Library',
        'profile': 'Profile Settings'
    }
    return titles.get(page, 'Dashboard')

def get_user_role_display(user):
    if hasattr(user, 'role'):
        role_display = {
            'student': 'Student',
            'teacher': 'Teacher',
            'admin': 'Administrator',
            'normal': 'User'
        }
        return role_display.get(user.role, 'User')
    return 'User'

def get_notification_counts(user):
    """Get notification counts for the user"""
    counts = {
        'announcements': 0,
        'messages': 0
    }
    
    try:
        # Count unread announcements
        if hasattr(user, 'role'):
            if user.role == 'student':
                try:
                    student_class = user.student_profile.current_class
                    counts['announcements'] = Announcement.objects.filter(
                        is_active=True
                    ).filter(
                        Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
                    ).filter(
                        Q(target_audience='All') |
                        Q(target_audience='Students') |
                        Q(target_audience='Class', target_class=student_class)
                    ).count()
                except:
                    counts['announcements'] = Announcement.objects.filter(
                        is_active=True,
                        target_audience__in=['All', 'Students']
                    ).count()
            elif user.role == 'teacher':
                counts['announcements'] = Announcement.objects.filter(
                    is_active=True,
                    target_audience__in=['All', 'Faculty']
                ).count()
        
        # Count unread messages (placeholder - implement message system)
        counts['messages'] = 0  # Will be implemented when message system is ready
        
    except Exception:
        pass
    
    return counts

def get_overview_context(user):
    """Get overview page context"""
    context = {}
    
    if hasattr(user, 'role'):
        if user.role == 'teacher':
            # Teacher overview data
            try:
                faculty_profile = user.faculty_profile
                context.update({
                    'my_subjects': CourseOffering.objects.filter(faculty=faculty_profile).count(),
                    'total_students': Enrollment.objects.filter(
                        course_offering__faculty=faculty_profile
                    ).values('student').distinct().count(),
                    'classes_today': 6,  # Placeholder - calculate from timetable
                    'pending_tasks': 5,  # Placeholder - calculate from grading system
                })
            except:
                context.update({
                    'my_subjects': 4,
                    'total_students': 120,
                    'classes_today': 6,
                    'pending_tasks': 5,
                })
        elif user.role == 'student':
            # Student overview data
            try:
                student_profile = user.student_profile
                context.update({
                    'my_subjects': student_profile.enrolled_subjects.count(),
                    'total_students': 1,
                    'classes_today': 6,
                    'pending_tasks': 3,
                })
            except:
                context.update({
                    'my_subjects': 6,
                    'total_students': 1,
                    'classes_today': 6,
                    'pending_tasks': 3,
                })
    
    return context

def get_attendance_context(user):
    """Get attendance page context"""
    context = {
        'classes': StudentClass.objects.filter(is_active=True),
        'subjects': [],  # Will be populated based on user role
        'recent_attendance': [],
        'attendance_stats': {
            'present': 85,
            'absent': 8,
            'late': 3,
            'rate': 89
        }
    }
    
    if hasattr(user, 'role') and user.role == 'teacher':
        # Get teacher's subjects
        try:
            faculty_profile = user.faculty_profile
            context['subjects'] = CourseOffering.objects.filter(faculty=faculty_profile)
        except:
            pass
    
    return context

def get_announcements_context(user):
    """Get announcements page context"""
    context = {
        'classes': StudentClass.objects.filter(is_active=True),
        'announcements': []
    }
    
    if hasattr(user, 'role') and user.role == 'teacher':
        # Get announcements created by this teacher
        context['announcements'] = Announcement.objects.filter(
            created_by=user
        ).order_by('-created_at')
    
    return context

def get_messages_context(user):
    """Get messages page context"""
    try:
        from .models import Message
        
        # Get sent and received messages
        sent_messages = Message.objects.filter(sender=user).order_by('-sent_at')
        received_messages = Message.objects.filter(recipient=user).order_by('-sent_at')
        unread_count = received_messages.filter(is_read=False).count()
        
        return {
            'messages': list(received_messages)[:20],  # Recent received messages
            'sent_messages': list(sent_messages)[:10],  # Recent sent messages
            'unread_count': unread_count
        }
    except Exception as e:
        print(f"Error getting messages context: {e}")
        return {
            'messages': [],
            'sent_messages': [],
            'unread_count': 0
        }

def get_courses_context(user):
    """Get courses page context"""
    context = {
        'courses': []
    }
    
    if hasattr(user, 'role') and user.role == 'teacher':
        try:
            faculty_profile = user.faculty_profile
            context['courses'] = CourseOffering.objects.filter(faculty=faculty_profile)
        except:
            pass
    elif user.role == 'student':
        try:
            student_profile = user.student_profile
            context['courses'] = Enrollment.objects.filter(student=student_profile)
        except:
            pass
    
    return context

def get_grading_context(user):
    """Get grading page context"""
    return {
        'pending_grades': [],
        'graded_assignments': []
    }

def get_timetable_context(user):
    """Get timetable page context"""
    return {
        'schedule': [],
        'today_classes': []
    }

def get_fees_context(user):
    """Get fees page context"""
    return {
        'fee_structure': [],
        'payment_history': []
    }

def get_library_context(user):
    """Get library page context"""
    return {
        'books': [],
        'borrowed_books': []
    }

def get_profile_context(user):
    """Get profile page context"""
    return {
        'user_profile': user,
        'profile_form': None  # Will be implemented
    }

# AJAX Form Handlers
class DashboardAjaxView(LoginRequiredMixin, View):
    """Base class for dashboard AJAX views"""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Invalid request'})
        return super().dispatch(request, *args, **kwargs)
    
    def form_invalid(self, form):
        return JsonResponse({
            'success': False,
            'errors': form.errors,
            'message': 'Please correct the errors below.'
        })
    
    def form_valid(self, form):
        form.save()
        return JsonResponse({
            'success': True,
            'message': 'Operation completed successfully!',
            'reload': True
        })

class CreateAnnouncementAjaxView(DashboardAjaxView):
    """AJAX view for creating announcements"""
    
    def post(self, request, *args, **kwargs):
        form = AnnouncementForm(request.POST, user=request.user)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.created_by = request.user
            announcement.save()
            return JsonResponse({
                'success': True,
                'message': 'Announcement created successfully!',
                'redirect': 'announcements'
            })
        else:
            return self.form_invalid(form)

class MarkAttendanceAjaxView(DashboardAjaxView):
    """AJAX view for marking attendance"""
    
    def post(self, request, *args, **kwargs):
        # This will be implemented with the attendance system
        return JsonResponse({
            'success': True,
            'message': 'Attendance marked successfully!',
            'reload': True
        })

@login_required
@require_http_methods(["POST"])
def mark_message_read(request, message_id):
    """Mark a received message as read"""
    try:
        message = get_object_or_404(Message, id=message_id, recipient=request.user)
        message.is_read = True
        message.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(["POST"])
def delete_received_message(request, message_id):
    """Delete a received message"""
    try:
        message = get_object_or_404(Message, id=message_id, recipient=request.user)
        message.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(["POST"])
def delete_sent_message(request, message_id):
    """Delete a sent message"""
    try:
        message = get_object_or_404(Message, id=message_id, sender=request.user)
        message.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
