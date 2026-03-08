from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group
from django.contrib import messages
from django.views.generic import CreateView
from django.contrib.auth.decorators import user_passes_test
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Count, Avg, Sum
from django.db.models import Q, Count, Avg, Sum as DBSum  # Alias to ensure no conflicts
from django.db.models.functions import Now
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
)
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import get_user_model
import json
import uuid
from .utils import is_student, is_faculty, is_admin, is_parent  # Ensure all these functions exist
from .forms import UserForm, UserUpdateForm, StudentProfileForm, FeeForm, MaterialUploadForm, MessageForm, ForumPostForm, ForumTopicForm, SubjectEnrollmentForm, BulkSubjectEnrollmentForm, SubjectForm, ClassForm, TimeTableForm

from .models import (
    Course, Department, StudentProfile, FacultyProfile, AdminProfile, HeadmasterProfile, ParentProfile,
    Enrollment, Attendance, Grade, ActivityLog, Fee, LeaveRequest,ExamSchedule, Payment, Announcement, Message,
    CourseOffering, Semester, ForumTopic, Book, BorrowedBook, Activity, Achievement, FeeStructure,
    ReportCard, Material, Schedule, ForumPost, NECTAExam, Subject, SubjectEnrollment, SchoolCalendar, 
    Notification, Participation, SystemSetting, TimeTable, Assignment, Submission
)

User = get_user_model()
class StudentDetailView(DetailView):
    model = StudentProfile
    template_name = 'students/student_detail.html'  # adjust path as needed
    context_object_name = 'student'

# Consolidated to SubjectManagementView below
def get_school_info():
    school_info = SystemSetting.objects.first()
    if not school_info:
        school_info = type('SchoolInfo', (), {
            'name': 'Default School Name',
            'email': 'contact@school.edu',
            'phone': '+1234567890',
            'address': '123 School Street, City',
            'logo': None,
            'established_year': 2000,
            'motto': 'Education is Key'
        })
    return school_info

 
