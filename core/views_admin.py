# Admin User Creation Views
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms_admin import AdminCreateStudentForm, AdminCreateTeacherForm, AdminCreateHeadmasterForm
from .models import StudentProfile, FacultyProfile, HeadmasterProfile
from .utils import is_admin, is_headmaster
from django.utils import timezone

@login_required
@user_passes_test(is_admin)
def admin_create_student(request):
    """View for admins to create student accounts"""
    if request.method == 'POST':
        form = AdminCreateStudentForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            
            # Set user role and flags
            user.role = 'student'
            user.is_student = True
            user.save()
            
            # Create StudentProfile
            StudentProfile.objects.create(
                user=user,
                roll_number=form.cleaned_data['roll_number'],
                admission_year=form.cleaned_data['admission_year'],
                current_form=form.cleaned_data['current_form'],
                current_semester=1,
                phone=form.cleaned_data.get('phone', ''),
                address=form.cleaned_data.get('address', ''),
            )
            
            messages.success(request, f"Student account for {user.get_full_name()} created successfully!")
            return redirect('admin_unified_dashboard', page='users')
    else:
        form = AdminCreateStudentForm()
    
    return render(request, 'core/admin/create_student.html', {
        'form': form,
        'title': 'Create Student Account'
    })

@login_required
@user_passes_test(is_admin)
def admin_create_teacher(request):
    """View for admins to create teacher accounts"""
    if request.method == 'POST':
        form = AdminCreateTeacherForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            
            # Set user role and flags
            user.role = 'teacher'
            user.is_faculty = True
            user.save()
            
            # Create FacultyProfile
            FacultyProfile.objects.create(
                user=user,
                employee_id=form.cleaned_data['employee_id'],
                department=form.cleaned_data['department'],
                phone=form.cleaned_data.get('phone', ''),
                address=form.cleaned_data.get('address', ''),
                date_joined=timezone.now().date()
            )
            
            messages.success(request, f"Teacher account for {user.get_full_name()} created successfully!")
            return redirect('admin_unified_dashboard', page='users')
    else:
        form = AdminCreateTeacherForm()
    
    return render(request, 'core/admin/create_teacher.html', {
        'form': form,
        'title': 'Create Teacher Account'
    })

@login_required
@user_passes_test(is_admin)
def admin_create_headmaster(request):
    """View for admins to create headmaster accounts"""
    if request.method == 'POST':
        form = AdminCreateHeadmasterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            
            # Set user role and flags
            user.role = 'headmaster'
            user.is_headmaster = True
            user.save()
            
            # Create HeadmasterProfile
            HeadmasterProfile.objects.create(
                user=user,
                employee_id=form.cleaned_data['employee_id'],
                phone=form.cleaned_data.get('phone', ''),
                address=form.cleaned_data.get('address', ''),
                date_joined=timezone.now().date()
            )
            
            messages.success(request, f"Headmaster account for {user.get_full_name()} created successfully!")
            return redirect('admin_unified_dashboard', page='users')
    else:
        form = AdminCreateHeadmasterForm()
    
    return render(request, 'core/admin/create_headmaster.html', {
        'form': form,
        'title': 'Create Headmaster Account'
    })

@login_required
@user_passes_test(lambda u: u.is_headmaster or u.is_admin)
def headmaster_create_student(request):
    """View for headmasters to create student accounts"""
    if request.method == 'POST':
        form = AdminCreateStudentForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            
            # Set user role and flags
            user.role = 'student'
            user.is_student = True
            user.save()
            
            # Create StudentProfile
            StudentProfile.objects.create(
                user=user,
                roll_number=form.cleaned_data['roll_number'],
                admission_year=form.cleaned_data['admission_year'],
                current_form=form.cleaned_data['current_form'],
                current_semester=1,
                phone=form.cleaned_data.get('phone', ''),
                address=form.cleaned_data.get('address', ''),
            )
            
            messages.success(request, f"Student account for {user.get_full_name()} created successfully!")
            return redirect('headmaster_unified_dashboard', page='users')
    else:
        form = AdminCreateStudentForm()
    
    return render(request, 'core/headmaster/create_student.html', {
        'form': form,
        'title': 'Create Student Account'
    })

@login_required
@user_passes_test(is_headmaster)
def headmaster_create_teacher(request):
    """View for headmasters to create teacher accounts"""
    if request.method == 'POST':
        form = AdminCreateTeacherForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            
            # Set user role and flags
            user.role = 'teacher'
            user.is_faculty = True
            user.save()
            
            # Create FacultyProfile
            FacultyProfile.objects.create(
                user=user,
                employee_id=form.cleaned_data['employee_id'],
                department=form.cleaned_data['department'],
                phone=form.cleaned_data.get('phone', ''),
                address=form.cleaned_data.get('address', ''),
                date_joined=timezone.now().date()
            )
            
            messages.success(request, f"Teacher account for {user.get_full_name()} created successfully!")
            return redirect('headmaster_unified_dashboard', page='users')
    else:
        form = AdminCreateTeacherForm()
    
    return render(request, 'core/headmaster/create_teacher.html', {
        'form': form,
        'title': 'Create Teacher Account'
    })
