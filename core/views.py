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
from django.db.models import Q, Count, Avg
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
)
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import get_user_model
from .utils import is_student, is_faculty, is_admin, is_parent  # Ensure all these functions exist

from .models import (
    User, Course, Department, StudentProfile, FacultyProfile, AdminProfile,
    Enrollment, Attendance, Grade, ActivityLog, Fee, LeaveRequest,ExamSchedule, Payment, Announcement, Message,
    ForumTopic, Book, BorrowedBook, Activity, Achievement, FeeStructure,
    ReportCard, Material, Schedule, ForumPost
)

User = get_user_model()
class StudentDetailView(DetailView):
    model = StudentProfile
    template_name = 'students/student_detail.html'  # adjust path as needed
    context_object_name = 'student'

class CourseListView(View):
    def get(self, request):
        # Get all courses with related data
        courses = Course.objects.select_related('department').prefetch_related('enrollment_set').all()
        departments = Department.objects.all()
        
        # Get statistics
        total_courses = courses.count()
        active_courses = courses.filter(is_active=True).count()
        total_enrollments = Enrollment.objects.filter(course__in=courses).count()
        
        context = {
            'courses': courses,
            'departments': departments,
            'total_courses': total_courses,
            'active_courses': active_courses,
            'total_enrollments': total_enrollments,
        }
        return render(request, 'core/course_list.html', context)  
class CourseManagementView(View):
    def get(self, request):
        return render(request, 'core/course_management.html') 
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
    template_name = 'core/course_management.html'
    context_object_name = 'courses'
    
    def test_func(self):
        return is_admin(self.request.user)
    
    def get_queryset(self):
        return Course.objects.select_related('department').all()

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
class StudentListView(ListView):
    model = StudentProfile
    template_name = 'core/student_list.html'  # your template here
    context_object_name = 'students'
# ======================
# Permission Helpers
# ======================
def is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name='Admin').exists())

def is_faculty(user):
    return user.is_authenticated and user.groups.filter(name='Faculty').exists()

def is_student(user):
    return user.is_authenticated and user.groups.filter(name='Student').exists()

def is_parent(user):
    return user.is_authenticated and hasattr(user, 'parent_profile')

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

    return render(request, 'core/attendance_summary.html', context)
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
class UserListView(ListView):
    model = User
    template_name = 'core/user_list.html'  # Adjust path accordingly
    context_object_name = 'users'
    paginate_by = 20  # optional pagination
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'  # fallback template (optional)

    def dispatch(self, request, *args, **kwargs):
        if is_student(request.user):
            return redirect('student_dashboard')
        elif is_faculty(request.user):
            return redirect('faculty_dashboard')
        elif is_admin(request.user):
            return redirect('admin_dashboard')
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
        return render(request, 'core/login.html', {'form': form})

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return self.redirect_based_on_role(user)
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'core/login.html', {'form': form})
    
    def redirect_based_on_role(self, user):
        """Redirect user based on their role"""
        if user.role == 'normal':
            return redirect('public_home')
        elif user.role == 'student':
            return redirect('student_dashboard')
        elif user.role == 'teacher':
            return redirect('teacher_dashboard')
        elif user.role == 'headmaster':
            return redirect('headmaster_dashboard')
        elif user.role == 'admin':
            return redirect('admin_dashboard')
        else:
            return redirect('public_home')

class CustomLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('public_home')

# Public Registration Views
from .forms import PublicUserRegistrationForm, StaffRegistrationForm

class PublicRegisterView(CreateView):
    """Registration for normal users and students"""
    model = User
    form_class = PublicUserRegistrationForm
    template_name = 'core/public_register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password1'])
        user.save()
        
        # Create profile based on role
        if user.role == 'student':
            user.is_student = True
            user.save()
            # StudentProfile will be created when student completes admission
            messages.success(self.request, "Student registration successful! Please complete your admission application.")
        else:
            messages.success(self.request, "Account created successfully! You can now login.")
        
        return super().form_valid(form)