@login_required
@user_passes_test(is_admin)
def faculty_register(request):
    from .forms import FacultyUserForm, FacultyProfileForm
    
    if request.method == 'POST':
        user_form = FacultyUserForm(request.POST)
        profile_form = FacultyProfileForm(request.POST, request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            return redirect('faculty_list')  # Ensure this URL exists
    else:
        user_form = FacultyUserForm()
        profile_form = FacultyProfileForm()
    return render(request, 'core/faculty_register.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@login_required
@user_passes_test(is_admin)
def faculty_list(request):
    faculty_members = FacultyProfile.objects.select_related('user')
    return render(request, 'core/faculty_list.html', {'faculty_members': faculty_members})
class StudentUpdateView(UpdateView):
    from .forms import StudentProfileForm
    
    model = StudentProfile
    form_class = StudentProfileForm
    template_name = 'students/student_form.html'  # adjust to your template path
    success_url = reverse_lazy('student_list')
class FacultyListView(ListView):
    model = FacultyProfile
    template_name = 'core/faculty_list.html'  # Update with your actual template path
    context_object_name = 'faculties'
    
    def get_queryset(self):
        # You can add filtering/sorting logic here if needed
        return FacultyProfile.objects.select_related('user').all()
class FacultyDetailView(LoginRequiredMixin, DetailView):
    model = FacultyProfile
    template_name = 'core/faculty_detail.html'  # Update with your actual template path
    context_object_name = 'faculty'
    pk_url_kwarg = 'pk'  # This is the default, but explicit is better
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any additional context data here if needed
        return context
class FacultyUpdateView(UpdateView):
    from .forms import FacultyProfileForm
    
    model = FacultyProfile
    form_class = FacultyProfileForm
    template_name = 'core/faculty_edit.html'
    context_object_name = 'faculty'
    pk_url_kwarg = 'pk'
    
    def get_success_url(self):
        return reverse_lazy('faculty_detail', kwargs={'pk': self.object.pk})
    
    def test_func(self):
        # Only allow faculty to edit their own profile or admins
        faculty = self.get_object()
        return self.request.user == faculty.user or is_admin(self.request.user)
    

class CourseManagementView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Course
    template_name = 'core/course_management/course_management.html'
    context_object_name = 'courses'
    
    def test_func(self):
        return is_admin(self.request.user)
    
    def get_queryset(self):
        return Course.objects.select_related('department').all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import Department, User, StudentProfile
        context.update({
            'departments_count': Department.objects.count(),
            'total_students': User.objects.filter(role='student').count(),
            'role': 'Administrator',
            'title': 'Subject Management'
        })
        return context


class ActivityLogView(LoginRequiredMixin, ListView):
    model = ActivityLog
    template_name = 'core/activity_log.html'
    context_object_name = 'activity_logs'
    paginate_by = 20  # Show 20 logs per page

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter logs for non-admin users (only show their own activities)
        if not is_admin(self.request.user):
            queryset = queryset.filter(user=self.request.user)
            
        return queryset.order_by('-timestamp')  # Newest first

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_admin'] = is_admin(self.request.user)
        return context
# Permission check functions are imported from .utils

def is_headmaster(user):
    return user.is_authenticated and hasattr(user, 'role') and user.role == 'headmaster'
# ======================
# Core Views
# ======================
@login_required
def attendance_summary(request):
    # For faculty: show their courses' attendance
    if is_faculty(request.user):
        courses = Course.objects.filter(faculty=request.user.facultyprofile)
        attendance_data = []
        for course in courses:
            records = Attendance.objects.filter(course=course)
            attendance_data.append({
                'course': course,
                'total_students': records.values('student').distinct().count(),
                'average_attendance': records.filter(present=True).count() / records.count() * 100 if records.count() > 0 else 0
            })
        context = {
            'attendance_data': attendance_data,
            'user_type': 'faculty'
        }

    # For admin: show all courses attendance
    elif is_admin(request.user):
        courses = Course.objects.all()
        attendance_data = []
        for course in courses:
            records = Attendance.objects.filter(course=course)
            attendance_data.append({
                'course': course,
                'total_students': records.values('student').distinct().count(),
                'average_attendance': records.filter(present=True).count() / records.count() * 100 if records.count() > 0 else 0
            })
        context = {
            'attendance_data': attendance_data,
            'user_type': 'admin'
        }

    # For students: show their own attendance
    elif is_student(request.user):
        student_profile = request.user.studentprofile
        attendance_records = Attendance.objects.filter(student=student_profile)
        context = {
            'attendance_records': attendance_records,
            'user_type': 'student'
        }

    else:
        context = {'error': 'Unauthorized access'}

    return render(request, 'core/attendance/attendance_list.html', context)
@login_required
def view_fee_structure(request):
    # Get all fee structures
    fee_structures = FeeStructure.objects.all().order_by('department', 'program')
    
    # For students: show only their program's fee structure
    if is_student(request.user):
        student_profile = request.user.studentprofile
        fee_structures = fee_structures.filter(
            department=student_profile.department,
            program=student_profile.program
        )
    
    # For faculty: show fee structures from their department
    elif is_faculty(request.user):
        faculty_profile = request.user.facultyprofile
        fee_structures = fee_structures.filter(
            department=faculty_profile.department
        )
    
    context = {
        'fee_structures': fee_structures,
        'is_admin': is_admin(request.user)
    }
    return render(request, 'core/fee_structure.html', context)
@login_required
@user_passes_test(is_admin)
def user_approve(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = True  # or any logic to approve the user
    user.save()
    messages.success(request, f"User {user.username} has been approved.")
    return redirect('user_approval')
class UserApprovalView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = 'core/user_approval.html'  # create this template
    context_object_name = 'pending_users'

    def get_queryset(self):
        # Filter users who are pending approval, adjust this as per your logic
        return User.objects.filter(is_active=False)

    def test_func(self):
        # Only allow admins or staff to access this view
        return self.request.user.is_staff
class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = 'core/admin_management/admin_user_list.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def test_func(self):
        return is_admin(self.request.user)
    
    def get_queryset(self):
        queryset = User.objects.all().order_by('-date_joined')
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(username__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        
        # Filter by role
        role_filter = self.request.GET.get('role', '')
        if role_filter:
            queryset = queryset.filter(role=role_filter)
        
        # Filter by status
        status_filter = self.request.GET.get('status', '')
        if status_filter == 'active':
            queryset = queryset.filter(is_active=True)
        elif status_filter == 'inactive':
            queryset = queryset.filter(is_active=False)
        elif status_filter == 'pending':
            queryset = queryset.filter(is_active=False)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calculate user statistics
        total_users = User.objects.count()
        students = User.objects.filter(role='student').count()
        teachers = User.objects.filter(role='teacher').count()
        headmasters = User.objects.filter(role='headmaster').count()
        admins = User.objects.filter(role='admin').count()
        
        context.update({
            'title': 'User Management',
            'total_users': total_users,
            'students': students,
            'teachers': teachers,
            'headmasters': headmasters,
            'admins': admins,
        })
        
        return context
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'  # fallback template (optional)

    def dispatch(self, request, *args, **kwargs):
        if is_student(request.user):
            return redirect('student_dashboard')
        elif is_faculty(request.user):
            return redirect('faculty_dashboard')
        elif is_admin(request.user):
            return redirect('admin_student_list')
        elif is_parent(request.user):
            return redirect('parent_dashboard')
        return super().dispatch(request, *args, **kwargs)

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'core/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if hasattr(user, 'student_profile'):
            context['profile'] = user.student_profile
            context['profile_type'] = 'student'
        elif hasattr(user, 'faculty_profile'):
            context['profile'] = user.faculty_profile
            context['profile_type'] = 'faculty'
        elif hasattr(user, 'admin_profile'):
            context['profile'] = user.admin_profile
            context['profile_type'] = 'admin'
        elif hasattr(user, 'parent_profile'):
            context['profile'] = user.parent_profile
            context['profile_type'] = 'parent'
        
        return context

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'core/profile_update.html'
    fields = ['first_name', 'last_name', 'email']
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        from .forms import StudentProfileForm, FacultyProfileForm, AdminProfileForm
        
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        
        # Add profile form based on user role
        if hasattr(self.request.user, 'student_profile'):
            context['profile_form'] = StudentProfileForm(instance=self.request.user.student_profile)
        elif hasattr(self.request.user, 'faculty_profile'):
            context['profile_form'] = FacultyProfileForm(instance=self.request.user.faculty_profile)
        elif hasattr(self.request.user, 'admin_profile'):
            context['profile_form'] = AdminProfileForm(instance=self.request.user.admin_profile)
        
        return context

    def post(self, request, *args, **kwargs):
        from .forms import StudentProfileForm, FacultyProfileForm, AdminProfileForm
        
        self.object = self.get_object()
        form = self.get_form()
        
        profile_form = None
        if hasattr(request.user, 'student_profile'):
            profile_form = StudentProfileForm(request.POST, instance=request.user.student_profile)
        elif hasattr(request.user, 'faculty_profile'):
            profile_form = FacultyProfileForm(request.POST, instance=request.user.faculty_profile)
        elif hasattr(request.user, 'admin_profile'):
            profile_form = AdminProfileForm(request.POST, instance=request.user.admin_profile)
        
        if form.is_valid() and (profile_form is None or profile_form.is_valid()):
            return self.form_valid(form, profile_form)
        return self.form_invalid(form, profile_form)

    def form_valid(self, form, profile_form):
        form.save()
        if profile_form:
            profile_form.save()
        messages.success(self.request, "Profile updated successfully!")
        return super().form_valid(form)

    def form_invalid(self, form, profile_form):
        messages.error(self.request, "Please correct the errors below.")
        return self.render_to_response(
            self.get_context_data(form=form, profile_form=profile_form)
        )

# ======================
# Authentication Views
#
@method_decorator(csrf_protect, name='dispatch')
class CustomLoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return self.redirect_based_on_role(request.user)
        form = AuthenticationForm()
        
        # Check if user just registered and pre-fill the form
        context = {'form': form}
        if 'registration_role' in request.session:
            context['registration_role'] = request.session['registration_role']
            context['registration_username'] = request.session.get('registration_username', '')
            # Clear session data after using it
            del request.session['registration_role']
            if 'registration_username' in request.session:
                del request.session['registration_username']
        
        return render(request, 'core/login.html', context)

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        
        if form.is_valid():
            user = form.get_user()
            
            auth_login(request, user)
            
            # Show success message with actual role
            user_role = getattr(user, 'role', 'user').title()
            messages.success(request, f'Welcome back! You are logged in as {user_role}.')
            
            return self.redirect_based_on_role(user)
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
            return self.get_context_with_form(request, form)
    
    def get_context_with_form(self, request, form):

        """Helper method to render form with proper styling"""
        # Add Tailwind CSS classes and placeholders to form fields
        form.fields['username'].widget.attrs.update({
            'placeholder': 'Enter your username or email',
            'class': 'form-input w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200 bg-white/80 backdrop-blur-sm'
        })
        form.fields['password'].widget.attrs.update({
            'placeholder': 'Enter your password',
            'class': 'form-input w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200 bg-white/80 backdrop-blur-sm'
        })
        return render(request, 'core/login.html', {'form': form})
    
    def redirect_based_on_role(self, user):
        """Redirect user based on their role to role-specific unified dashboard"""
        if hasattr(user, 'role'):
            if user.role == 'student':
                return redirect('student_unified_dashboard', page='overview')
            elif user.role == 'teacher':
                return redirect('unified_dashboard', page='overview')
            elif user.role == 'headmaster':
                return redirect('headmaster_unified_dashboard', page='overview')
            elif user.role == 'admin':
                return redirect('admin_unified_dashboard', page='overview')
            else:
                # Default to student dashboard if no role is set
                return redirect('student_unified_dashboard', page='overview')
        else:
            # Default to student dashboard if no role is set
            return redirect('student_unified_dashboard', page='overview')

class CustomLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('public_home')

# Public Registration Views
from .forms import PublicUserRegistrationForm

class PublicRegisterView(CreateView):
    """Registration for normal users and students"""
    model = User
    form_class = PublicUserRegistrationForm
    template_name = 'core/public_pages/public_register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password1'])
        user.save()
        
        # Create profile based on role
        if user.role == 'student':
            user.is_student = True
            user.save()
            # Create StudentProfile with additional details
            StudentProfile.objects.create(
                user=user,
                roll_number=f"STU{user.id:06d}",
                admission_year=timezone.now().year,
                current_form=1,
                current_semester=1,
                phone=form.cleaned_data.get('phone', ''),
                address=form.cleaned_data.get('address', ''),
                date_of_birth=form.cleaned_data.get('date_of_birth', None),
                gender=form.cleaned_data.get('gender', ''),
                necta_exam_number=form.cleaned_data.get('necta_exam_number', ''),
                birth_certificate_number=form.cleaned_data.get('birth_certificate_number', ''),
                previous_school=form.cleaned_data.get('previous_school', ''),
            )
            messages.success(self.request, f"Welcome {user.get_full_name() or user.username}! Your student account has been created successfully. Please login to access your dashboard.")
        elif user.role == 'teacher':
            user.is_faculty = True
            user.save()
            # FacultyProfile will be created by admin
            messages.success(self.request, f"Welcome {user.get_full_name() or user.username}! Your teacher account has been created successfully. Please login to access your dashboard.")
        elif user.role == 'headmaster':
            user.is_headmaster = True
            user.save()
            # HeadmasterProfile will need to be created by admin
            messages.success(self.request, f"Welcome {user.get_full_name() or user.username}! Your headmaster account has been created successfully. Please login to access your dashboard.")
        
        # Store registration info for login page
        self.request.session['registration_role'] = user.role
        self.request.session['registration_username'] = user.username
        
        return super().form_valid(form)

# Role-based Dashboard Views
class RoleBasedDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        return self.redirect_based_on_role(request.user)
    
    def redirect_based_on_role(self, user):
        """Redirect user based on their role to role-specific unified dashboard"""
        if user.role == 'normal':
            return redirect('public_home')
        elif user.role == 'student':
            return redirect('student_unified_dashboard', page='overview')
        elif user.role == 'teacher':
            return redirect('unified_dashboard', page='overview')
        elif user.role == 'headmaster':
            return redirect('headmaster_unified_dashboard', page='overview')
        elif user.role == 'admin':
            return redirect('admin_unified_dashboard', page='overview')
        else:
            return redirect('public_home')

# Teacher Dashboard
@login_required
def teacher_dashboard(request):
    if not request.user.role == 'teacher':
        return redirect('public_home')
    
    try:
        # Get teacher profile
        faculty_profile = request.user.faculty_profile
    except FacultyProfile.DoesNotExist:
        faculty_profile = None
    
    # Get courses assigned to this teacher
    from .models import CourseOffering
    my_courses = CourseOffering.objects.filter(
        faculty=faculty_profile
    ).select_related('course', 'semester').count()
    
    # Get total students in teacher's courses
    from django.db.models import Count
    courses_with_students = CourseOffering.objects.filter(
        faculty=faculty_profile
    ).annotate(student_count=Count('enrollments'))
    
    total_students = sum(course.student_count for course in courses_with_students)
    
    # Get pending assignments (mock data for now)
    pending_assignments = 5
    
    # Get classes today (mock data for now)
    classes_today = 3
    
    # Get actual courses for display
    courses = CourseOffering.objects.filter(
        faculty=faculty_profile
    ).select_related('course', 'semester').prefetch_related('enrollments')
    
    context = {
        'user': request.user,
        'role': 'Teacher',
        'faculty_profile': faculty_profile,
        'my_subjects': my_courses,
        'total_students': total_students,
        'pending_assignments': pending_assignments,
        'classes_today': classes_today,
        'subjects': courses,
        'school_info': get_school_info(),
    }
    return render(request, 'core/teacher_parts/dashboard_old.html', context)

# Headmaster Dashboard
@login_required
def headmaster_dashboard(request):
    if not request.user.role == 'headmaster':
        return redirect('public_home')
    
    total_students = User.objects.filter(role='student').count()
    total_teachers = User.objects.filter(role='teacher').count()
    total_staff = User.objects.filter(role__in=['teacher', 'admin', 'headmaster']).count()
    total_departments = Department.objects.count()
    
    context = {
        'user': request.user,
        'role': 'Head of School',
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_staff': total_staff,
        'departments_count': total_departments,
        'courses': Course.objects.all(),
        'recent_activities': User.objects.order_by('-date_joined')[:5],
    }
    return render(request, 'core/headmaster_management/headmaster_dashboard.html', context)


# School Admin Dashboard
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Enhanced admin dashboard with comprehensive CRUD operations"""
    
    # Get comprehensive statistics
    total_students = StudentProfile.objects.count()
    active_students = StudentProfile.objects.filter(user__is_active=True).count()
    new_students_this_month = 0  # TODO: Calculate from Enrollment model if needed
    
    total_teachers = FacultyProfile.objects.count()
    active_teachers = FacultyProfile.objects.filter(user__is_active=True).count()
    new_teachers_this_month = FacultyProfile.objects.filter(
        user__date_joined__month=timezone.now().month,
        user__date_joined__year=timezone.now().year
    ).count()
    
    # Course statistics
    total_courses = Course.objects.count()
    active_courses = CourseOffering.objects.filter(
        semester__is_active=True
    ).count()
    new_courses_this_month = CourseOffering.objects.filter(
        created_at__month=timezone.now().month,
        created_at__year=timezone.now().year
    ).count()
    
    # Financial statistics
    from django.db.models import Sum
    total_revenue = Payment.objects.aggregate(
        total=Sum('amount')
    )['total'] or 0
    fees_collected = Payment.objects.filter(
        status='completed'
    ).count()
    fees_pending = Payment.objects.filter(
        status='pending'
    ).count()
    
    # Calculate growth rates
    student_growth_rate = 12  # Example growth rate
    teacher_growth_rate = 8   # Example growth rate
    course_growth_rate = 5   # Example growth rate
    revenue_growth_rate = 15  # Example growth rate
    
    # Get recent activities
    recent_activities = ActivityLog.objects.select_related('user').order_by('-timestamp')[:10]
    
    print("DEBUG: Statistics calculated successfully")
    
    # Fee information with better formatting
    from django.db.models import Sum
    total_fees_collected = Fee.objects.filter(is_paid=True).aggregate(total=Sum('amount'))['total'] or 0
    pending_fees = Fee.objects.filter(is_paid=False).count()
    context = {
        'total_students': total_students,
        'active_students': active_students,
        'new_students_this_month': new_students_this_month,
        'total_teachers': total_teachers,
        'active_teachers': active_teachers,
        'new_teachers_this_month': new_teachers_this_month,
        'total_courses': total_courses,
        'active_courses': active_courses,
        'new_courses_this_month': new_courses_this_month,
        'total_revenue': total_revenue,
        'fees_collected': fees_collected,
        'fees_pending': fees_pending,
        'student_growth_rate': student_growth_rate,
        'teacher_growth_rate': teacher_growth_rate,
        'course_growth_rate': course_growth_rate,
        'revenue_growth_rate': revenue_growth_rate,
        'recent_activities': recent_activities,
    }
    
    return render(request, 'core/admin_management/admin_dashboard.html', context)

# API Views
@login_required
def debug_permissions(request):
    """Debug view to check user permissions"""
    user_info = {
        'username': request.user.username,
        'is_authenticated': request.user.is_authenticated,
        'is_superuser': request.user.is_superuser,
        'is_staff': request.user.is_staff,
        'role': getattr(request.user, 'role', 'NO_ROLE'),
        'has_admin_profile': hasattr(request.user, 'admin_profile'),
        'is_admin_result': is_admin(request.user),
        'user_id': request.user.id,
        'email': request.user.email,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
    }
    
    return JsonResponse(user_info)

@login_required
def api_test(request):
    """Simple test API endpoint"""
    return JsonResponse({'success': True, 'message': 'API test successful'})

def api_test_no_auth(request):
    """Simple test API endpoint without authentication"""
    return JsonResponse({'success': True, 'message': 'API test no auth successful'})

def api_test_plain(request):
    """Simple test endpoint returning plain text"""
    from django.http import HttpResponse
    return HttpResponse('Plain text response', content_type='text/plain')

@login_required
def api_create_teacher(request):
    """API endpoint for creating teachers"""
    if not is_admin(request.user):
        return JsonResponse({'success': False, 'message': 'Permission denied'})
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
    
    try:
        import json
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email', 'username', 'password', 'department', 'designation']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({'success': False, 'message': f'{field.replace("_", " ").title()} is required'})
        
        # Check if username already exists
        if User.objects.filter(username=data['username']).exists():
            return JsonResponse({'success': False, 'message': 'Username already exists'})
        
        # Check if email already exists
        if User.objects.filter(email=data['email']).exists():
            return JsonResponse({'success': False, 'message': 'Email already exists'})
        
        # Get department
        try:
            department = Department.objects.get(id=data['department'])
        except Department.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid department'})
        
        # Create user
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role='teacher'
        )
        
        # Create faculty profile
        faculty_profile = FacultyProfile.objects.create(
            user=user,
            department=department,
            designation=data['designation'],
            specialization=data.get('specialization', '')
        )
        
        return JsonResponse({
            'success': True, 
            'message': 'Teacher created successfully',
            'teacher_id': faculty_profile.id
        })
        
    except json.JSONDecodeError as e:
        return JsonResponse({'success': False, 'message': f'Invalid JSON data: {str(e)}'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
def api_users(request, pk=None):
    """API endpoint for users CRUD operations"""
    # Temporarily check permissions inside the function for debugging
    if not is_admin(request.user):
        return JsonResponse({'error': 'Permission denied - user is not admin', 'debug': {
            'username': request.user.username,
            'role': getattr(request.user, 'role', 'NO_ROLE'),
            'is_superuser': request.user.is_superuser,
            'has_admin_profile': hasattr(request.user, 'admin_profile'),
            'is_admin_result': is_admin(request.user)
        }}, status=403)
    
    if request.method == 'GET':
        # Get query parameters
        page = request.GET.get('page', 1)
        search = request.GET.get('search', '')
        role = request.GET.get('role', '')
        status = request.GET.get('status', '')
        
        # Build query
        queryset = User.objects.all().order_by('-date_joined')
        
        # Apply filters
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(username__icontains=search) |
                Q(email__icontains=search)
            )
        
        if role:
            queryset = queryset.filter(role=role)
        
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        # Paginate
        paginator = Paginator(queryset, 20)
        users_page = paginator.get_page(page)
        
        # Prepare data
        users_data = []
        for user in users_page:
            users_data.append({
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'is_active': user.is_active,
                'date_joined': user.date_joined.isoformat()
            })
        
        # Prepare pagination data
        pagination_data = {
            'current_page': users_page.number,
            'total_pages': users_page.paginator.num_pages,
            'has_previous': users_page.has_previous(),
            'has_next': users_page.has_next(),
            'total_items': users_page.paginator.count
        }
        
        return JsonResponse({
            'users': users_data,
            'pagination': pagination_data
        })
    
    elif request.method == 'DELETE':
        # Delete user
        if not pk:
            return JsonResponse({'error': 'User ID is required'}, status=400)
        
        try:
            user = User.objects.get(id=pk)
            user.delete()
            return JsonResponse({'success': True, 'message': 'User deleted successfully'})
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

class StudentListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = StudentProfile
    template_name = 'core/admin_management/admin_student_list.html'
    context_object_name = 'students'
    paginate_by = 20
    
    def test_func(self):
        return is_admin(self.request.user)
    
    def get_queryset(self):
        queryset = StudentProfile.objects.select_related('user', 'department').order_by('user__first_name', 'user__last_name')
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(user__username__icontains=search_query) |
                Q(roll_number__icontains=search_query) |
                Q(user__email__icontains=search_query)
            )
        
        # Filter by department
        department_filter = self.request.GET.get('department', '')
        if department_filter:
            queryset = queryset.filter(department_id=department_filter)
        
        # Filter by form
        form_filter = self.request.GET.get('form', '')
        if form_filter:
            queryset = queryset.filter(current_form=form_filter)
        
        # Filter by status
        status_filter = self.request.GET.get('status', '')
        if status_filter == 'active':
            queryset = queryset.filter(user__is_active=True)
        elif status_filter == 'inactive':
            queryset = queryset.filter(user__is_active=False)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add statistics for the student list page
        total_students = StudentProfile.objects.count()
        active_students = StudentProfile.objects.filter(user__is_active=True).count()
        inactive_students = StudentProfile.objects.filter(user__is_active=False).count()
        new_students = StudentProfile.objects.filter(
            user__date_joined__month=timezone.now().month,
            user__date_joined__year=timezone.now().year
        ).count()
        
        # Get departments for filter dropdown
        from .models import Department
        departments = Department.objects.all()
        departments_count = departments.count()
        
        context.update({
            'total_students': total_students,
            'active_students': active_students,
            'inactive_students': inactive_students,
            'new_students': new_students,
            'departments': departments,
            'departments_count': departments_count,
        })
        
        return context

@login_required
@user_passes_test(is_admin)
def admin_student_list(request):
    """Complete student management with CRUD operations"""
    
    # Get all students with related data
    students = StudentProfile.objects.select_related(
        'user', 'department'
    ).prefetch_related(
        'enrollments__course_offering__course',
        'enrollments__attendances'
    ).order_by('-user__date_joined')
    
    # Get departments for filter
    departments = Department.objects.all()
    
    # Apply filters
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
    
    # Calculate statistics
    total_students = students.count()
    active_students = students.filter(user__is_active=True).count()
    new_students_this_month = 0  # TODO: Calculate from Enrollment model if needed
    
    context = {
        'students': students,
        'departments': departments,
        'total_students': total_students,
        'active_students': active_students,
        'new_students_this_month': new_students_this_month,
        'search_query': search_query,
        'department_filter': department_filter,
        'status_filter': status_filter,
    }
    
    return render(request, 'core/admin_management/admin_student_list.html', context)


@login_required
@user_passes_test(is_admin)
def admin_student_detail(request, pk):
    """View detailed student information"""
    student = get_object_or_404(
        StudentProfile.objects.select_related(
            'user', 'department'
        ).prefetch_related(
            'enrollments__course_offering__course',
            'enrollments__attendances',
            'enrollments__grades'
        ),
        pk=pk
    )
    
    # Get student statistics
    enrollments = student.enrollments.all()
    total_attendance = 0
    present_attendance = 0
    
    for enrollment in enrollments:
        attendance_records = enrollment.attendances.all()
        total_attendance += attendance_records.count()
        present_attendance += attendance_records.filter(status='P').count()
    
    attendance_percentage = (present_attendance / total_attendance * 100) if total_attendance > 0 else 0
    
    # Get recent activities
    recent_activities = ActivityLog.objects.filter(
        user=student.user
    ).order_by('-timestamp')[:10]
    
    context = {
        'student': student,
        'enrollments': enrollments,
        'attendance_percentage': round(attendance_percentage, 1),
        'recent_activities': recent_activities,
    }
    
    return render(request, 'core/admin_management/admin_student_detail.html', context)


@login_required
@user_passes_test(is_admin)
def admin_student_edit(request, pk):
    """Edit existing student"""
    student = get_object_or_404(StudentProfile.objects.select_related('user', 'department'), pk=pk)
    
    if request.method == 'POST':
        try:
            # Update user information
            student.user.first_name = request.POST.get('first_name')
            student.user.last_name = request.POST.get('last_name')
            student.user.email = request.POST.get('email')
            
            # Update password if provided
            new_password = request.POST.get('password')
            if new_password:
                student.user.set_password(new_password)
            
            student.user.save()
            
            # Update student profile
            student.roll_number = request.POST.get('roll_number')
            student.phone = request.POST.get('phone', '')
            student.address = request.POST.get('address', '')
            student.current_form = request.POST.get('current_form')
            student.father_name = request.POST.get('father_name', '')
            student.mother_name = request.POST.get('mother_name', '')
            student.guardian_name = request.POST.get('guardian_name', '')
            student.guardian_phone = request.POST.get('guardian_phone', '')
            
            # Update department
            department_id = request.POST.get('department')
            if department_id:
                student.department = get_object_or_404(Department, id=department_id)
            
            student.save()
            
            messages.success(request, f'Student {student.user.get_full_name()} updated successfully!')
            return redirect('admin_student_detail', pk=student.pk)
            
        except Exception as e:
            messages.error(request, f'Error updating student: {str(e)}')
    
    departments = Department.objects.all()
    context = {
        'student': student,
        'departments': departments,
    }
    
    return render(request, 'core/admin_management/admin_student_edit.html', context)


@login_required
@user_passes_test(is_admin)
def admin_student_delete(request, pk):
    """Delete student"""
    student = get_object_or_404(StudentProfile, pk=pk)
    
    if request.method == 'POST':
        student_name = student.user.get_full_name()
        user = student.user
        student.delete()
        user.delete()
        
        messages.success(request, f'Student {student_name} deleted successfully!')
        return redirect('admin_student_list')
    
    context = {
        'student': student,
    }
    
    return render(request, 'core/admin_management/admin_student_delete.html', context)

@login_required
@user_passes_test(is_admin)
def admin_student_create(request):
    """Create a new student"""
    if request.method == 'POST':
        try:
            # Get form data
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            roll_number = request.POST.get('roll_number')
            department = request.POST.get('department')
            admission_year = request.POST.get('admission_year')
            current_form = request.POST.get('current_form')
            current_semester = request.POST.get('current_semester')
            phone = request.POST.get('phone', '')
            address = request.POST.get('address', '')
            necta_exam_number = request.POST.get('necta_exam_number', '')
            birth_certificate_number = request.POST.get('birth_certificate_number', '')
            previous_school = request.POST.get('previous_school', '')
            
            # Validate required fields
            if not all([first_name, last_name, username, email, password, roll_number, 
                       department_id, admission_year, current_form, current_semester]):
                messages.error(request, 'Please fill in all required fields.', extra_tags='error')
                return redirect('admin_student_list')
            
            # Check if username already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists. Please choose a different username.', extra_tags='error')
                return redirect('admin_student_list')
            
            # Check if email already exists
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists. Please use a different email.', extra_tags='error')
                return redirect('admin_student_list')
            
            # Check if roll number already exists
            if StudentProfile.objects.filter(roll_number=roll_number).exists():
                messages.error(request, 'Roll number already exists. Please use a different roll number.', extra_tags='error')
                return redirect('admin_student_list')
            
            # Create user account
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role='student',
                is_active=True
            )
            
            # Create student profile
            student = StudentProfile.objects.create(
                user=user,
                roll_number=roll_number,
                department=Department.objects.get(id=department),
                admission_year=int(admission_year),
                current_form=int(current_form),
                current_semester=int(current_semester),
                phone=phone,
                address=address,
                necta_exam_number=necta_exam_number,
                birth_certificate_number=birth_certificate_number,
                previous_school=previous_school
            )
            
            messages.success(request, f'Student {first_name} {last_name} has been successfully added to the system!', extra_tags='success')
            return redirect('admin_student_list')
            
        except Exception as e:
            messages.error(request, f'An error occurred while creating the student: {str(e)}', extra_tags='error')
            return redirect('admin_student_list')
    
    # If GET request, redirect to student list
    return redirect('admin_student_list')

class StudentDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = StudentProfile
    template_name = 'core/admin_management/admin_student_detail.html'
    context_object_name = 'student'
    
    def test_func(self):
        return is_admin(self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.get_object()
        
        # Get student enrollments with course information
        enrollments = Enrollment.objects.filter(student=student).select_related('course', 'semester')
        context['enrollments'] = enrollments
        
        # Get student fees
        fees = Fee.objects.filter(student=student).order_by('-due_date')
        context['fees'] = fees
        
        # Calculate fee statistics
        total_fees = fees.aggregate(total=DBSum('amount'))['total'] or 0
        paid_fees = fees.filter(status='paid').aggregate(total=DBSum('amount'))['total'] or 0
        context['total_fees'] = total_fees
        context['paid_fees'] = paid_fees
        context['outstanding_fees'] = total_fees - paid_fees
        
        # Get NECTA exam results
        necta_exams = NECTAExam.objects.filter(student=student).order_by('-exam_year', '-exam_month')
        context['necta_exams'] = necta_exams
        
        context['title'] = f'Student Details: {student.user.get_full_name()}'
        return context

class StudentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = StudentProfile
    form_class = StudentProfileForm
    template_name = 'core/admin_management/admin_student_edit.html'
    success_url = reverse_lazy('admin_student_list')
    
    def test_func(self):
        return is_admin(self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Student'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Student information updated successfully!')
        return super().form_valid(form)

class StudentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = StudentProfile
    template_name = 'core/admin_management/admin_student_delete.html'
    success_url = reverse_lazy('admin_student_list')
    
    def test_func(self):
        return is_admin(self.request.user)
    
    def delete(self, request, *args, **kwargs):
        student = self.get_object()
        messages.success(request, f'Student {student.user.get_full_name()} deleted successfully!')
        return super().delete(request, *args, **kwargs)

# ======================
# Teacher Management Views  
# ======================

class TeacherListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = FacultyProfile
    template_name = 'core/admin_management/admin_teacher_list.html'
    context_object_name = 'teachers'
    paginate_by = 20
    
    def test_func(self):
        return is_admin(self.request.user)
    
    def get_queryset(self):
        queryset = FacultyProfile.objects.select_related('user', 'department').order_by('user__first_name', 'user__last_name')
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(user__username__icontains=search_query) |
                Q(employee_id__icontains=search_query) |
                Q(user__email__icontains=search_query) |
                Q(specialization__icontains=search_query)
            )
        
        # Filter by department
        department_filter = self.request.GET.get('department', '')
        if department_filter:
            queryset = queryset.filter(department__id=department_filter)
        
        # Filter by status
        status_filter = self.request.GET.get('status', '')
        if status_filter == 'active':
            queryset = queryset.filter(user__is_active=True)
        elif status_filter == 'inactive':
            queryset = queryset.filter(user__is_active=False)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add statistics for the teacher list page
        total_teachers = FacultyProfile.objects.count()
        active_teachers = FacultyProfile.objects.filter(user__is_active=True).count()
        new_teachers = FacultyProfile.objects.filter(
            user__date_joined__month=timezone.now().month,
            user__date_joined__year=timezone.now().year
        ).count()
        total_departments = Department.objects.count()
        total_students = StudentProfile.objects.count()
        
        # Get departments for filter dropdown
        departments = Department.objects.all()
        
        context.update({
            'title': 'Teacher Management',
            'total_teachers': total_teachers,
            'active_teachers': active_teachers,
            'new_teachers': new_teachers,
            'total_departments': total_departments,
            'departments': departments,
            'total_students': total_students,
        })
        
        return context

@login_required
@user_passes_test(is_admin)
def admin_teacher_list(request):
    """Complete teacher management with CRUD operations"""
    
    # Get all teachers with related data
    teachers = FacultyProfile.objects.select_related(
        'user', 'department'
    ).prefetch_related(
        'courseofferings__course',
        'courseofferings__semester'
    ).order_by('-user__date_joined')
    
    # Get departments for filter
    departments = Department.objects.all()
    
    # Apply filters
    search_query = request.GET.get('search', '')
    department_filter = request.GET.get('department', '')
    status_filter = request.GET.get('status', '')
    
    if search_query:
        teachers = teachers.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(employee_id__icontains=search_query) |
            Q(specialization__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    if department_filter:
        teachers = teachers.filter(department_id=department_filter)
    
    if status_filter:
        if status_filter == 'active':
            teachers = teachers.filter(user__is_active=True)
        elif status_filter == 'inactive':
            teachers = teachers.filter(user__is_active=False)
    
    # Calculate statistics
    total_teachers = teachers.count()
    active_teachers = teachers.filter(user__is_active=True).count()
    new_teachers_this_month = teachers.filter(
        user__date_joined__month=timezone.now().month,
        user__date_joined__year=timezone.now().year
    ).count()
    
    context = {
        'teachers': teachers,
        'departments': departments,
        'total_teachers': total_teachers,
        'active_teachers': active_teachers,
        'new_teachers_this_month': new_teachers_this_month,
        'search_query': search_query,
        'department_filter': department_filter,
        'status_filter': status_filter,
    }
    
    return render(request, 'core/admin_management/admin_teacher_list.html', context)


@login_required
@user_passes_test(is_admin)
def admin_teacher_detail(request, pk):
    """View detailed teacher information"""
    teacher = get_object_or_404(
        FacultyProfile.objects.select_related(
            'user', 'department'
        ).prefetch_related(
            'courseofferings__course',
            'courseofferings__semester',
            'courseofferings__enrollments'
        ),
        pk=pk
    )
    
    # Get teacher statistics
    course_offerings = teacher.courseofferings.all()
    total_students = 0
    active_courses = 0
    
    for offering in course_offerings:
        enrollment_count = offering.enrollments.count()
        total_students += enrollment_count
        if enrollment_count > 0:
            active_courses += 1
    
    # Get recent activities
    recent_activities = ActivityLog.objects.filter(
        user=teacher.user
    ).order_by('-timestamp')[:10]
    
    context = {
        'teacher': teacher,
        'course_offerings': course_offerings,
        'total_students': total_students,
        'active_courses': active_courses,
        'recent_activities': recent_activities,
    }
    
    return render(request, 'core/admin_management/admin_teacher_detail.html', context)


@login_required
@user_passes_test(is_admin)
def admin_teacher_edit(request, pk):
    """Edit existing teacher"""
    teacher = get_object_or_404(FacultyProfile.objects.select_related('user', 'department'), pk=pk)
    
    if request.method == 'POST':
        try:
            # Update user information
            teacher.user.first_name = request.POST.get('first_name')
            teacher.user.last_name = request.POST.get('last_name')
            teacher.user.email = request.POST.get('email')
            
            # Update password if provided
            new_password = request.POST.get('password')
            if new_password:
                teacher.user.set_password(new_password)
            
            teacher.user.save()
            
            # Update teacher profile
            teacher.employee_id = request.POST.get('employee_id')
            teacher.phone = request.POST.get('phone', '')
            teacher.specialization = request.POST.get('specialization')
            teacher.qualification = request.POST.get('qualification', '')
            teacher.experience_years = request.POST.get('experience_years', 0)
            teacher.address = request.POST.get('address', '')
            
            # Update department
            department_id = request.POST.get('department')
            if department_id:
                teacher.department = get_object_or_404(Department, id=department_id)
            
            teacher.save()
            
            messages.success(request, f'Teacher {teacher.user.get_full_name()} updated successfully!')
            return redirect('admin_teacher_detail', pk=teacher.pk)
            
        except Exception as e:
            messages.error(request, f'Error updating teacher: {str(e)}')
    
    departments = Department.objects.all()
    context = {
        'teacher': teacher,
        'departments': departments,
    }
    
    return render(request, 'core/admin_management/admin_teacher_edit.html', context)


@login_required
@user_passes_test(is_admin)
def admin_teacher_delete(request, pk):
    """Delete teacher"""
    teacher = get_object_or_404(FacultyProfile, pk=pk)
    
    if request.method == 'POST':
        teacher_name = teacher.user.get_full_name()
        user = teacher.user
        teacher.delete()
        user.delete()
        
        messages.success(request, f'Teacher {teacher_name} deleted successfully!')
        return redirect('admin_teacher_list')
    
    context = {
        'teacher': teacher,
    }
    
    return render(request, 'core/admin_management/admin_teacher_delete.html', context)

@login_required
@user_passes_test(is_admin)
def admin_teacher_create(request):
    """Create a new teacher"""
    if request.method == 'POST':
        try:
            # Get form data
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            employee_id = request.POST.get('employee_id')
            department_id = request.POST.get('department')
            specialization = request.POST.get('specialization')
            qualification = request.POST.get('qualification', '')
            experience_years = request.POST.get('experience_years', 0)
            phone = request.POST.get('phone', '')
            
            # Validate required fields
            if not all([first_name, last_name, username, email, password, employee_id, 
                       department_id, specialization]):
                messages.error(request, 'Please fill in all required fields.', extra_tags='error')
                return redirect('admin_student_list')
            
            # Check if username already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists. Please choose a different username.', extra_tags='error')
                return redirect('admin_student_list')
            
            # Check if email already exists
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists. Please use a different email.', extra_tags='error')
                return redirect('admin_student_list')
            
            # Check if employee ID already exists
            if FacultyProfile.objects.filter(employee_id=employee_id).exists():
                messages.error(request, 'Employee ID already exists. Please use a different employee ID.', extra_tags='error')
                return redirect('admin_student_list')
            
            # Get department
            department = get_object_or_404(Department, id=department_id)
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role='teacher',
                is_active=True
            )
            
            # Create teacher profile
            teacher = FacultyProfile.objects.create(
                user=user,
                employee_id=employee_id,
                department=department,
                specialization=specialization,
                qualification=qualification,
                experience_years=int(experience_years),
                phone=phone
            )
            
            messages.success(request, f'Teacher {teacher.user.get_full_name()} has been successfully created!', extra_tags='success')
            return redirect('admin_student_list')
            
        except Exception as e:
            messages.error(request, f'Error creating teacher: {str(e)}', extra_tags='error')
            return redirect('admin_student_list')
    
    # If GET request, redirect to admin dashboard
    return redirect('admin_student_list')

class TeacherDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = FacultyProfile
    template_name = 'core/admin_management/admin_teacher_detail.html'
    context_object_name = 'teacher'
    
    def test_func(self):
        return is_admin(self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.get_object()
        
        # Get courses taught by this teacher
        courses_taught = Course.objects.filter(department=teacher.department)
        context['courses_taught'] = courses_taught
        
        context['title'] = f'Teacher Details: {teacher.user.get_full_name()}'
        return context

class TeacherUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'core/admin_management/admin_teacher_edit.html'
    success_url = reverse_lazy('admin_teacher_list')
    
    def test_func(self):
        return is_admin(self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Teacher'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Teacher information updated successfully!')
        return super().form_valid(form)

class TeacherDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = User
    template_name = 'core/admin_management/admin_teacher_delete.html'
    success_url = reverse_lazy('admin_teacher_list')
    
    def test_func(self):
        return is_admin(self.request.user)
    
    def delete(self, request, *args, **kwargs):
        teacher = self.get_object()
        messages.success(request, f'Teacher {teacher.get_full_name()} deleted successfully!')
        return super().delete(request, *args, **kwargs)

# ======================
# Student CRUD Views
# ======================

@login_required
@user_passes_test(is_admin)
def admin_student_create(request):
    """Create a new student"""
    if request.method == 'POST':
        try:
            # Get form data
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            roll_number = request.POST.get('roll_number')
            department_id = request.POST.get('department')
            admission_year = request.POST.get('admission_year')
            current_form = request.POST.get('current_form')
            current_semester = request.POST.get('current_semester')
            phone = request.POST.get('phone')
            address = request.POST.get('address')
            
            # Validate required fields
            if not all([first_name, last_name, username, email, password, roll_number, department_id]):
                messages.error(request, 'Please fill in all required fields.', extra_tags='error')
                return redirect('admin_student_list')
            
            # Check if username already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists. Please choose a different username.', extra_tags='error')
                return redirect('admin_student_list')
            
            # Check if email already exists
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists. Please use a different email.', extra_tags='error')
                return redirect('admin_student_list')
            
            # Check if roll number already exists
            if StudentProfile.objects.filter(roll_number=roll_number).exists():
                messages.error(request, 'Roll number already exists. Please use a different roll number.', extra_tags='error')
                return redirect('admin_student_list')
            
            # Get department
            try:
                department = Department.objects.get(id=department_id)
            except Department.DoesNotExist:
                messages.error(request, 'Invalid department selected.', extra_tags='error')
                return redirect('admin_student_list')
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role='student',
                is_active=True
            )
            
            # Create student profile
            student = StudentProfile.objects.create(
                user=user,
                roll_number=roll_number,
                department=department,
                admission_year=admission_year,
                current_form=current_form,
                current_semester=current_semester,
                phone=phone,
                address=address
            )
            
            messages.success(request, f'Student {user.get_full_name()} has been successfully created!', extra_tags='success')
            return redirect('admin_student_list')
            
        except Exception as e:
            messages.error(request, f'Error creating student: {str(e)}', extra_tags='error')
            return redirect('admin_student_list')
    
    return redirect('admin_student_list')

class StudentDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = StudentProfile
    template_name = 'core/admin_management/admin_student_detail.html'
    context_object_name = 'student'
    
    def test_func(self):
        return is_admin(self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.get_object()
        
        # Get student enrollments
        enrollments = Enrollment.objects.filter(student=student).select_related('course_offering__course')
        context['enrollments'] = enrollments
        
        # Get student grades
        grades = Grade.objects.filter(student=student).select_related('course_offering__course')
        context['grades'] = grades
        
        # Get student fees
        fees = Fee.objects.filter(student=student).order_by('-due_date')
        context['fees'] = fees
        
        context['title'] = f'Student Details: {student.user.get_full_name()}'
        return context

class StudentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = StudentProfile
    form_class = StudentProfileForm
    template_name = 'core/admin_management/admin_student_edit.html'
    success_url = reverse_lazy('admin_dashboard')
    
    def test_func(self):
        return is_admin(self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Student'
        context['user_form'] = UserUpdateForm(instance=self.get_object().user)
        return context
    
    def form_valid(self, form):
        # Also update user information
        user_form = UserUpdateForm(self.request.POST, instance=self.get_object().user)
        if user_form.is_valid():
            user_form.save()
        
        messages.success(self.request, 'Student information updated successfully!')
        return super().form_valid(form)

class StudentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = User
    template_name = 'core/admin_management/admin_student_delete.html'
    success_url = reverse_lazy('admin_dashboard')
    
    def test_func(self):
        return is_admin(self.request.user)
    
    def get_object(self):
        # Get the user associated with the student profile
        student_id = self.kwargs['pk']
        try:
            student = StudentProfile.objects.get(id=student_id)
            return student.user
        except StudentProfile.DoesNotExist:
            return None
    
    def delete(self, request, *args, **kwargs):
        student_user = self.get_object()
        if student_user:
            messages.success(request, f'Student {student_user.get_full_name()} deleted successfully!')
        return super().delete(request, *args, **kwargs)

# ======================
# Fee Management Views
# ======================

class FeeListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Fee
    template_name = 'core/admin_management/admin_fees.html'
    context_object_name = 'fees'
    paginate_by = 25
    
    def test_func(self):
        return is_admin(self.request.user)
    
    def get_queryset(self):
        queryset = Fee.objects.select_related('student__user').order_by('-due_date')
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(student__user__first_name__icontains=search_query) |
                Q(student__user__last_name__icontains=search_query) |
                Q(student__roll_number__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Filter by status
        status_filter = self.request.GET.get('status', '')
        if status_filter == 'paid':
            queryset = queryset.filter(is_paid=True)
        elif status_filter == 'pending':
            queryset = queryset.filter(is_paid=False, due_date__gte=timezone.now().date())
        elif status_filter == 'overdue':
            queryset = queryset.filter(is_paid=False, due_date__lt=timezone.now().date())
        
        # Filter by student
        student_filter = self.request.GET.get('student', '')
        if student_filter:
            queryset = queryset.filter(student__id=student_filter)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calculate fee statistics
        total_fees = Fee.objects.count()
        paid_fees = Fee.objects.filter(is_paid=True).count()
        pending_fees = Fee.objects.filter(is_paid=False, due_date__gte=timezone.now().date()).count()
        overdue_fees = Fee.objects.filter(is_paid=False, due_date__lt=timezone.now().date()).count()
        
        # Calculate total amounts
        from django.db.models import Sum
        total_collected = Fee.objects.filter(is_paid=True).aggregate(total=Sum('amount'))['total'] or 0
        total_pending = Fee.objects.filter(is_paid=False).aggregate(total=Sum('amount'))['total'] or 0
        total_overdue = Fee.objects.filter(is_paid=False, due_date__lt=timezone.now().date()).aggregate(total=Sum('amount'))['total'] or 0
        
        # Get students for filter dropdown
        students = StudentProfile.objects.select_related('user').all()
        
        context.update({
            'title': 'Fee Management',
            'total_fees': total_fees,
            'paid_fees': paid_fees,
            'pending_fees': pending_fees,
            'overdue_fees': overdue_fees,
            'total_collected': total_collected,
            'total_pending': total_pending,
            'total_overdue': total_overdue,
            'students': students,
        })
        
        return context

class FeeCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Fee
    form_class = FeeForm
    template_name = 'core/admin_management/admin_fee_create.html'
    success_url = reverse_lazy('admin_fee_list')
    
    def test_func(self):
        return is_admin(self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Fee'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Fee created successfully!')
        return super().form_valid(form)

class FeeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Fee
    form_class = FeeForm
    template_name = 'core/admin_management/admin_fee_edit.html'
    success_url = reverse_lazy('admin_fee_list')
    
    def test_func(self):
        return is_admin(self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Fee'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Fee updated successfully!')
        return super().form_valid(form)

class FeeDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Fee
    template_name = 'core/admin_management/admin_fee_delete.html'
    success_url = reverse_lazy('admin_fee_list')
    
    def test_func(self):
        return is_admin(self.request.user)
    
    def delete(self, request, *args, **kwargs):
        fee = self.get_object()
        messages.success(request, f'Fee for {fee.student.user.get_full_name()} deleted successfully!')
        return super().delete(request, *args, **kwargs)

class BaseRegisterView(CreateView):
    from .forms import UserForm, StudentProfileForm, FeeForm
    
    model = User
    form_class = UserForm
    template_name = 'core/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password1'])
        user.save()
        self.create_profile(user)
        messages.success(self.request, f"{self.user_type.capitalize()} registration successful!")
        return super().form_valid(form)

    def create_profile(self, user):
        raise NotImplementedError

class RegisterStudentView(BaseRegisterView):
    template_name = 'core/register_student.html'
    user_type = 'student'

    def create_profile(self, user):
        user.is_student = True
        user.save()
        StudentProfile.objects.create(user=user)

class RegisterFacultyView(BaseRegisterView):
    template_name = 'core/register_faculty.html'
    user_type = 'faculty'

    def create_profile(self, user):
        user.is_faculty = True
        user.save()
        FacultyProfile.objects.create(user=user)

# ======================
# User Management Views
# ======================
class UserManagementView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = 'core/user_management.html'
    context_object_name = 'users'
    paginate_by = 10

    def test_func(self):
        return is_admin(self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(username__icontains=query) |
                Q(email__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query)
            )  # Added missing parenthesis here
        return queryset

def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['pending_users'] = User.objects.filter(is_active=False).count()  # Added .count() for better performance
    return context

@login_required
def add_user(request):
    if not is_admin(request.user):
        messages.error(request, "You don't have permission to add users.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create appropriate profile based on role
            if user.role == 'student':
                from .models import Department
                # Get or create a default department for O-level students
                department, created = Department.objects.get_or_create(
                    code='GEN',
                    defaults={'name': 'General Studies', 'education_level': 'olevel'}
                )
                StudentProfile.objects.create(
                    user=user,
                    roll_number=f"STU{user.id:06d}",
                    admission_year=timezone.now().year,
                    current_form=1,
                    department=department
                )
                messages.success(request, f"Student {user.username} created successfully!")
                
            elif user.role == 'teacher':
                # Create faculty profile (admin will complete details)
                from .models import Department
                department, created = Department.objects.get_or_create(
                    code='GEN',
                    defaults={'name': 'General Studies', 'education_level': 'olevel'}
                )
                FacultyProfile.objects.create(
                    user=user,
                    department=department,
                    designation='lecturer'
                )
                messages.success(request, f"Teacher {user.username} created successfully!")
                
            elif user.role == 'headmaster':
                # Create headmaster profile
                HeadmasterProfile.objects.create(
                    user=user,
                    appointment_date=timezone.now().date()
                )
                messages.success(request, f"Headmaster {user.username} created successfully!")
                
            elif user.role == 'admin':
                # Create admin profile
                from .models import Department
                department, created = Department.objects.get_or_create(
                    code='GEN',
                    defaults={'name': 'General Studies', 'education_level': 'olevel'}
                )
                AdminProfile.objects.create(
                    user=user,
                    department=department,
                    access_level='regular'
                )
                messages.success(request, f"Admin {user.username} created successfully!")
                
            else:
                messages.success(request, f"User {user.username} created successfully!")
            
            return redirect('user_list')
        messages.error(request, "Please correct the errors below.")
    else:
        form = UserForm()
    
    context = {
        'form': form,
        'title': 'Add New User',
        'user_roles': User.ROLE_CHOICES
    }
    return render(request, 'core/admin_management/admin_add_user.html', context)

class UserDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = User
    template_name = 'core/user_detail.html'
    context_object_name = 'user'

    def test_func(self):
        return is_admin(self.request.user)

class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    from .forms import UserUpdateForm
    
    model = User
    form_class = UserUpdateForm
    template_name = 'core/user_management/edit_user.html'
    success_url = reverse_lazy('admin_dashboard')

    def test_func(self):
        return is_admin(self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, f'User "{form.instance.get_full_name()}" has been updated successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Failed to update user. Please check the form for errors.')
        return super().form_invalid(form)

@login_required
def deactivate_user(request, user_id):
    if not is_admin(request.user):
        messages.error(request, "Permission denied")
        return redirect('dashboard')
    
    user = get_object_or_404(User, pk=user_id)
    user.is_active = False
    user.save()
    messages.success(request, f"User {user.username} deactivated")
    return redirect('user_management')

@login_required
def activate_user(request, user_id):
    if not is_admin(request.user):
        messages.error(request, "Permission denied")
        return redirect('dashboard')
    
    user = get_object_or_404(User, pk=user_id)
    user.is_active = True
    user.save()
    messages.success(request, f"User {user.username} activated")
    return redirect('user_management')

# ======================
# Course Management Views
# ======================
class CourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'core/course_management/course_list.html'
    context_object_name = 'courses'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        if is_faculty(self.request.user):
            try:
                faculty_profile = self.request.user.faculty_profile
                queryset = queryset.filter(
                    Q(courseoffering__faculty=faculty_profile) | 
                    Q(department=faculty_profile.department)
                ).distinct()
            except FacultyProfile.DoesNotExist:
                queryset = Course.objects.none()
        elif is_student(self.request.user):
            student = self.request.user.student_profile
            queryset = queryset.filter(enrollments__student=student)
        return queryset

class CourseDetailView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'core/course_management/course_detail.html'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enrollments'] = Enrollment.objects.filter(
            course_offering__course=self.object
        ).select_related('student__user')
        
        if is_student(self.request.user):
            context['is_enrolled'] = Enrollment.objects.filter(
                student=self.request.user.student_profile,
                course_offering__course=self.object
            ).exists()
        
        if is_faculty(self.request.user):
            context['materials'] = Material.objects.filter(course=self.object)
        
        return context


class CreateCourseView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Course
    from .forms import CourseForm
    form_class = CourseForm
    template_name = 'core/course_management/course_form.html'
    success_url = reverse_lazy('subjects_management')

    def test_func(self):
        return is_admin(self.request.user)
        
class CourseUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Course
    from .forms import CourseForm
    form_class = CourseForm
    template_name = 'core/course_management/course_form.html'
    success_url = reverse_lazy('subjects_management')

    def test_func(self):
        return is_admin(self.request.user)


class CourseDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Course
    template_name = 'core/course_management/course_confirm_delete.html'
    success_url = reverse_lazy('course_list')

    def test_func(self):
        return is_admin(self.request.user)

# ======================
# Student Views
# ======================

@login_required
@user_passes_test(is_student)
def student_courses(request):
    """Student courses page"""
    try:
        student = request.user.student_profile
    except StudentProfile.DoesNotExist:
        return redirect('student_dashboard')
    
    # Get student enrollments with related data
    enrollments = Enrollment.objects.filter(
        student=student
    ).select_related(
        'course_offering__course',
        'course_offering__faculty',
        'course_offering__semester'
    ).prefetch_related('attendances')
    
    # Calculate attendance percentages
    enriched_enrollments = []
    total_attendance = 0
    for enrollment in enrollments:
        total_classes = enrollment.attendances.count()
        present_classes = enrollment.attendances.filter(status='P').count()
        attendance_percentage = (present_classes / total_classes * 100) if total_classes > 0 else 0
        
        total_attendance += attendance_percentage
        
        enriched_enrollments.append({
            'enrollment': enrollment,
            'attendance_percentage': attendance_percentage,
            'grade': getattr(enrollment, 'grade', None)
        })
    
    # Calculate average attendance
    average_attendance = total_attendance / len(enrollments) if enrollments else 0
    
    # Get available courses for enrollment
    available_courses = []
    current_semester = Semester.objects.filter(is_current=True).first()
    if current_semester:
        enrolled_course_ids = enrollments.values_list('course_offering__course__id', flat=True)
        available_courses = CourseOffering.objects.filter(
            semester=current_semester
        ).exclude(
            course__id__in=enrolled_course_ids
        ).select_related('course', 'faculty').order_by('course__name')
    
    context = {
        'student': student,
        'enrollments': enriched_enrollments,
        'average_attendance': average_attendance,
        'available_courses': available_courses,
        'current_semester': current_semester,
    }
    
    return render(request, 'core/student_parts/courses.html', context)

@login_required
@user_passes_test(is_student)
def student_results(request):
    """Student academic results page"""
    try:
        student = request.user.student_profile
    except StudentProfile.DoesNotExist:
        return redirect('student_dashboard')
    
    # Get NECTA exam results
    necta_exams = NECTAExam.objects.filter(student=student).order_by('-exam_year', '-exam_month')
    
    # Calculate performance statistics
    total_exams = necta_exams.count()
    average_grade = 0
    best_grade = 'N/A'
    pass_rate = 0
    
    if total_exams > 0:
        total_points = sum(exam.get_grade_points() for exam in necta_exams)
        average_grade = total_points / total_exams
        
        # Calculate best grade
        grade_points = [exam.get_grade_points() for exam in necta_exams]
        if grade_points:
            best_grade = max(grade_points)
            # Convert points back to grade
            if best_grade >= 4:
                best_grade = 'A'
            elif best_grade >= 3:
                best_grade = 'B'
            elif best_grade >= 2:
                best_grade = 'C'
            elif best_grade >= 1:
                best_grade = 'D'
            else:
                best_grade = 'F'
        
        # Calculate pass rate (assuming A, B, C, D are passes)
        passing_grades = sum(1 for exam in necta_exams if exam.get_grade_points() >= 1)
        pass_rate = (passing_grades / total_exams) * 100
    
    # Group exams by subject for performance analysis
    subject_performance = {}
    for exam in necta_exams:
        subject_name = exam.get_subject_display()
        if subject_name not in subject_performance:
            subject_performance[subject_name] = {
                'exams': [],
                'total_score': 0,
                'total_points': 0,
                'best_grade': 'N/A',
                'pass_rate': 0
            }
        
        subject_performance[subject_name]['exams'].append(exam)
        subject_performance[subject_name]['total_score'] += exam.score or 0
        subject_performance[subject_name]['total_points'] += exam.get_grade_points()
    
    # Calculate subject-wise statistics
    for subject_name, data in subject_performance.items():
        exams = data['exams']
        if exams:
            # Average score
            data['average_score'] = data['total_score'] / len(exams)
            
            # Average grade points
            data['average_grade_points'] = data['total_points'] / len(exams)
            
            # Best grade for this subject
            subject_points = [exam.get_grade_points() for exam in exams]
            best_points = max(subject_points)
            if best_points >= 4:
                data['best_grade'] = 'A'
            elif best_points >= 3:
                data['best_grade'] = 'B'
            elif best_points >= 2:
                data['best_grade'] = 'C'
            elif best_points >= 1:
                data['best_grade'] = 'D'
            else:
                data['best_grade'] = 'F'
            
            # Pass rate for this subject
            passing_count = sum(1 for exam in exams if exam.get_grade_points() >= 1)
            data['pass_rate'] = (passing_count / len(exams)) * 100
            
            data['total_assessments'] = len(exams)
    
    # Get regular grades from enrollments
    enrollment_grades = Grade.objects.filter(
        enrollment__student=student
    ).select_related('enrollment__course_offering__course').order_by('-awarded_on')
    
    context = {
        'student': student,
        'necta_results': necta_exams,
        'enrollment_grades': enrollment_grades,
        'total_exams': total_exams,
        'average_grade': average_grade,
        'best_grade': best_grade,
        'pass_rate': round(pass_rate, 1),
        'subject_performance': subject_performance,
    }
    
    return render(request, 'core/student_parts/results.html', context)

@login_required
@user_passes_test(is_student)
def student_timetable(request):
    """Student timetable page with robust filtering"""
    try:
        student = request.user.student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('student_dashboard')
    
    # Get current semester
    current_semester = Semester.objects.filter(is_current=True).first()
    if not current_semester:
        current_semester = Semester.objects.all().order_by('-id').first()
    
    # Get student's enrolled courses
    enrollments = Enrollment.objects.filter(
        student=student
    ).select_related('course_offering__course')
    
    course_ids = enrollments.values_list('course_offering__course__id', flat=True)
    
    # Get timetable entries for student's courses in current semester
    # We filter by course_id to catch all offerings of that course the student might be in
    timetable_entries = TimeTable.objects.filter(
        course_offering__course__id__in=course_ids,
        semester=current_semester
    ).select_related('course_offering__course', 'course_offering__faculty').order_by('day', 'start_time')
    
    context = {
        'title': 'My Weekly Timetable',
        'current_semester': current_semester,
        'schedules': timetable_entries,
        'days': [day[0] for day in TimeTable.DAY_CHOICES],
        'school_info': get_school_info(),
    }
    
    return render(request, 'core/student_parts/timetable.html', context)

# Removed duplicate StudentDashboardView


@login_required
@user_passes_test(is_student)
def student_assignments(request):
    """Student assignments page"""
    try:
        student = request.user.student_profile
    except StudentProfile.DoesNotExist:
        return redirect('student_dashboard')
    
    # Get student's enrollments
    enrollments = Enrollment.objects.filter(student=student).select_related('course_offering__course')
    
    # Get assignments for student's courses
    course_offering_ids = enrollments.values_list('course_offering__id', flat=True)
    assignments = Assignment.objects.filter(
        course_offering__id__in=course_offering_ids
    ).select_related('course_offering__course').order_by('-created_at')
    
    # Get student's submissions
    submissions = {}
    for assignment in assignments:
        try:
            submission = Submission.objects.get(assignment=assignment, student=student)
            submissions[assignment.id] = submission
        except Submission.DoesNotExist:
            submissions[assignment.id] = None
    
    # Calculate statistics
    submitted_count = len([s for s in submissions.values() if s is not None])
    pending_count = len(assignments) - submitted_count
    
    # Calculate overdue assignments
    now = timezone.now()
    overdue_count = 0
    for assignment in assignments:
        if assignment.due_date and assignment.due_date < now:
            submission = submissions.get(assignment.id)
            if not submission:
                overdue_count += 1
    
    # Add helper methods to assignment objects
    for assignment in assignments:
        assignment.is_overdue = assignment.due_date and assignment.due_date < now
        assignment.is_due_soon = assignment.due_date and (assignment.due_date - now).days <= 3
        assignment.get_status_display = lambda: 'Submitted' if assignment.id in submissions and submissions[assignment.id] else 'Not Submitted'
        
        # Add grade display method to submissions
        if assignment.id in submissions and submissions[assignment.id]:
            submission = submissions[assignment.id]
            if submission.marks_obtained is not None:
                # Calculate percentage
                submission.score_percentage = (submission.marks_obtained / assignment.max_marks) * 100 if assignment.max_marks > 0 else 0
                
                if submission.score_percentage >= 80:
                    grade_display = 'Excellent'
                elif submission.score_percentage >= 60:
                    grade_display = 'Good'
                elif submission.score_percentage >= 40:
                    grade_display = 'Satisfactory'
                else:
                    grade_display = 'Needs Improvement'
                submission.get_grade_display = grade_display
            else:
                submission.get_grade_display = 'Not Graded'
    
    context = {
        'student': student,
        'assignments': assignments,
        'submissions': submissions,
        'submitted_count': submitted_count,
        'pending_count': pending_count,
        'overdue_count': overdue_count,
        'school_info': get_school_info(),
    }
    
    return render(request, 'core/student_parts/assignments.html', context)

@login_required
@user_passes_test(is_student)
def student_exams(request):
    """Student exams page"""
    try:
        student = request.user.student_profile
    except StudentProfile.DoesNotExist:
        return redirect('student_dashboard')
    
    # Get student's enrollments
    enrollments = Enrollment.objects.filter(student=student).select_related('course_offering__course')
    
    # Get upcoming exams for student's courses
    course_offerings = enrollments.values_list('course_offering__course__id', flat=True)
    upcoming_exams = ExamSchedule.objects.filter(
        course__id__in=course_offerings,
        date__gte=timezone.now().date()
    ).select_related('course').order_by('date', 'start_time')
    
    # Get past exams
    past_exams = ExamSchedule.objects.filter(
        course__id__in=course_offerings,
        date__lt=timezone.now().date()
    ).select_related('course').order_by('-date', '-start_time')[:10]
    
    # Calculate exam statistics
    total_exams = upcoming_exams.count() + past_exams.count()
    upcoming_count = upcoming_exams.count()
    past_count = past_exams.count()
    
    # Calculate exam distribution by type
    exam_types = {}
    for exam in upcoming_exams:
        exam_types[exam.exam_type] = exam_types.get(exam.exam_type, 0) + 1
    for exam in past_exams:
        exam_types[exam.exam_type] = exam_types.get(exam.exam_type, 0) + 1
    
    # Add helper methods to exam objects
    today = timezone.now().date()
    tomorrow = today + timezone.timedelta(days=1)
    
    for exam in upcoming_exams:
        days_until = (exam.date - today).days
        exam.days_until = days_until
        exam.is_today = exam.date == today
        exam.is_tomorrow = exam.date == tomorrow
        exam.is_urgent = days_until <= 3
        
        # Add status display method
        if exam.date == today:
            exam.status_display = 'Exam Day'
            exam.status_class = 'danger'
        elif days_until <= 3:
            exam.status_display = 'Soon'
            exam.status_class = 'warning'
        else:
            exam.status_display = 'Scheduled'
            exam.status_class = 'success'
    
    for exam in past_exams:
        days_ago = (today - exam.date).days
        exam.days_ago = days_ago
        exam.status_display = 'Completed'
        exam.status_class = 'success'
    
    context = {
        'student': student,
        'upcoming_exams': upcoming_exams,
        'past_exams': past_exams,
        'total_exams': total_exams,
        'upcoming_count': upcoming_count,
        'past_count': past_count,
        'exam_types': exam_types,
        'today': today,
        'tomorrow': tomorrow,
    }
    
    return render(request, 'core/student_parts/exams.html', context)

@login_required
@user_passes_test(is_student)
def student_library(request):
    """Student library page"""
    try:
        student = request.user.student_profile
    except StudentProfile.DoesNotExist:
        return redirect('student_dashboard')
    
    # Get currently borrowed books
    borrowed_books = BorrowedBook.objects.filter(
        student=student,
        return_date__isnull=True
    ).select_related('book').order_by('due_date')
    
    # Get borrowing history
    borrowing_history = BorrowedBook.objects.filter(
        student=student
    ).select_related('book').order_by('-issue_date')[:20]
    
    # Calculate overdue books
    overdue_books = borrowed_books.filter(due_date__lt=timezone.now().date())
    
    # Get available books for browsing
    available_books = Book.objects.filter(
        available_copies__gt=0
    ).order_by('title')
    
    # Get popular books (most borrowed)
    popular_books = Book.objects.annotate(
        borrow_count=Count('borrowedbook')
    ).order_by('-borrow_count')[:10]
    
    # Get books by category
    categories = Book.objects.values('category').annotate(
        count=Count('id')
    ).order_by('category')
    
    # Calculate library statistics
    total_borrowed = borrowing_history.count()
    total_overdue = overdue_books.count()
    currently_borrowed = borrowed_books.count()
    
    # Add helper methods to borrowed books
    for borrowed_book in borrowed_books:
        borrowed_book.days_until_due = (borrowed_book.due_date - timezone.now().date()).days
        borrowed_book.is_overdue = borrowed_book.due_date < timezone.now().date()
        borrowed_book.days_overdue = (timezone.now().date() - borrowed_book.due_date).days if borrowed_book.is_overdue else 0
        
        # Status display
        if borrowed_book.is_overdue:
            borrowed_book.status_display = 'Overdue'
            borrowed_book.status_class = 'danger'
        elif borrowed_book.days_until_due <= 3:
            borrowed_book.status_display = 'Due Soon'
            borrowed_book.status_class = 'warning'
        else:
            borrowed_book.status_display = 'Borrowed'
            borrowed_book.status_class = 'info'
    
    # Add helper methods to history books
    for history_book in borrowing_history:
        history_book.is_returned = history_book.return_date is not None
        if history_book.is_returned:
            history_book.status_display = 'Returned'
            history_book.status_class = 'success'
        else:
            history_book.status_display = 'Borrowed'
            history_book.status_class = 'info'
    
    context = {
        'student': student,
        'borrowed_books': borrowed_books,
        'borrowing_history': borrowing_history,
        'overdue_books': overdue_books,
        'available_books': available_books,
        'popular_books': popular_books,
        'categories': categories,
        'total_borrowed': total_borrowed,
        'total_overdue': total_overdue,
        'currently_borrowed': currently_borrowed,
    }
    
    return render(request, 'core/student_parts/library.html', context)

@login_required
@user_passes_test(is_student)
def student_achievements(request):
    """Student achievements page"""
    try:
        student = request.user.student_profile
    except StudentProfile.DoesNotExist:
        return redirect('student_dashboard')
    
    # Get student achievements
    achievements = Achievement.objects.filter(student=student).order_by('-date_awarded')
    
    # Get activity participation
    participations = Participation.objects.filter(
        student=student
    ).select_related('activity').order_by('-registered_on')
    
    # Calculate achievement statistics
    total_achievements = achievements.count()
    total_participations = participations.count()
    attended_activities = participations.filter(attended=True).count()
    
    # Group achievements by year
    achievements_by_year = {}
    for achievement in achievements:
        year = achievement.date_awarded.year
        if year not in achievements_by_year:
            achievements_by_year[year] = []
        achievements_by_year[year].append(achievement)
    
    # Group participations by activity type
    participations_by_type = {}
    max_participation_count = 0
    for participation in participations:
        activity_type = participation.activity.activity_type
        if activity_type not in participations_by_type:
            participations_by_type[activity_type] = []
        participations_by_type[activity_type].append(participation)
        # Track max for percentage calculation
        if len(participations_by_type[activity_type]) > max_participation_count:
            max_participation_count = len(participations_by_type[activity_type])
    
    # Add percentage data for progress bars
    for activity_type, type_participations in participations_by_type.items():
        participations_by_type[activity_type] = {
            'participations': type_participations,
            'count': len(type_participations),
            'percentage': (len(type_participations) / max_participation_count * 100) if max_participation_count > 0 else 0
        }
    
    # Calculate attendance rate
    attendance_rate = 0
    if total_participations > 0:
        attendance_rate = round((attended_activities / total_participations) * 100, 1)
    
    # Add helper methods to achievements
    for achievement in achievements:
        achievement.years_ago = (timezone.now().date().year - achievement.date_awarded.year)
        achievement.is_recent = achievement.date_awarded.year >= timezone.now().date().year - 1
    
    # Add helper methods to participations
    for participation in participations:
        participation.days_since_registered = (timezone.now().date() - participation.registered_on.date()).days
        participation.is_recent = participation.registered_on.date() >= timezone.now().date() - timezone.timedelta(days=30)
        participation.attendance_status = 'Attended' if participation.attended else 'Not Attended'
        participation.attendance_class = 'success' if participation.attended else 'warning'
    
    context = {
        'student': student,
        'achievements': achievements,
        'participations': participations,
        'achievements_by_year': achievements_by_year,
        'participations_by_type': participations_by_type,
        'total_achievements': total_achievements,
        'total_participations': total_participations,
        'attended_activities': attended_activities,
        'attendance_rate': attendance_rate,
    }
    
    return render(request, 'core/student_parts/achievements.html', context)

@login_required
@user_passes_test(is_student)
def student_fees(request):
    """Student fees page"""
    try:
        student = request.user.student_profile
    except StudentProfile.DoesNotExist:
        return redirect('student_dashboard')
    
    # Get all fees for student
    fees = Fee.objects.filter(student=student).order_by('-due_date')
    
    # Calculate fee statistics
    total_fees = fees.aggregate(total=DBSum('amount'))['total'] or 0
    paid_fees = fees.filter(is_paid=True).aggregate(total=DBSum('amount'))['total'] or 0
    outstanding_fees = fees.filter(is_paid=False).aggregate(total=DBSum('amount'))['total'] or 0
    overdue_fees = fees.filter(is_paid=False, due_date__lt=timezone.now().date())
    
    # Get payment history
    payments = Payment.objects.filter(student=student).order_by('-payment_date')[:10]
    
    # Group fees by category
    fees_by_category = {}
    for fee in fees:
        if fee.category not in fees_by_category:
            fees_by_category[fee.category] = {
                'fees': [],
                'total': 0,
                'count': 0,
                'percentage': 0
            }
        fees_by_category[fee.category]['fees'].append(fee)
        fees_by_category[fee.category]['total'] += float(fee.amount)
        fees_by_category[fee.category]['count'] += 1
    
    # Group fees by semester
    fees_by_semester = {}
    for fee in fees:
        if fee.semester not in fees_by_semester:
            fees_by_semester[fee.semester] = {
                'fees': [],
                'total': 0,
                'count': 0,
                'percentage': 0
            }
        fees_by_semester[fee.semester]['fees'].append(fee)
        fees_by_semester[fee.semester]['total'] += float(fee.amount)
        fees_by_semester[fee.semester]['count'] += 1
    
    # Calculate percentages
    if total_fees > 0:
        for category, data in fees_by_category.items():
            data['percentage'] = (data['total'] / total_fees) * 100
        
        for semester, data in fees_by_semester.items():
            data['percentage'] = (data['total'] / total_fees) * 100
    
    # Calculate payment statistics
    total_payments = payments.aggregate(total=DBSum('amount'))['total'] or 0
    payment_count = payments.count()
    
    # Add helper methods to fees
    for fee in fees:
        fee.days_until_due = (fee.due_date - timezone.now().date()).days
        fee.is_overdue = fee.due_date < timezone.now().date() and not fee.is_paid
        fee.is_due_soon = fee.due_date >= timezone.now().date() and (fee.due_date - timezone.now().date()).days <= 7 and not fee.is_paid
        
        # Calculate days overdue if overdue
        if fee.is_overdue:
            fee.days_overdue = abs((timezone.now().date() - fee.due_date).days)
        else:
            fee.days_overdue = 0
        
        # Status display
        if fee.is_paid:
            fee.status_display = 'Paid'
            fee.status_class = 'success'
        elif fee.is_overdue:
            fee.status_display = 'Overdue'
            fee.status_class = 'danger'
        elif fee.is_due_soon:
            fee.status_display = 'Due Soon'
            fee.status_class = 'warning'
        else:
            fee.status_display = 'Pending'
            fee.status_class = 'info'
    
    # Add helper methods to payments
    for payment in payments:
        payment.days_ago = (timezone.now().date() - payment.payment_date.date()).days
        payment.is_recent = payment.payment_date.date() >= timezone.now().date() - timezone.timedelta(days=30)
    
    context = {
        'student': student,
        'fees': fees,
        'fees_by_category': fees_by_category,
        'fees_by_semester': fees_by_semester,
        'total_fees': total_fees,
        'paid_fees': paid_fees,
        'outstanding_fees': outstanding_fees,
        'overdue_count': overdue_fees.count(),
        'payments': payments,
        'total_payments': total_payments,
        'payment_count': payment_count,
    }
    
    return render(request, 'core/student_parts/fees.html', context)

@login_required
@user_passes_test(is_student)
def student_messages(request):
    """Student messages page"""
    try:
        student = request.user.student_profile
    except StudentProfile.DoesNotExist:
        return redirect('student_dashboard')
    
    # Get received messages
    received_messages = Message.objects.filter(
        recipient=request.user
    ).select_related('sender').order_by('-sent_at')
    
    # Get sent messages
    sent_messages = Message.objects.filter(
        sender=request.user
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
        message.sender_role = 'Staff' if message.sender.is_staff else ('Admin' if message.sender.is_superuser else 'User')
    
    for message in sent_messages:
        message.days_ago = (timezone.now().date() - message.sent_at.date()).days
        message.is_recent = message.sent_at.date() >= timezone.now().date() - timezone.timedelta(days=7)
        message.recipient_name = message.recipient.get_full_name() or message.recipient.username
        message.recipient_role = 'Staff' if message.recipient.is_staff else ('Admin' if message.recipient.is_superuser else 'User')
    
    # Get potential recipients (teachers and staff)
    from .models import User
    potential_recipients = User.objects.filter(
        Q(is_staff=True) | Q(is_superuser=True)
    ).exclude(id=request.user.id).order_by('first_name', 'last_name')
    
    # Get current date for template comparisons
    today = timezone.now().date()
    yesterday = today - timezone.timedelta(days=1)
    
    context = {
        'student': student,
        'received_messages': received_messages,
        'sent_messages': sent_messages,
        'unread_count': unread_count,
        'total_messages': total_messages,
        'potential_recipients': potential_recipients,
        'today': today,
        'yesterday': yesterday,
    }
    
    return render(request, 'core/student_parts/messages.html', context)

@login_required
@user_passes_test(is_admin)
def admin_messages(request):
    """Admin messages page"""
    try:
        # Get admin profile (if exists)
        admin_profile = request.user.adminprofile
    except:
        # If no admin profile exists, create a basic one
        admin_profile = None
    
    # Get received messages
    received_messages = Message.objects.filter(
        recipient=request.user
    ).select_related('sender').order_by('-sent_at')
    
    # Get sent messages
    sent_messages = Message.objects.filter(
        sender=request.user
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
        message.sender_role = 'Student' if message.sender.role == 'student' else ('Teacher' if message.sender.role == 'teacher' else ('Headmaster' if message.sender.role == 'headmaster' else 'Admin'))
    
    for message in sent_messages:
        message.days_ago = (timezone.now().date() - message.sent_at.date()).days
        message.is_recent = message.sent_at.date() >= timezone.now().date() - timezone.timedelta(days=7)
        message.recipient_name = message.recipient.get_full_name() or message.recipient.username
        message.recipient_role = 'Student' if message.recipient.role == 'student' else ('Teacher' if message.recipient.role == 'teacher' else ('Headmaster' if message.recipient.role == 'headmaster' else 'Admin'))
    
    # Get potential recipients (all users except self)
    from .models import User
    potential_recipients = User.objects.filter(
        Q(is_staff=True) | Q(is_superuser=True) | Q(role__in=['student', 'teacher', 'headmaster'])
    ).exclude(id=request.user.id).order_by('first_name', 'last_name')
    
    # Get students and teachers for compose modal
    students = StudentProfile.objects.select_related('user').all()
    teachers = FacultyProfile.objects.select_related('user').all()
    
    # Get all messages for the list
    all_messages = received_messages.union(sent_messages).order_by('-sent_at')
    
    # Get current date for template comparisons
    today = timezone.now().date()
    yesterday = today - timezone.timedelta(days=1)
    
    context = {
        'admin': admin_profile,
        'messages': all_messages,
        'received_messages': received_messages,
        'sent_messages': sent_messages,
        'unread_count': unread_count,
        'total_messages': total_messages,
        'students': students,
        'teachers': teachers,
        'potential_recipients': potential_recipients,
        'today': today,
        'yesterday': yesterday,
        'user': request.user,
        'role': 'School Administrator',
    }
    
    return render(request, 'core/admin_management/admin_messages_enhanced.html', context)

@login_required
@user_passes_test(is_student)
def student_announcements(request):
    """Student announcements page"""
    try:
        student = request.user.student_profile
    except StudentProfile.DoesNotExist:
        return redirect('student_dashboard')
    
    # Get announcements for students
    announcements = Announcement.objects.filter(
        Q(target_audience='All') | Q(target_audience='Students')
    ).select_related('created_by').order_by('-created_at')
    
    # Get current date for template comparisons
    today = timezone.now().date()
    yesterday = today - timezone.timedelta(days=1)
    
    context = {
        'student': student,
        'announcements': announcements,
        'today': today,
        'yesterday': yesterday,
    }
    
    return render(request, 'core/announcement_list.html', context)

@login_required
@user_passes_test(is_student)
def student_activities(request):
    """Student activities page"""
    try:
        student = request.user.student_profile
    except StudentProfile.DoesNotExist:
        return redirect('student_dashboard')
    
    # Get upcoming activities
    upcoming_activities = Activity.objects.filter(
        date__gte=timezone.now().date()
    ).order_by('date')
    
    # Get student's participations
    participations = Participation.objects.filter(
        student=student
    ).select_related('activity').order_by('-registered_on')
    
    # Add helper methods to participations
    for participation in participations:
        participation.days_since_registered = (timezone.now().date() - participation.registered_on.date()).days
    
    # Get past activities
    past_activities = Activity.objects.filter(
        date__lt=timezone.now().date()
    ).order_by('-date')[:10]
    
    context = {
        'student': student,
        'upcoming_activities': upcoming_activities,
        'participations': participations,
        'past_activities': past_activities,
    }
    
    return render(request, 'core/student_parts/activities.html', context)

@login_required
@user_passes_test(is_student)
def student_profile_view(request):
    """Student profile page"""
    try:
        student = request.user.student_profile
    except StudentProfile.DoesNotExist:
        return redirect('student_dashboard')
    
    # Get student statistics
    enrollments = Enrollment.objects.filter(student=student).count()
    total_fees = Fee.objects.filter(student=student).aggregate(total=DBSum('amount'))['total'] or 0
    achievements_count = Achievement.objects.filter(student=student).count()
    
    context = {
        'student': student,
        'enrollments_count': enrollments,
        'total_fees': total_fees,
        'achievements_count': achievements_count,
    }
    
    return render(request, 'core/student_parts/profile.html', context)

@login_required
@user_passes_test(is_student)
def student_settings(request):
    """Student settings page"""
    try:
        student = request.user.student_profile
    except StudentProfile.DoesNotExist:
        return redirect('student_dashboard')
    
    if request.method == 'POST':
        # Handle different form submissions
        if 'profile_form' in request.POST:
            # Handle profile update
            user_form = UserUpdateForm(request.POST, instance=request.user)
            profile_form = StudentProfileForm(request.POST, request.FILES, instance=student)
            
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                
                # Handle profile picture upload separately
                if 'profile_picture' in request.FILES:
                    profile_picture = request.FILES['profile_picture']
                    
                    # Validate file type
                    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
                    if profile_picture.content_type not in allowed_types:
                        messages.error(request, 'Invalid file type. Please upload JPEG, PNG, GIF, or WebP images.', extra_tags='error')
                        return redirect('student_settings')
                    
                    # Validate file size (max 5MB)
                    if profile_picture.size > 5 * 1024 * 1024:
                        messages.error(request, 'File too large. Please upload an image smaller than 5MB.', extra_tags='error')
                        return redirect('student_settings')
                    
                    # Save the profile picture
                    profile_form.save()
                    
                    # Log the successful upload
                    print(f"Profile picture uploaded for student {student.roll_number}: {profile_picture.name}")
                    
                    messages.success(request, f'Profile picture "{profile_picture.name}" uploaded successfully!', extra_tags='profile_picture')
                else:
                    profile_form.save()
                    messages.success(request, 'Profile updated successfully!', extra_tags='success')
                
                return redirect('student_settings')
            else:
                # Add specific error messages
                if user_form.errors:
                    for field, errors in user_form.errors.items():
                        for error in errors:
                            messages.error(request, f'{field.replace("_", " ").title()}: {error}', extra_tags='error')
                
                if profile_form.errors:
                    for field, errors in profile_form.errors.items():
                        for error in errors:
                            messages.error(request, f'{field.replace("_", " ").title()}: {error}', extra_tags='error')
        
        elif 'account_form' in request.POST:
            # Handle account settings
            user_form = UserUpdateForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Account settings updated successfully!', extra_tags='success')
                return redirect('student_settings')
            else:
                for field, errors in user_form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field.replace("_", " ").title()}: {error}', extra_tags='error')
        
        elif 'contact_form' in request.POST:
            # Handle contact information update
            profile_form = StudentProfileForm(request.POST, instance=student)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Contact information updated successfully!', extra_tags='success')
                return redirect('student_settings')
            else:
                for field, errors in profile_form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field.replace("_", " ").title()}: {error}', extra_tags='error')
        
        elif 'password_form' in request.POST:
            # Handle password change
            old_password = request.POST.get('old_password')
            new_password1 = request.POST.get('new_password1')
            new_password2 = request.POST.get('new_password2')
            
            if request.user.check_password(old_password):
                if new_password1 == new_password2:
                    if len(new_password1) >= 8:
                        request.user.set_password(new_password1)
                        request.user.save()
                        messages.success(request, 'Password changed successfully!', extra_tags='success')
                        return redirect('student_settings')
                    else:
                        messages.error(request, 'Password must be at least 8 characters long.', extra_tags='error')
                else:
                    messages.error(request, 'New passwords do not match.', extra_tags='error')
            else:
                messages.error(request, 'Current password is incorrect.', extra_tags='error')
    
    # Initialize forms for GET request
    user_form = UserUpdateForm(instance=request.user)
    profile_form = StudentProfileForm(instance=student)
    
    context = {
        'student': student,
        'user_form': user_form,
        'profile_form': profile_form,
    }
    
    return render(request, 'core/student_management/settings_clean.html', context)

class StudentDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'core/student_management/student_dashboard.html'
    
    def test_func(self):
        return is_student(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Check if student has a profile, if not create one
        try:
            student = self.request.user.student_profile
        except StudentProfile.DoesNotExist:
            # Create a StudentProfile for the user
            # Get or create a default department first
            from .models import Department
            department, created = Department.objects.get_or_create(
                code='GEN',
                defaults={'name': 'General Studies', 'slug': 'general-studies'}
            )
            
            student = StudentProfile.objects.create(
                user=self.request.user,
                roll_number=f"STU{self.request.user.id:06d}",
                admission_year=timezone.now().year,
                current_semester=1,
                department=department
            )
        
        # Get enrollments with related data
        enrollments = Enrollment.objects.filter(
            student=student
        ).select_related(
            'course_offering__course',
            'course_offering__faculty'
        ).prefetch_related('attendances')
        
        # Calculate attendance percentages
        enriched_enrollments = []
        total_present = 0
        total_sessions = 0
        for enrollment in enrollments:
            sessions = enrollment.attendances.all()
            total_classes = sessions.count()
            present_classes = sessions.filter(status='P').count()
            attendance_percentage = (present_classes / total_classes * 100) if total_classes > 0 else 0
            
            total_present += present_classes
            total_sessions += total_classes
            
            enriched_enrollments.append({
                'enrollment': enrollment,
                'attendance_percentage': attendance_percentage,
                'grade': getattr(enrollment, 'grade', None)
            })
        
        overall_attendance = (total_present / total_sessions * 100) if total_sessions > 0 else 0

        
        # School Information - Get from database or create default
        try:
            # Try to get school information from system settings
            school_name = SystemSetting.objects.get(key='school_name').value
            school_motto = SystemSetting.objects.get(key='school_motto').value
            school_vision = SystemSetting.objects.get(key='school_vision').value
            school_mission = SystemSetting.objects.get(key='school_mission').value
            school_address = SystemSetting.objects.get(key='school_address').value
            school_phone = SystemSetting.objects.get(key='school_phone').value
            school_email = SystemSetting.objects.get(key='school_email').value
            school_website = SystemSetting.objects.get(key='school_website').value
            school_founded_year = SystemSetting.objects.get(key='school_founded_year').value
            school_type = SystemSetting.objects.get(key='school_type').value
            school_registration = SystemSetting.objects.get(key='school_registration').value
            school_exam_center = SystemSetting.objects.get(key='school_exam_center').value
        except (SystemSetting.DoesNotExist, KeyError):
            # Default values if no settings exist
            school_name = 'Mkalala Secondary School'
            school_motto = 'Education for Excellence'
            school_vision = 'To be a center of academic excellence and moral development'
            school_mission = 'To provide quality education that prepares students for higher education and life challenges'
            school_address = 'P.O. Box 1234, Mkalala, Tanzania'
            school_phone = '+255 123 456 789'
            school_email = 'info@mkalala.sc.tz'
            school_website = 'www.mkalala.sc.tz'
            school_founded_year = '2005'
            school_type = 'O-Level Secondary School'
            school_registration = 'REG.12345/6789'
            school_exam_center = 'CSEE/FTNA Center'
        
        school_info = {
            'name': school_name,
            'motto': school_motto,
            'vision': school_vision,
            'mission': school_mission,
            'address': school_address,
            'phone': school_phone,
            'email': school_email,
            'website': school_website,
            'founded_year': school_founded_year,
            'school_type': school_type,
            'registration_number': school_registration,
            'examination_center': school_exam_center,
        }
        
        # Academic Performance Data
        necta_exams = NECTAExam.objects.filter(student=student).order_by('-exam_year', '-exam_month')
        average_grade = self.calculate_average_grade(necta_exams)
        academic_performance = {
            'total_exams': necta_exams.count(),
            'average_grade': average_grade,
            'best_subject': self.get_best_subject(necta_exams),
            'subjects_taken': necta_exams.values_list('subject', flat=True).distinct().count(),
            'recent_exams': necta_exams[:5],
            'progress_stroke_dasharray': (average_grade + 5) * 31.4,  # Calculate for SVG progress ring
        }
        
        # Fee Information
        fees = Fee.objects.filter(student=student).order_by('-due_date')
        fee_summary = {
            'total_fees': fees.aggregate(total=DBSum('amount'))['total'] or 0,
            'paid_fees': fees.filter(is_paid=True).aggregate(total=DBSum('amount'))['total'] or 0,
            'outstanding_fees': fees.filter(is_paid=False).aggregate(total=DBSum('amount'))['total'] or 0,
            'overdue_fees': fees.filter(is_paid=False, due_date__lt=timezone.now().date()).count(),
            'recent_fees': fees[:5],
        }
        
        # Library Information
        borrowed_books = BorrowedBook.objects.filter(student=student, return_date__isnull=True)
        library_info = {
            'active_borrowed_books': borrowed_books.count(),
            'overdue_books': borrowed_books.filter(due_date__lt=timezone.now().date()).count(),
            'total_borrowed_history': BorrowedBook.objects.filter(student=student).count(),
            'recent_borrowed': borrowed_books[:5],
        }
        
        # Activity Participation
        participations = Participation.objects.filter(student=student).select_related('activity')
        activity_info = {
            'total_activities': participations.count(),
            'attended_activities': participations.filter(attended=True).count(),
            'upcoming_activities': Activity.objects.filter(date__gte=timezone.now())[:5],
            'recent_participations': participations.order_by('-registered_on')[:5],
        }
        
        # Achievements
        achievements = Achievement.objects.filter(student=student).order_by('-date_awarded')
        
        # Messages and Notifications
        unread_messages = Message.objects.filter(recipient=self.request.user, is_read=False).count()
        notifications = Notification.objects.filter(recipient=self.request.user, is_read=False).order_by('-created_at')[:5]
        
        context.update({
            # Student Information
            'student': student,
            'enriched_enrollments': enriched_enrollments,
            'overall_attendance': overall_attendance,
            
            # Assignments
            'recent_assignments': Assignment.objects.filter(
                course_offering__id__in=[e['enrollment'].course_offering_id for e in enriched_enrollments]
            ).select_related('course_offering__course').order_by('-created_at')[:5],
            
            # School Information
            'school_info': school_info,

            
            # Academic Data
            'upcoming_exams': ExamSchedule.objects.filter(
                course__in=[e.course_offering.course for e in enrollments],
                date__gte=timezone.now()
            ).order_by('date')[:5],
            'academic_performance': academic_performance,
            
            # Fee Information
            'fee_summary': fee_summary,
            'unpaid_fees': Fee.objects.filter(student=student, is_paid=False),
            
            # Library Information
            'library_info': library_info,
            
            # Activities
            'activity_info': activity_info,
            'achievements': achievements,
            
            # Communications
            'recent_announcements': Announcement.objects.filter(
                Q(target_audience='All') | Q(target_audience='Students')
            ).order_by('-created_at')[:5],
            'unread_messages': unread_messages,
            'notifications': notifications,
            
            # Course Information
            'available_courses': self.get_available_courses(student),
            
            # Current Academic Calendar
            'current_calendar': SchoolCalendar.objects.filter(is_current=True).first(),
        })
        
        return context

    def calculate_average_grade(self, necta_exams):
        """Calculate average grade points from NECTA exams"""
        if not necta_exams:
            return 0.0
        
        total_points = sum(exam.get_grade_points() for exam in necta_exams)
        return total_points / necta_exams.count()
    
    def get_best_subject(self, necta_exams):
        """Get the subject with best performance"""
        if not necta_exams:
            return None
        
        subject_performance = {}
        for exam in necta_exams:
            subject = exam.get_subject_display()
            if subject not in subject_performance:
                subject_performance[subject] = []
            subject_performance[subject].append(exam.get_grade_points())
        
        best_subject = None
        best_average = 0
        
        for subject, points_list in subject_performance.items():
            average = sum(points_list) / len(points_list)
            if average > best_average:
                best_average = average
                best_subject = subject
        
        return best_subject

    def get_available_courses(self, student):
        """Get courses available for enrollment"""
        # Get courses the student is not already enrolled in
        enrolled_course_ids = Enrollment.objects.filter(
            student=student
        ).values_list('course_offering__course__id', flat=True)
        
        # Get available course offerings for current semester
        current_semester = Semester.objects.filter(is_current=True).first()
        
        if current_semester:
            available_courses = CourseOffering.objects.filter(
                semester=current_semester
            ).exclude(
                course__id__in=enrolled_course_ids
            ).select_related('course', 'faculty').order_by('course__name')
            
            return available_courses
        return CourseOffering.objects.none()

# Duplicate CreateCourseView removed


@login_required
def enroll_course(request):
    if not is_student(request.user):
        return redirect('dashboard')
    
    if request.method == 'POST':
        course_offering_id = request.POST.get('course_offering_id')
        if course_offering_id:
            course_offering = get_object_or_404(CourseOffering, pk=course_offering_id)
            student = request.user.student_profile
            
            # Check if already enrolled
            if Enrollment.objects.filter(student=student, course_offering=course_offering).exists():
                messages.warning(request, f"You are already enrolled in {course_offering.course.name}")
            else:
                # Create enrollment
                Enrollment.objects.create(
                    student=student,
                    course_offering=course_offering,
                    enrollment_date=timezone.now()
                )
                messages.success(request, f"Successfully enrolled in {course_offering.course.name}")
            
            return redirect('student_dashboard')
    
    return redirect('student_dashboard')

@login_required
def view_timetable(request):
    if not is_student(request.user):
        return redirect('dashboard')
    
    student = request.user.student_profile
    schedules = Schedule.objects.filter(
        course__in=student.enrolled_courses.all()
    ).order_by('day', 'start_time')
    
    return render(request, 'core/timetable.html', {
        'schedules': schedules,
        'weekdays': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    })

# ======================
# Faculty Views
# ======================
class FacultyDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'core/faculty_dashboard.html'
    
    def test_func(self):
        return is_faculty(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        faculty = self.request.user.faculty_profile
        courses = Course.objects.filter(courseoffering__faculty=faculty)
        
        # Get course stats
        course_stats = []
        for course in courses:
            enrollments = Enrollment.objects.filter(course_offering__course=course)
            attendance_stats = Attendance.objects.filter(
                enrollment__course_offering__course=course
            ).values('status').annotate(count=Count('status'))
            
            course_stats.append({
                'course': course,
                'student_count': enrollments.count(),
                'attendance_stats': attendance_stats,
            })

        context.update({
            'faculty': faculty,
            'course_stats': course_stats,
            'pending_leave_requests': LeaveRequest.objects.filter(
                course__in=courses,
                status='pending'
            ).count(),
            'recent_messages': Message.objects.filter(
                receiver=self.request.user
            ).order_by('-sent_at')[:5]
        })
        return context

@login_required
def upload_material(request, course_id):
    if not is_faculty(request.user):
        return redirect('dashboard')
    
    course = get_object_or_404(Course, pk=course_id)
    faculty = request.user.faculty_profile
    
    if not Course.objects.filter(
        pk=course_id,
        courseoffering__faculty=faculty
    ).exists():
        messages.error(request, "You don't teach this course")
        return redirect('faculty_dashboard')
    
    if request.method == 'POST':
        form = MaterialUploadForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.course = course
            material.uploaded_by = faculty
            material.save()
            messages.success(request, "Material uploaded successfully")
            return redirect('course_detail', pk=course_id)
    else:
        form = MaterialUploadForm()
    
    return render(request, 'core/upload_material.html', {
        'form': form,
        'course': course
    })
# ======================
# Admin Views
# ======================
# Note: Admin dashboard is handled by admin_dashboard() function above

class SystemSettingsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'core/system_settings.html'
    
    def test_func(self):
        return is_admin(self.request.user)

# ======================
# Enrollment Views
# ======================
class EnrollmentListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Enrollment
    template_name = 'core/enrollment_list.html'
    context_object_name = 'enrollments'
    paginate_by = 20

    def test_func(self):
        return is_admin(self.request.user) or is_faculty(self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'student__user',
            'course_offering__course',
            'course_offering__faculty__user'
        )
        
        if is_faculty(self.request.user):
            queryset = queryset.filter(
                course_offering__faculty=self.request.user.faculty_profile
            )
            
        course_id = self.request.GET.get('course')
        if course_id:
            queryset = queryset.filter(course_offering__course_id=course_id)
            
        student_id = self.request.GET.get('student')
        if student_id:
            queryset = queryset.filter(student_id=student_id)
            
        return queryset.order_by('-enrollment_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if is_admin(self.request.user):
            context['courses'] = Course.objects.all()
            context['students'] = StudentProfile.objects.all()
        else:
            context['courses'] = Course.objects.filter(
                courseoffering__faculty=self.request.user.faculty_profile
            ).distinct()
        return context

class EnrollmentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    from .forms import EnrollmentForm
    
    model = Enrollment
    form_class = EnrollmentForm
    template_name = 'core/enrollment_form.html'
    success_url = reverse_lazy('enrollment_list')

    def test_func(self):
        return is_admin(self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Enrollment created successfully!")
        return super().form_valid(form)

class EnrollmentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    from .forms import EnrollmentForm
    
    model = Enrollment
    form_class = EnrollmentForm
    template_name = 'core/enrollment_form.html'

    def test_func(self):
        return is_admin(self.request.user)

    def get_success_url(self):
        messages.success(self.request, "Enrollment updated successfully!")
        return reverse('enrollment_list')

# ======================
# Grade Views
# ======================
class GradeListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Grade
    template_name = 'core/grade_list.html'
    context_object_name = 'grades'
    paginate_by = 20

    def test_func(self):
        return is_admin(self.request.user) or is_faculty(self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'enrollment__student__user',
            'enrollment__course_offering__course'
        )
        
        if is_faculty(self.request.user):
            queryset = queryset.filter(
                enrollment__course_offering__faculty=self.request.user.faculty_profile
            )
            
        course_id = self.request.GET.get('course')
        if course_id:
            queryset = queryset.filter(
                enrollment__course_offering__course_id=course_id
            )
            
        return queryset.order_by('-awarded_on')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if is_faculty(self.request.user):
            context['courses'] = Course.objects.filter(
                courseoffering__faculty=self.request.user.faculty_profile
            ).distinct()
        else:
            context['courses'] = Course.objects.all()
        return context

class GradeCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    from .forms import GradeForm
    
    model = Grade
    form_class = GradeForm
    template_name = 'core/grade_form.html'
    success_url = reverse_lazy('grade_list')

    def test_func(self):
        return is_faculty(self.request.user)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if is_faculty(self.request.user):
            faculty_profile = self.request.user.faculty_profile
            form.fields['enrollment'].queryset = Enrollment.objects.filter(
                course_offering__faculty=faculty_profile
            )
        return form

    def form_valid(self, form):
        messages.success(self.request, "Grade added successfully!")
        return super().form_valid(form)

class GradeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    from .forms import GradeForm
    
    model = Grade
    form_class = GradeForm
    template_name = 'core/grade_form.html'

    def test_func(self):
        if is_admin(self.request.user):
            return True
        if is_faculty(self.request.user):
            return self.get_object().enrollment.course_offering.faculty == self.request.user.faculty_profile
        return False

    def get_success_url(self):
        messages.success(self.request, "Grade updated successfully!")
        return reverse('grade_list')

@login_required
def debug_permissions(request):
    """Debug view to check user permissions and authentication status"""
    from .utils import is_admin, is_faculty
    
    user = request.user
    return JsonResponse({
        'authenticated': user.is_authenticated,
        'username': user.username,
        'role': getattr(user, 'role', 'NO_ROLE'),
        'is_superuser': user.is_superuser,
        'is_staff': user.is_staff,
        'is_active': user.is_active,
        'has_admin_profile': hasattr(user, 'admin_profile'),
        'has_faculty_profile': hasattr(user, 'faculty_profile'),
        'is_admin_result': is_admin(user),
        'is_faculty_result': is_faculty(user),
        'can_access_attendance': is_admin(user) or is_faculty(user) or user.is_superuser,
        'session_key': request.session.session_key,
        'session_data': dict(request.session),
    })

def attendance_test(request):
    """Temporary test view that bypasses authentication for testing attendance functionality"""
    from .utils import is_admin, is_faculty
    
    # Simulate different user types based on URL parameter
    user_type = request.GET.get('user_type', 'teacher')
    
    if user_type == 'admin':
        # Simulate admin user
        context = {
            'user_role': 'admin',
            'courses': Course.objects.all(),
            'attendance_records': Attendance.objects.all().select_related(
                'enrollment__student__user',
                'enrollment__course_offering__course',
                'enrollment__course_offering__faculty'
            ).order_by('-date')[:10],
            'is_paginated': False,
            'user_type': 'Admin User'
        }
    elif user_type == 'teacher':
        # Simulate teacher user (john_teacher)
        try:
            teacher_faculty = FacultyProfile.objects.get(user__username='john_teacher')
            context = {
                'user_role': 'teacher',
                'courses': Course.objects.filter(offerings__faculty=teacher_faculty).distinct(),
                'attendance_records': Attendance.objects.filter(
                    enrollment__course_offering__faculty=teacher_faculty
                ).select_related(
                    'enrollment__student__user',
                    'enrollment__course_offering__course',
                    'enrollment__course_offering__faculty'
                ).order_by('-date')[:10],
                'is_paginated': False,
                'user_type': 'Teacher (john_teacher)'
            }
        except FacultyProfile.DoesNotExist:
            context = {
                'user_role': 'teacher',
                'courses': Course.objects.none(),
                'attendance_records': Attendance.objects.none(),
                'is_paginated': False,
                'user_type': 'Teacher (no faculty found)'
            }
    else:
        context = {
            'user_role': 'unknown',
            'courses': Course.objects.none(),
            'attendance_records': Attendance.objects.none(),
            'is_paginated': False,
            'user_type': 'Unknown User'
        }
    
    return render(request, 'core/attendance/attendance_list.html', context)

# ======================
# Attendance Views
# ======================
class AttendanceListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Attendance
    template_name = 'core/attendance/attendance_list.html'
    context_object_name = 'attendance_records'
    paginate_by = 20

    def test_func(self):
        # Admins and superusers can see all attendance
        if is_admin(self.request.user) or self.request.user.is_superuser:
            return True
        # Teachers can see attendance for their courses
        elif is_faculty(self.request.user):
            return True
        return False

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'enrollment__student__user',
            'enrollment__course_offering__course',
            'enrollment__course_offering__faculty'
        )
        
        # Teachers can only see attendance for their courses
        if is_faculty(self.request.user):
            queryset = queryset.filter(
                enrollment__course_offering__faculty=self.request.user.faculty_profile
            )
        # Admins and superusers can see all attendance (no filtering needed)
        
        course_id = self.request.GET.get('course')
        if course_id:
            queryset = queryset.filter(
                enrollment__course_offering__course_id=course_id
            )
            
        date = self.request.GET.get('date')
        if date:
            queryset = queryset.filter(date=date)
            
        return queryset.order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Admins and superusers can see all courses
        if is_admin(self.request.user) or self.request.user.is_superuser:
            context['courses'] = Course.objects.all()
            context['user_role'] = 'admin'
        # Teachers can only see their courses
        elif is_faculty(self.request.user):
            context['courses'] = Course.objects.filter(
                offerings__faculty=self.request.user.faculty_profile
            ).distinct()
            context['user_role'] = 'teacher'
        else:
            context['courses'] = Course.objects.none()
            context['user_role'] = 'unknown'
            
        return context

class AttendanceCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    from .forms import AttendanceForm
    
    model = Attendance
    form_class = AttendanceForm
    template_name = 'core/attendance/attendance_form.html'
    success_url = reverse_lazy('attendance_list')

    def test_func(self):
        return is_admin(self.request.user) or is_faculty(self.request.user) or self.request.user.is_superuser

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if is_faculty(self.request.user):
            form.fields['enrollment'].queryset = Enrollment.objects.filter(
                course_offering__faculty=self.request.user.faculty_profile
            )
        return form

    def form_valid(self, form):
        messages.success(self.request, "Attendance recorded successfully!")
        return super().form_valid(form)

class AttendanceUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    from .forms import AttendanceForm
    
    model = Attendance
    form_class = AttendanceForm
    template_name = 'core/attendance/attendance_form.html'

    def test_func(self):
        if is_admin(self.request.user) or self.request.user.is_superuser:
            return True
        if is_faculty(self.request.user):
            return self.get_object().enrollment.course_offering.faculty == self.request.user.faculty_profile
        return False

    def get_success_url(self):
        messages.success(self.request, "Attendance updated successfully!")
        return reverse('attendance_list')

# ======================
# Fee Management Views
# ======================
# Consolidated FeeListView moved to administrative section


class FeeCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    from .forms import FeeForm
    
    model = Fee
    form_class = FeeForm
    template_name = 'core/fee_form.html'
    success_url = reverse_lazy('fee_list')

    def test_func(self):
        return is_admin(self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Fee record created successfully!")
        return super().form_valid(form)

class FeeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    from .forms import FeeForm
    
    model = Fee
    form_class = FeeForm
    template_name = 'core/fee_form.html'

    def test_func(self):
        return is_admin(self.request.user)

    def get_success_url(self):
        messages.success(self.request, "Fee record updated successfully!")
        return reverse('fee_list')

@login_required
def payment_history(request):
    if not is_student(request.user):
        return redirect('dashboard')
    
    student = request.user.student_profile
    payments = Payment.objects.filter(student=student).order_by('-paid_on')
    
    return render(request, 'core/payment_history.html', {
        'payments': payments,
        'total_paid': sum(p.amount for p in payments)
    })

# ======================
# Leave Request Views
# ======================
@login_required
def leave_requests_list(request):
    if not is_student(request.user):
        return redirect('dashboard')
    
    student = request.user.student_profile
    leaves = LeaveRequest.objects.filter(student=student).order_by('-submitted_at')
    
    return render(request, 'core/leave_requests_list.html', {
        'leaves': leaves
    })

class LeaveRequestCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    from .forms import LeaveRequestForm
    
    model = LeaveRequest
    form_class = LeaveRequestForm
    template_name = 'core/leave_request_form.html'
    success_url = reverse_lazy('leave_requests_list')

    def test_func(self):
        return is_student(self.request.user)

    def form_valid(self, form):
        form.instance.student = self.request.user.student_profile
        messages.success(self.request, "Leave request submitted successfully!")
        return super().form_valid(form)

@login_required
def faculty_leave_requests(request):
    if not is_faculty(request.user):
        return redirect('dashboard')
    
    faculty = request.user.faculty_profile
    courses = Course.objects.filter(courseoffering__faculty=faculty)
    leave_requests = LeaveRequest.objects.filter(
        course__in=courses
    ).order_by('-submitted_at')
    
    return render(request, 'core/faculty_leave_requests.html', {
        'leave_requests': leave_requests
    })

@login_required
def update_leave_status(request, leave_id, status):
    if not is_faculty(request.user):
        return redirect('dashboard')
    
    leave = get_object_or_404(LeaveRequest, pk=leave_id)
    faculty = request.user.faculty_profile
    
    if not Course.objects.filter(
        pk=leave.course.pk,
        courseoffering__faculty=faculty
    ).exists():
        messages.error(request, "You don't have permission to update this leave request")
        return redirect('faculty_dashboard')
    
    leave.status = status
    leave.processed_by = faculty
    leave.processed_on = timezone.now()
    leave.save()
    
    messages.success(request, f"Leave request {status}")
    return redirect('faculty_leave_requests')

# ======================
# Communication Views
# ======================
@login_required
def announcement_list(request):
    """View announcements based on user role and permissions"""
    from .models import StudentClass
    
    user = request.user
    
    # Base queryset - active and non-expired announcements
    announcements = Announcement.objects.filter(is_active=True)
    
    # Filter out expired announcements
    announcements = announcements.filter(
        Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
    )
    
    # Filter based on user role and target audience
    if hasattr(user, 'role'):
        if user.role == 'student':
            # Students see announcements targeted at them
            try:
                student_class = user.student_profile.current_class
                announcements = announcements.filter(
                    Q(target_audience='All') |
                    Q(target_audience='Students') |
                    Q(target_audience='Class', target_class=student_class)
                )
            except:
                announcements = announcements.filter(
                    Q(target_audience='All') | Q(target_audience='Students')
                )
        elif user.role == 'teacher':
            # Teachers see announcements targeted at faculty
            announcements = announcements.filter(
                Q(target_audience='All') | Q(target_audience='Faculty')
            )
        elif user.role == 'admin':
            # Admins see all announcements
            pass
    else:
        # Default to faculty if no role
        announcements = announcements.filter(
            Q(target_audience='All') | Q(target_audience='Faculty')
        )
    
    announcements = announcements.order_by('-created_at')
    
    return render(request, 'core/announcement_list.html', {
        'announcements': announcements,
        'today': timezone.now().date(),
        'yesterday': (timezone.now() - timezone.timedelta(days=1)).date(),
    })

@login_required
@user_passes_test(is_admin)
def admin_announcements(request):
    """Administrative dashboard for institutional broadcasting"""
    from .forms import AnnouncementForm
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, user=request.user)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.created_by = request.user
            announcement.save()
            messages.success(request, "Institutional announcement broadcasted successfully.")
            return redirect('admin_announcements')
    else:
        form = AnnouncementForm(user=request.user)

    announcements = Announcement.objects.all().order_by('-created_at')
    
    return render(request, 'core/admin_management/admin_announcements.html', {
        'form': form,
        'announcements': announcements,
        'role': 'Administrator',
        'title': 'Institutional Oversight'
    })

@login_required
@user_passes_test(is_faculty)
def teacher_announcements(request):
    """Teacher dashboard for class-specific announcements"""
    from .forms import AnnouncementForm
    
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, user=request.user)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.created_by = request.user
            announcement.save()
            messages.success(request, "Announcement created successfully!")
            return redirect('teacher_announcements')
    else:
        form = AnnouncementForm(user=request.user)

    # Get announcements created by this teacher
    announcements = Announcement.objects.filter(created_by=request.user).order_by('-created_at')
    
    return render(request, 'core/teacher_announcements.html', {
        'form': form,
        'announcements': announcements,
        'role': 'Teacher',
        'title': 'Class Announcements'
    })

@login_required
def inbox(request):
    messages = Message.objects.filter(recipient=request.user).order_by('-sent_at')
    return render(request, 'core/inbox.html', {'messages': messages})

@login_required
def send_message(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            messages.success(request, "Message sent successfully")
            return redirect('inbox')
    else:
        form = MessageForm()

    # All users can message any other user in the system
    recipients = User.objects.all().select_related('student_profile', 'faculty_profile').exclude(id=request.user.id)

    return render(request, 'core/communication/send_message.html', {
        'form': form,
        'recipients': recipients.order_by('first_name', 'last_name')
    })

# ======================
# Forum Views
# ======================
@login_required
def forum_topics(request):
    topics = ForumTopic.objects.annotate(
        post_count=Count('posts')
    ).order_by('-created_at')
    
    return render(request, 'communication/forum_topics.html', {
        'topics': topics
    })

@login_required
def topic_detail(request, topic_id):
    topic = get_object_or_404(ForumTopic, pk=topic_id)
    posts = topic.posts.all().select_related('author')
    
    if request.method == 'POST':
        form = ForumPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.author = request.user
            post.save()
            return redirect('topic_detail', topic_id=topic_id)
    else:
        form = ForumPostForm()
    
    return render(request, 'communication/topic_detail.html', {
        'topic': topic,
        'posts': posts,
        'form': form
    })

class CreateTopicView(LoginRequiredMixin, CreateView):
    from .forms import ForumTopicForm
    
    model = ForumTopic
    form_class = ForumTopicForm
    template_name = 'communication/create_topic.html'
    success_url = reverse_lazy('forum_topics')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Topic created successfully!")
        return super().form_valid(form)

# ======================
# Library Views
# ======================
@login_required
def search_books(request):
    query = request.GET.get('q', '')
    books = Book.objects.filter(title__icontains=query) if query else Book.objects.all()
    
    return render(request, 'library/book_search.html', {
        'books': books,
        'query': query
    })

@login_required
def borrowed_books(request):
    if not is_student(request.user):
        return redirect('dashboard')
    
    student = request.user.student_profile
    borrowed = BorrowedBook.objects.filter(
        student=student
    ).select_related('book').order_by('-issue_date')
    
    return render(request, 'library/borrowed_books.html', {
        'borrowed_books': borrowed
    })

@login_required
def elibrary(request):
    ebooks = Book.objects.filter(is_ebook=True)
    return render(request, 'library/elibrary.html', {'ebooks': ebooks})

# ======================
# Parent Views
# ======================
class ParentDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'core/parent_dashboard.html'
    
    def test_func(self):
        return is_parent(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        parent = self.request.user.parent_profile
        child = parent.child
        
        context.update({
            'child': child,
            'attendance': Attendance.objects.filter(student=child).order_by('-date')[:5],
            'grades': Grade.objects.filter(student=child).order_by('-awarded_on')[:5],
            'unpaid_fees': Fee.objects.filter(student=child, is_paid=False),
            'announcements': Announcement.objects.filter(
                Q(target_audience='All') | Q(target_audience='Parents')
            ).order_by('-created_at')[:5]
        })
        return context

@login_required
def view_child_attendance(request):
    if not is_parent(request.user):
        return redirect('dashboard')
    
    child = request.user.parent_profile.child
    attendance = Attendance.objects.filter(student=child).order_by('-date')
    
    return render(request, 'parent/attendance.html', {
        'attendance': attendance,
        'child': child
    })

@login_required
def view_child_grades(request):
    if not is_parent(request.user):
        return redirect('dashboard')
    
    child = request.user.parent_profile.child
    grades = Grade.objects.filter(student=child).select_related('course')
    
    return render(request, 'parent/grades.html', {
        'grades': grades,
        'child': child
    })

@login_required
def view_fee_alerts(request):
    if not is_parent(request.user):
        return redirect('dashboard')
    
    child = request.user.parent_profile.child
    payments = Payment.objects.filter(student=child).order_by('-paid_on')
    
    return render(request, 'parent/fees.html', {
        'payments': payments,
        'child': child
    })

@login_required
def parent_send_message(request):
    if not is_parent(request.user):
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            messages.success(request, "Message sent successfully")
            return redirect('parent_inbox')
    else:
        form = MessageForm()
    
    teachers = User.objects.filter(groups__name='Faculty')
    
    return render(request, 'parent/send_message.html', {
        'form': form,
        'teachers': teachers
    })

# ======================
# Activity Views
# ======================
@login_required
def activity_list(request):
    activities = Activity.objects.order_by('-date')
    return render(request, 'activities/activity_list.html', {
        'activities': activities
    })

@login_required
def achievement_list(request):
    if not is_student(request.user):
        return redirect('dashboard')
    
    student = request.user.student_profile
    achievements = Achievement.objects.filter(student=student).order_by('-date_awarded')
    
    return render(request, 'activities/achievements.html', {
        'achievements': achievements
    })

# ======================
# Exam Views
# ======================
@login_required
def exam_schedule_view(request):
    if not is_student(request.user):
        return redirect('dashboard')
    
    student = request.user.student_profile
    exams = ExamSchedule.objects.filter(
        course__in=student.enrolled_courses.all()
    ).order_by('date', 'start_time')
    
    return render(request, 'exams/exam_schedule.html', {
        'exams': exams
    })

@login_required
def gradebook_view(request):
    if not is_student(request.user):
        return redirect('dashboard')
    
    student = request.user.student_profile
    grades = Grade.objects.filter(student=student).select_related('course')
    
    return render(request, 'exams/gradebook.html', {
        'grades': grades
    })

@login_required
def report_cards_view(request):
    if not is_student(request.user):
        return redirect('dashboard')
    
    student = request.user.student_profile
    reports = ReportCard.objects.filter(student=student).order_by('-semester')
    
    return render(request, 'exams/report_cards.html', {
        'reports': reports
    })

# ======================
# Material Views
# ======================
@login_required
def view_materials(request):
    if not is_student(request.user):
        return redirect('dashboard')
    
    student = request.user.student_profile
    materials = Material.objects.filter(
        course__in=student.enrolled_courses.all()
    ).order_by('-upload_date')
    
    return render(request, 'core/materials.html', {
        'materials': materials
    })

# ======================
# System Reports
# ======================
class ReportsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'core/reports.html'
    
    def test_func(self):
        return is_admin(self.request.user)

   
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    
    # Student stats by department
    context['student_dept_stats'] = StudentProfile.objects.values(
        'department__name'
    ).annotate(
        count=Count('department'),
        avg_gpa=Avg('gpa')
    ).order_by('-count')
    
    # Faculty stats by department
    context['faculty_dept_stats'] = FacultyProfile.objects.values(
        'department__name'
    ).annotate(
        count=Count('department')
    ).order_by('-count')
    
    # Course stats with enrollment and grades
    context['course_stats'] = Course.objects.annotate(
        enrollment_count=Count('enrollments'),
        avg_grade=Avg('enrollments__grade__score')
    ).order_by('-enrollment_count')
    
    # Attendance distribution
    context['attendance_stats'] = Attendance.objects.values(
        'status'
    ).annotate(
        count=Count('status')
    )
    
    return context






    # //Course


# Public-facing views
def public_home(request):
    """Public home page for visitors"""
    return render(request, 'core/public_pages/public_home.html')

def public_about(request):
    """Public about page"""
    return render(request, 'core/public_pages/public_about.html')

def public_courses(request):
    """Public courses catalog page"""
    return render(request, 'core/public_pages/public_courses.html')

def public_admissions(request):
    """Public admissions page"""
    return render(request, 'core/public_pages/public_admissions.html')

def public_contact(request):
    """Public contact page"""
    return render(request, 'core/public_pages/public_contact.html')


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Course, Department
from django.db.models import Avg, Count
from django.utils import timezone
from datetime import timedelta

@login_required
def grade_list(request):
    # Get all grades with related data
    grades = Grade.objects.select_related(
        'enrollment__student__user',
        'enrollment__course_offering__course',
        'enrollment__course_offering__faculty__user'
    ).all()
    
    # Get courses for filtering
    courses = Course.objects.select_related('department').all()
    
    # Get statistics
    total_grades = grades.count()
    average_grade = grades.aggregate(avg_grade=Avg('grade'))['avg_grade']
    recent_grades = grades.filter(awarded_on__gte=timezone.now() - timedelta(days=7)).count()
    
    # Filter by course if specified
    course_filter = request.GET.get('course')
    if course_filter:
        grades = grades.filter(enrollment__course_offering__course_id=course_filter)
    
    context = {
        'grades': grades,
        'courses': courses,
        'total_grades': total_grades,
        'average_grade': average_grade,
        'recent_grades': recent_grades,
    }
    return render(request, 'core/grade_list.html', context)

# ======================
# Subject Enrollment Views for Tanzanian O-Level
# ======================
@login_required
@user_passes_test(is_admin)
def subject_enrollment_dashboard(request):
    """Dashboard for managing subject enrollments"""
    academic_year = timezone.now().year
    
    # Get statistics
    total_enrollments = SubjectEnrollment.objects.filter(academic_year=academic_year).count()
    students_by_form = {}
    for form_num in range(1, 5):
        students_by_form[f'Form {form_num}'] = StudentProfile.objects.filter(
            current_form=form_num
        ).count()
    
    # Subject enrollment statistics
    subject_stats = Subject.objects.filter(
        enrollments__academic_year=academic_year
    ).annotate(
        enrollment_count=Count('enrollments')
    ).order_by('-enrollment_count')
    
    context = {
        'academic_year': academic_year,
        'total_enrollments': total_enrollments,
        'students_by_form': students_by_form,
        'subject_stats': subject_stats,
        'available_subjects': Subject.objects.all().order_by('form_level', 'code'),
    }
    return render(request, 'core/subject_enrollment_dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def enroll_student_subjects(request, student_id):
    """Enroll a specific student in subjects"""
    student = get_object_or_404(StudentProfile, id=student_id)
    academic_year = timezone.now().year
    
    if request.method == 'POST':
        form = SubjectEnrollmentForm(request.POST, initial={'student': student})
        if form.is_valid():
            # Check if student is already enrolled in this subject
            subject = form.cleaned_data['subject']
            existing = SubjectEnrollment.objects.filter(
                student=student, 
                subject=subject, 
                academic_year=academic_year
            ).first()
            
            if existing:
                messages.warning(request, f"{student} is already enrolled in {subject}")
            else:
                form.instance.student = student
                form.instance.academic_year = academic_year
                form.save()
                messages.success(request, f"Successfully enrolled {student} in {subject}")
            return redirect('subject_enrollment_dashboard')
    else:
        form = SubjectEnrollmentForm(initial={'student': student})
    
    # Filter subjects based on student's current form
    available_subjects = Subject.objects.filter(form_level=str(student.current_form))
    
    context = {
        'form': form,
        'student': student,
        'available_subjects': available_subjects,
        'current_enrollments': SubjectEnrollment.objects.filter(
            student=student, academic_year=academic_year
        ).select_related('subject'),
    }
    return render(request, 'core/enroll_student_subjects.html', context)

@login_required
@user_passes_test(is_admin)
def bulk_subject_enrollment(request):
    """Bulk enrollment of students in subjects"""
    academic_year = timezone.now().year
    
    if request.method == 'POST':
        form = BulkSubjectEnrollmentForm(request.POST)
        if form.is_valid():
            academic_year = form.cleaned_data['academic_year']
            students = StudentProfile.objects.filter(current_form__in=[1, 2])  # Forms 1 & 2
            
            # Get core subjects for these forms
            core_subjects = Subject.objects.filter(
                form_level__in=['1', '2'], 
                is_core=True
            )
            
            enrolled_count = 0
            for student in students:
                for subject in core_subjects:
                    # Check if already enrolled
                    if not SubjectEnrollment.objects.filter(
                        student=student, 
                        subject=subject, 
                        academic_year=academic_year
                    ).exists():
                        SubjectEnrollment.objects.create(
                            student=student,
                            subject=subject,
                            academic_year=academic_year
                        )
                        enrolled_count += 1
            
            messages.success(request, f"Successfully enrolled {enrolled_count} student-subject combinations")
            return redirect('subject_enrollment_dashboard')
    else:
        form = BulkSubjectEnrollmentForm()
    
    context = {
        'form': form,
        'academic_year': academic_year,
        'core_subjects_form1': Subject.objects.filter(form_level='1', is_core=True),
        'core_subjects_form2': Subject.objects.filter(form_level='2', is_core=True),
    }
    return render(request, 'core/bulk_subject_enrollment.html', context)

class SubjectEnrollmentListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """List all subject enrollments"""
    model = SubjectEnrollment
    template_name = 'core/subject_enrollment_list.html'
    context_object_name = 'enrollments'
    paginate_by = 25
    
    def test_func(self):
        return is_admin(self.request.user)
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('student__user', 'subject')
        academic_year = self.request.GET.get('academic_year', timezone.now().year)
        return queryset.filter(academic_year=academic_year)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['academic_years'] = SubjectEnrollment.objects.values_list('academic_year', flat=True).distinct()
        context['current_year'] = timezone.now().year
        return context

# ======================
# Subject Management Views
# ======================
# Last deployment: Mar 6, 2026 4:53 PM UTC
class SubjectListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """List all subjects"""
    model = Subject
    template_name = 'core/subject_list.html'
    context_object_name = 'subjects'
    paginate_by = 20
    
    def test_func(self):
        return is_admin(self.request.user)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        form_level = self.request.GET.get('form_level')
        if form_level:
            queryset = queryset.filter(form_level=form_level)
        return queryset.order_by('form_level', 'code')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_levels'] = Subject.FORM_LEVELS
        context['current_form_level'] = self.request.GET.get('form_level', '')
        return context

class SubjectCreateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    """Create a new subject"""
    model = Subject
    form_class = SubjectForm
    template_name = 'core/subject_form.html'
    success_message = "Subject '%(name)s' has been created successfully."
    
    def test_func(self):
        return is_admin(self.request.user)
    
    def get_success_url(self):
        return reverse('subject_list')

class SubjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    """Update an existing subject"""
    model = Subject
    form_class = SubjectForm
    template_name = 'core/subject_form.html'
    success_message = "Subject '%(name)s' has been updated successfully."
    
    def test_func(self):
        return is_admin(self.request.user)
    
    def get_success_url(self):
        return reverse('subject_list')

class SubjectDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a subject"""
    model = Subject
    template_name = 'core/subject_confirm_delete.html'
    success_url = reverse_lazy('subject_list')
    
    def test_func(self):
        return is_admin(self.request.user)
    
    def delete(self, request, *args, **kwargs):
        subject = self.get_object()
        success_message = f"Subject '{subject.name}' has been deleted successfully."
        messages.success(request, success_message)
        return super().delete(request, *args, **kwargs)

# ======================
# Class Management Views
# ======================
@login_required
@user_passes_test(is_admin)
def class_management(request):
    """Manage student classes and form assignments"""
    form_level = request.GET.get('form_level', '1')
    
    students = StudentProfile.objects.filter(current_form=form_level).select_related('user', 'department')
    
    # Get statistics
    class_stats = {}
    for form_num in range(1, 5):
        class_stats[f'Form {form_num}'] = StudentProfile.objects.filter(current_form=form_num).count()
    
    context = {
        'students': students,
        'form_level': form_level,
        'class_stats': class_stats,
        'form_levels': StudentProfile.FORM_CHOICES,
    }
    return render(request, 'core/class_management.html', context)

@login_required
@user_passes_test(is_admin)
def assign_student_class(request, student_id):
    """Assign or update a student's class/form"""
    student = get_object_or_404(StudentProfile, id=student_id)
    
    if request.method == 'POST':
        form = ClassForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, f"{student.user.get_full_name()} has been assigned to Form {form.cleaned_data['current_form']}")
            return redirect('class_management')
    else:
        form = ClassForm(instance=student)
    
    context = {
        'form': form,
        'student': student,
    }
    return render(request, 'core/assign_class.html', context)

@login_required
@user_passes_test(is_admin)
def bulk_class_assignment(request):
    """Bulk assignment of students to classes"""
    if request.method == 'POST':
        source_form = request.POST.get('source_form')
        target_form = request.POST.get('target_form')
        
        if source_form and target_form and source_form != target_form:
            students = StudentProfile.objects.filter(current_form=source_form)
            updated_count = students.update(current_form=target_form)
            messages.success(request, f"Successfully moved {updated_count} students from Form {source_form} to Form {target_form}")
        else:
            messages.error(request, "Please select different source and target forms.")
        
        return redirect('class_management')
    
    context = {
        'form_choices': StudentProfile.FORM_CHOICES,
    }
    return render(request, 'core/bulk_class_assignment.html', context)

@login_required
@user_passes_test(is_admin)
def admin_timetable(request):
    """Complete timetable management with CRUD operations"""
    
    # Get all timetable entries with related data
    timetable_entries = TimeTable.objects.select_related(
        'course_offering__course',
        'course_offering__faculty__user',
        'semester'
    ).order_by('day', 'start_time')
    
    # Get related data for filters
    courses = CourseOffering.objects.select_related('course', 'faculty__user').filter(semester__is_active=True)
    faculties = FacultyProfile.objects.select_related('user').all()
    semesters = Semester.objects.all()
    return render(request, 'core/admin_management/admin_timetable.html', context)

@login_required
@user_passes_test(is_admin)
def admin_timetable_delete(request, pk):
    schedule = get_object_or_404(TimeTable, pk=pk)
    schedule.delete()
    messages.success(request, "Timetable entry removed.")
    return redirect('admin_timetable')


@login_required
@user_passes_test(is_admin)
def admin_exams(request):
    """Admin exam management"""
    context = {
        'title': 'Exam Management',
        'school_info': get_school_info(),
    }
    return render(request, 'core/admin_management/admin_exams.html', context)


@login_required
@user_passes_test(is_admin)
def admin_library(request):
    """Admin library management"""
    context = {
        'title': 'Library Management',
        'school_info': get_school_info(),
    }
    return render(request, 'core/admin_management/admin_library.html', context)


@login_required
@user_passes_test(is_admin)
def admin_fees(request):
    """Complete fee management with CRUD operations"""
    
    # Get all fees with related data
    fees = Fee.objects.select_related(
        'student__user', 'fee_structure'
    ).prefetch_related(
        'payments'
    ).order_by('-due_date')
    
    # Get fee structures for filter
    fee_structures = FeeStructure.objects.all()
    
    # Apply filters
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    fee_structure_filter = request.GET.get('fee_structure', '')
    
    if search_query:
        fees = fees.filter(
            Q(student__user__first_name__icontains=search_query) |
            Q(student__user__last_name__icontains=search_query) |
            Q(student__roll_number__icontains=search_query) |
            Q(amount__icontains=search_query)
        )
    
    if status_filter:
        if status_filter == 'paid':
            fees = fees.filter(payments__status='completed')
        elif status_filter == 'pending':
            fees = fees.filter(payments__status='pending')
        elif status_filter == 'overdue':
            fees = fees.filter(due_date__lt=timezone.now().date(), payments__status__in=['pending', 'partial'])
    
    if fee_structure_filter:
        fees = fees.filter(fee_structure_id=fee_structure_filter)
    
    # Calculate statistics
    total_fees = fees.count()
    paid_fees = fees.filter(payments__status='completed').count()
    pending_fees = fees.filter(payments__status='pending').count()
    overdue_fees = fees.filter(due_date__lt=timezone.now().date(), payments__status__in=['pending', 'partial']).count()
    total_revenue = fees.aggregate(total=Sum('amount'))['total'] or 0
    collected_revenue = fees.filter(payments__status='completed').aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'fees': fees,
        'fee_structures': fee_structures,
        'total_fees': total_fees,
        'paid_fees': paid_fees,
        'pending_fees': pending_fees,
        'overdue_fees': overdue_fees,
        'total_revenue': total_revenue,
        'collected_revenue': collected_revenue,
        'search_query': search_query,
        'status_filter': status_filter,
        'fee_structure_filter': fee_structure_filter,
    }
    
    return render(request, 'core/admin_management/admin_fees.html', context)


@login_required
@user_passes_test(is_admin)
def admin_fee_create(request):
    """Create new fee"""
    if request.method == 'POST':
        try:
            student_id = request.POST.get('student')
            fee_structure_id = request.POST.get('fee_structure')
            amount = request.POST.get('amount')
            due_date = request.POST.get('due_date')
            
            # Validate required fields
            if not all([student_id, fee_structure_id, amount, due_date]):
                messages.error(request, 'Please fill in all required fields.')
                return redirect('admin_fees')
            
            # Get related objects
            student = get_object_or_404(StudentProfile, id=student_id)
            fee_structure = get_object_or_404(FeeStructure, id=fee_structure_id)
            
            # Create fee
            fee = Fee.objects.create(
                student=student,
                fee_structure=fee_structure,
                amount=amount,
                due_date=due_date,
                created_by=request.user
            )
            
            messages.success(request, f'Fee created for {student.user.get_full_name()} successfully!')
            return redirect('admin_fees')
            
        except Exception as e:
            messages.error(request, f'Error creating fee: {str(e)}')
    
    students = StudentProfile.objects.select_related('user').all()
    fee_structures = FeeStructure.objects.all()
    context = {
        'students': students,
        'fee_structures': fee_structures,
    }
    
    return render(request, 'core/admin_management/admin_fee_create.html', context)