class StaffRegisterView(CreateView):
    """Registration for staff roles (teacher, headmaster, admin)"""
    model = User
    form_class = StaffRegistrationForm
    template_name = 'core/staff_register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password1'])
        user.save()
        
        # Set role flags and create appropriate profile
        if user.role == 'teacher':
            user.is_faculty = True
            user.save()
            # FacultyProfile will need to be created by admin
            messages.success(self.request, "Teacher registration successful! Your profile will be completed by the school administration.")
        elif user.role == 'headmaster':
            user.is_headmaster = True
            user.save()
            # HeadmasterProfile will need to be created by admin
            messages.success(self.request, "Headmaster registration successful! Your profile will be completed by the school administration.")
        elif user.role == 'admin':
            user.is_admin = True
            user.save()
            # AdminProfile will need to be created by super admin
            messages.success(self.request, "Admin registration successful! Your profile will be completed by the super administrator.")
        
        return super().form_valid(form)

# Role-based Dashboard Views
class RoleBasedDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        return self.redirect_based_on_role(request.user)
    
    def redirect_based_on_role(self, user):
        """Redirect user based on their role"""
        if user.role == 'normal':
            return redirect('public_home')
        elif user.role == 'student':
            return redirect('student_dashboard')
        elif user.role == 'teacher':
            return redirect('teacher_dashboard')
        elif user.role == 'headmaster':
            return redirect('headmaster_dashboard')
        elif user.role == 'admin':
            return redirect('admin_dashboard')
        else:
            return redirect('public_home')

# Teacher Dashboard
@login_required
def teacher_dashboard(request):
    if not request.user.role == 'teacher':
        return redirect('public_home')
    
    context = {
        'user': request.user,
        'role': 'Teacher',
        'courses': Course.objects.all(),  # Will be filtered by teacher's assignments
        'students_count': User.objects.filter(role='student').count(),
    }
    return render(request, 'core/teacher_dashboard.html', context)

# Headmaster Dashboard
@login_required
def headmaster_dashboard(request):
    if not request.user.role == 'headmaster':
        return redirect('public_home')
    
    context = {
        'user': request.user,
        'role': 'Head of School',
        'total_students': User.objects.filter(role='student').count(),
        'total_teachers': User.objects.filter(role='teacher').count(),
        'total_staff': User.objects.filter(role__in=['teacher', 'admin', 'headmaster']).count(),
        'courses': Course.objects.all(),
    }
    return render(request, 'core/headmaster_dashboard.html', context)

# School Admin Dashboard
@login_required
def admin_dashboard(request):
    if not request.user.role == 'admin':
        return redirect('public_home')
    
    context = {
        'user': request.user,
        'role': 'School Administrator',
        'total_users': User.objects.all().count(),
        'students': User.objects.filter(role='student').count(),
        'teachers': User.objects.filter(role='teacher').count(),
        'pending_registrations': User.objects.filter(role__in=['teacher', 'headmaster', 'admin']).count(),
    }
    return render(request, 'core/admin_dashboard.html', context)

class BaseRegisterView(CreateView):
    from .forms import UserForm
    
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
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"User {user.username} created successfully")
            return redirect('user_management')
        messages.error(request, "Please correct the errors below.")
    else:
        form = UserForm()
    return render(request, 'core/add_user.html', {'form': form})

class UserDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = User
    template_name = 'core/user_detail.html'
    context_object_name = 'user'

    def test_func(self):
        return is_admin(self.request.user)

class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    from .forms import UserForm
    
    model = User
    form_class = UserForm
    template_name = 'core/edit_user.html'
    success_url = reverse_lazy('user_management')

    def test_func(self):
        return is_admin(self.request.user)

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
    template_name = 'core/course_list.html'
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
    template_name = 'core/course_detail.html'
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