@login_required
@user_passes_test(is_admin)
def admin_fee_edit(request, pk):
    """Edit existing fee"""
    fee = get_object_or_404(Fee.objects.select_related('student__user', 'fee_structure'), pk=pk)
    
    if request.method == 'POST':
        try:
            fee.amount = request.POST.get('amount')
            fee.due_date = request.POST.get('due_date')
            
            # Update fee structure if changed
            fee_structure_id = request.POST.get('fee_structure')
            if fee_structure_id:
                fee.fee_structure = get_object_or_404(FeeStructure, id=fee_structure_id)
            
            fee.save()
            
            messages.success(request, f'Fee updated successfully!')
            return redirect('admin_fees')
            
        except Exception as e:
            messages.error(request, f'Error updating fee: {str(e)}')
    
    students = StudentProfile.objects.select_related('user').all()
    fee_structures = FeeStructure.objects.all()
    context = {
        'fee': fee,
        'students': students,
        'fee_structures': fee_structures,
    }
    
    return render(request, 'core/admin_management/admin_fee_edit.html', context)


@login_required
@user_passes_test(is_admin)
def admin_fee_delete(request, pk):
    """Delete fee"""
    fee = get_object_or_404(Fee.objects.select_related('student__user'), pk=pk)
    
    if request.method == 'POST':
        student_name = fee.student.user.get_full_name()
        fee.delete()
        
        messages.success(request, f'Fee for {student_name} deleted successfully!')
        return redirect('admin_fees')
    
    context = {
        'fee': fee,
    }
    
    return render(request, 'core/admin_management/admin_fee_delete.html', context)

@login_required
@user_passes_test(is_admin)
def admin_reports(request):
    """Admin reports with institutional metrics"""
    from django.db.models import Sum
    total_students = User.objects.filter(role='student').count()
    total_teachers = User.objects.filter(role='teacher').count()
    revenue_month = Fee.objects.filter(is_paid=True, paid_date__month=timezone.now().month).aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'title': 'System Reports',
        'school_info': get_school_info(),
        'total_students': total_students,
        'total_teachers': total_teachers,
        'revenue_month': revenue_month,
        'staff_engagement': 92, # Placeholder for now
    }
    return render(request, 'core/admin_management/admin_reports.html', context)

@login_required
@user_passes_test(is_admin)
def admin_settings(request):
    """Admin settings"""
    context = {
        'title': 'System Settings',
        'school_info': get_school_info(),
    }
    return render(request, 'core/admin_management/admin_settings.html', context)

@login_required
@user_passes_test(is_admin)
def admin_timetable_create(request):
    """Create new timetable entry"""
    if request.method == 'POST':
        try:
            # Get form data
            course_offering_id = request.POST.get('course_offering')
            day = request.POST.get('day')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            room = request.POST.get('room', '')
            semester_id = request.POST.get('semester')
            
            # Validate required fields
            if not all([course_offering_id, day, start_time, end_time, semester_id]):
                messages.error(request, 'Please fill in all required fields.')
                return redirect('admin_timetable')
            
            # Get related objects
            course_offering = get_object_or_404(CourseOffering, id=course_offering_id)
            semester = get_object_or_404(Semester, id=semester_id)
            
            # Create timetable entry
            timetable = TimeTable.objects.create(
                course_offering=course_offering,
                day=day,
                start_time=start_time,
                end_time=end_time,
                room=room,
                semester=semester
            )
            
            messages.success(request, 'Timetable entry created successfully!')
            return redirect('admin_timetable')
            
        except Exception as e:
            messages.error(request, f'Error creating timetable entry: {str(e)}')
            return redirect('admin_timetable')
    
    # Get data for form
    courses = CourseOffering.objects.select_related('course', 'faculty__user').filter(semester__is_active=True)
    semesters = Semester.objects.all()
    
    context = {
        'courses': courses,
        'semesters': semesters,
    }
    
    return render(request, 'core/admin_management/admin_timetable_create.html', context)