class CreateCourseView(View):
    def get(self, request):
        from .forms import CourseForm
        form = CourseForm()
        return render(request, 'core/create_course.html', {'form': form})

    def post(self, request):
        from .forms import CourseForm
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('course_list')  # or another route
        return render(request, 'core/create_course.html', {'form': form})


        
class CourseUpdateView(UpdateView):
    model = Course
    fields = ['name', 'description', 'duration']  # Add the fields you want to be editable
    template_name = 'core/course_update.html'
    success_url = '/courses/manage/'  # Redirect to the course management page after update

    def get_object(self, queryset=None):
        # Ensure the course object is fetched based on the provided ID (pk)
        return get_object_or_404(Course, pk=self.kwargs['pk'])

class CourseDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Course
    template_name = 'core/course_confirm_delete.html'
    success_url = reverse_lazy('course_list')

    def test_func(self):
        return is_admin(self.request.user)

# ======================
# Student Views
# ======================
class StudentDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'core/student_dashboard.html'
    
    def test_func(self):
        return is_student(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student_profile
        
        # Get enrollments with related data
        enrollments = Enrollment.objects.filter(
            student=student
        ).select_related(
            'course_offering__course',
            'course_offering__faculty'
        ).prefetch_related('grade_set', 'attendance_set')
        
        # Calculate attendance percentages
        enriched_enrollments = []
        for enrollment in enrollments:
            total_classes = enrollment.attendance_set.count()
            present_classes = enrollment.attendance_set.filter(status='P').count()
            attendance_percentage = (present_classes / total_classes * 100) if total_classes > 0 else 0
            
            enriched_enrollments.append({
                'enrollment': enrollment,
                'attendance_percentage': attendance_percentage,
                'grade': enrollment.grade_set.first()
            })
        
        context.update({
            'student': student,
            'enrollments': enriched_enrollments,
            'upcoming_exams': ExamSchedule.objects.filter(
                course__in=[e.course_offering.course for e in enrollments],
                date__gte=timezone.now()
            ).order_by('date')[:5],
            'unpaid_fees': Fee.objects.filter(student=student, paid=False),
            'recent_announcements': Announcement.objects.filter(
                Q(target_audience='All') | Q(target_audience='Students')
            ).order_by('-created_at')[:5]
        })
        return context

class CreateCourseView(View):
    def get(self, request):
        return render(request, 'core/create_course.html')

@login_required
def enroll_course(request):
    if not is_student(request.user):
        return redirect('dashboard')
    
    student = request.user.student_profile
    available_courses = Course.objects.exclude(
        enrollments__student=student
    )
    
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        if course_id:
            course = get_object_or_404(Course, pk=course_id)
            Enrollment.objects.create(
                student=student,
                course_offering=course.current_offering(),
                enrollment_date=timezone.now()
            )
            messages.success(request, f"Successfully enrolled in {course.name}")
            return redirect('student_dashboard')
    
    return render(request, 'core/enroll_course.html', {
        'available_courses': available_courses
    })

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
def is_admin(user):
    return user.is_superuser or (hasattr(user, 'adminprofile') and user.adminprofile is not None)

# ======================
# Admin Views
# ======================
class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'core/admin_dashboard.html'
    
    def test_func(self):
        return is_admin(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # System statistics
        context.update({
            'total_students': StudentProfile.objects.count(),
            'total_faculty': FacultyProfile.objects.count(),
            'total_courses': Course.objects.count(),
            'active_enrollments': Enrollment.objects.count(),
            'pending_approvals': User.objects.filter(is_active=False).count(),
            'recent_activity': ActivityLog.objects.all().order_by('-timestamp')[:10]
        })
        return context

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

# ======================
# Attendance Views
# ======================
class AttendanceListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Attendance
    template_name = 'core/attendance_list.html'
    context_object_name = 'attendance_records'
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
            
        date = self.request.GET.get('date')
        if date:
            queryset = queryset.filter(date=date)
            
        return queryset.order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if is_admin(self.request.user):
            context['courses'] = Course.objects.all()
        else:
            context['courses'] = Course.objects.filter(
                courseoffering__faculty=self.request.user.faculty_profile
            ).distinct()
        return context

class AttendanceCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    from .forms import AttendanceForm
    
    model = Attendance
    form_class = AttendanceForm
    template_name = 'core/attendance_form.html'
    success_url = reverse_lazy('attendance_list')

    def test_func(self):
        return is_admin(self.request.user) or is_faculty(self.request.user)

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
    template_name = 'core/attendance_form.html'

    def test_func(self):
        if is_admin(self.request.user):
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
class FeeListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Fee
    template_name = 'core/fee_list.html'
    context_object_name = 'fees'
    paginate_by = 20

    def test_func(self):
        return is_admin(self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset().select_related('student__user', 'semester')
        
        student_id = self.request.GET.get('student')
        if student_id:
            queryset = queryset.filter(student_id=student_id)
            
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset.order_by('-due_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['students'] = StudentProfile.objects.all()
        return context

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
    announcements = Announcement.objects.filter(
        Q(target_audience='All') | 
        Q(target_audience='Students' if is_student(request.user) else 'Faculty')
    ).order_by('-created_at')
    
    return render(request, 'communication/announcements.html', {
        'announcements': announcements
    })

@login_required
def inbox(request):
    messages = Message.objects.filter(recipient=request.user).order_by('-sent_at')
    return render(request, 'communication/inbox.html', {'messages': messages})

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

    return render(request, 'communication/send_message.html', {
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
            'attendance': AttendanceRecord.objects.filter(student=child).order_by('-date')[:5],
            'grades': Grade.objects.filter(student=child).order_by('-awarded_on')[:5],
            'unpaid_fees': Fee.objects.filter(student=child, paid=False),
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
    attendance = AttendanceRecord.objects.filter(student=child).order_by('-date')
    
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
    context['attendance_stats'] = AttendanceRecord.objects.values(
        'status'
    ).annotate(
        count=Count('status')
    )
    
    return context






    # //Course


# Public-facing views
def public_home(request):
    """Public home page for visitors"""
    return render(request, 'core/public_home.html')

def public_about(request):
    """Public about page"""
    return render(request, 'core/public_about.html')

def public_courses(request):
    """Public courses catalog page"""
    return render(request, 'core/public_courses.html')

def public_admissions(request):
    """Public admissions page"""
    return render(request, 'core/public_admissions.html')

def public_contact(request):
    """Public contact page"""
    return render(request, 'core/public_contact.html')


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

def course_list(request):
    courses = Course.objects.all()
    return render(request, 'core/course_list.html', {'courses': courses})

def course_create(request):
    departments = Department.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        department_id = request.POST.get('department')
        credits = request.POST.get('credits')
        description = request.POST.get('description')
        syllabus = request.POST.get('syllabus')

        department = get_object_or_404(Department, id=department_id)

        Course.objects.create(
            name=name,
            code=code,
            department=department,
            credits=credits,
            description=description,
            syllabus=syllabus
        )
        messages.success(request, "Course created successfully.")
        return redirect('course_list')

    return render(request, 'core/course_form.html', {'departments': departments, 'title': 'Add Course'})

def course_update(request, pk):
    course = get_object_or_404(Course, pk=pk)
    departments = Department.objects.all()

    if request.method == 'POST':
        course.name = request.POST.get('name')
        course.code = request.POST.get('code')
        course.department = get_object_or_404(Department, id=request.POST.get('department'))
        course.credits = request.POST.get('credits')
        course.description = request.POST.get('description')
        course.syllabus = request.POST.get('syllabus')
        course.save()
        messages.success(request, "Course updated successfully.")
        return redirect('course_list')

    return render(request, 'core/course_form.html', {'course': course, 'departments': departments, 'title': 'Edit Course'})

def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.delete()
        messages.success(request, "Course deleted successfully.")
        return redirect('course_list')

    return render(request, 'core/course_confirm_delete.html', {'course': course})