@login_required
@user_passes_test(is_admin)
def admin_timetable_edit(request, pk):
    """Edit existing timetable entry"""
    timetable = get_object_or_404(TimeTable, pk=pk)
    
    if request.method == 'POST':
        try:
            # Update timetable
            timetable.course_offering_id = request.POST.get('course_offering')
            timetable.day = request.POST.get('day')
            timetable.start_time = request.POST.get('start_time')
            timetable.end_time = request.POST.get('end_time')
            timetable.room = request.POST.get('room', '')
            timetable.semester_id = request.POST.get('semester')
            
            timetable.save()
            
            messages.success(request, 'Timetable entry updated successfully!')
            return redirect('admin_timetable')
            
        except Exception as e:
            messages.error(request, f'Error updating timetable entry: {str(e)}')
            return redirect('admin_timetable')
    
    # Get data for form
    courses = CourseOffering.objects.select_related('course', 'faculty__user').filter(semester__is_active=True)
    semesters = Semester.objects.all()
    
    context = {
        'timetable': timetable,
        'courses': courses,
        'semesters': semesters,
    }
    
    return render(request, 'core/admin_management/admin_timetable_edit.html', context)

@login_required
@user_passes_test(is_admin)
def admin_timetable_delete(request, pk):
    """Delete timetable entry"""
    timetable = get_object_or_404(TimeTable, pk=pk)
    
    if request.method == 'POST':
        timetable.delete()
        messages.success(request, 'Timetable entry deleted successfully!')
        return redirect('admin_timetable')
    
    context = {
        'timetable': timetable,
    }
    
    return render(request, 'core/admin_management/admin_timetable_delete.html', context)

@login_required
def teacher_timetable(request):
    """View sessions specifically assigned to the logged-in teacher"""
    try:
        faculty = request.user.faculty_profile
    except FacultyProfile.DoesNotExist:
        messages.error(request, "Teacher profile not found.")
        return redirect('teacher_dashboard')
        
    current_semester = Semester.objects.filter(is_current=True).first()
    if not current_semester:
        current_semester = Semester.objects.all().order_by('-id').first()
    
    # Filter timetable by sessions where this faculty is the instructor
    timetable_entries = TimeTable.objects.filter(
        course_offering__faculty=faculty,
        semester=current_semester
    ).select_related('course_offering__course', 'semester', 'course_offering__course__department').order_by('day', 'start_time')
    
    context = {
        'title': 'My Teaching Schedule',
        'schedules': timetable_entries,
        'days': [day[0] for day in TimeTable.DAY_CHOICES],
        'is_teacher': True,
        'school_info': get_school_info(),
    }
    return render(request, 'core/teacher_timetable.html', context)

@login_required
@user_passes_test(is_student)
def submit_assignment(request, assignment_id):
    """Handle assignment submission"""
    assignment = get_object_or_404(Assignment, id=assignment_id)
    student = request.user.student_profile
    
    if request.method == 'POST':
        submission_text = request.POST.get('submission_text')
        submitted_file = request.FILES.get('submitted_file')
        
        if not submitted_file:
            messages.error(request, "Please upload a file to submit.")
            return redirect('student_assignments')
        
        # Check if already submitted
        submission, created = Submission.objects.get_or_create(
            assignment=assignment,
            student=student,
            defaults={'file': submitted_file}
        )
        
        if not created:
            # Update existing submission
            submission.file = submitted_file
            submission.submitted_at = timezone.now()
            
        submission.feedback = submission_text or ""
        submission.save()
        
        messages.success(request, f"Assignment '{assignment.title}' submitted successfully!")
        return redirect('student_assignments')
    
    return redirect('student_assignments')

@login_required
@user_passes_test(is_student)
def process_payment(request):
    """Handle student fee payments (Demo)"""
    if request.method == 'POST':
        fee_id = request.POST.get('fee_id')
        amount = request.POST.get('amount')
        payment_method = request.POST.get('payment_method')
        
        try:
            student = request.user.student_profile
            fee = Fee.objects.get(id=fee_id, student=student)
            
            # Simulated Transaction ID based on method
            prefix = {
                'mobile_money': 'MM',
                'bank_transfer': 'BT',
                'credit_card': 'CC'
            }.get(payment_method, 'PY')
            
            txn_id = f"{prefix}-{uuid.uuid4().hex[:8].upper()}"
            
            # Create payment record
            payment = Payment.objects.create(
                student=student,
                fee=fee,
                amount=amount,
                payment_method=payment_method,
                transaction_id=txn_id
            )
            
            # Update fee status (Simplified for demo)
            fee.is_paid = True
            fee.paid_date = timezone.now().date()
            # Generate receipt number
            fee.receipt_number = f"RCP-{payment.id}"
            fee.save()
            
            # Add school info to context if needed? No, just messages.
            method_name = dict(Payment.PAYMENT_METHOD_CHOICES).get(payment_method, "Selected Method")
            messages.success(request, f"Successfully paid {amount} TZS for {fee.category} via {method_name}. Transaction ID: {txn_id}")
            
        except Fee.DoesNotExist:
            messages.error(request, "Fee record not found or access denied.")
        except Exception as e:
            messages.error(request, f"Payment error: {str(e)}")
            
    return redirect('student_fees')
