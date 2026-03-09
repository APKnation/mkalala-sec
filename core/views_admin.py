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
def admin_edit_student(request, student_id):
    """View for admins to edit student accounts"""
    from django.shortcuts import get_object_or_404
    from .models import StudentProfile
    from .forms import AdminCreateStudentForm
    
    # Get student to edit
    student = get_object_or_404(StudentProfile, id=student_id)
    
    # Handle form submission
    if request.method == 'POST':
        form = AdminCreateStudentForm(request.POST, instance=student.user)
        if form.is_valid():
            user = form.save()
            
            # Update student profile fields
            student.roll_number = form.cleaned_data['roll_number']
            student.admission_year = form.cleaned_data['admission_year']
            student.current_form = form.cleaned_data['current_form']
            student.current_semester = form.cleaned_data['current_semester']
            student.phone = form.cleaned_data.get('phone', '')
            student.address = form.cleaned_data.get('address', '')
            student.save()
            
            messages.success(request, f'Student "{user.get_full_name()}" has been updated successfully!')
            return redirect('admin_unified_dashboard', page='students')
    else:
        form = AdminCreateStudentForm(instance=student.user)
    
    return render(request, 'core/admin/edit_student.html', {
        'form': form,
        'student': student,
        'title': 'Edit Student Account'
    })

@login_required
@user_passes_test(is_admin)
def admin_delete_student(request, student_id):
    """View for admins to delete student accounts"""
    from django.shortcuts import get_object_or_404
    from .models import StudentProfile
    
    # Get student to delete
    student = get_object_or_404(StudentProfile, id=student_id)
    
    # Handle deletion
    if request.method == 'POST':
        confirm_text = request.POST.get('confirm_text', '').strip()
        
        if confirm_text != 'DELETE':
            messages.error(request, 'Invalid confirmation. Please type DELETE exactly to confirm.')
            return redirect('admin_unified_dashboard', page='delete-student') + f'?student_id={student_id}'
        
        student_name = student.user.get_full_name()
        student_roll_number = student.roll_number
        
        # Delete student profile and user
        student.user.delete()
        
        messages.success(request, f'Student "{student_name}" (Roll No: {student_roll_number}) has been deleted successfully!')
        return redirect('admin_unified_dashboard', page='students')
    
    return render(request, 'core/admin/delete_student.html', {
        'student': student,
        'title': 'Delete Student Account'
    })

@login_required
@user_passes_test(is_admin)
def admin_edit_teacher(request, teacher_id):
    """View for admins to edit teacher accounts"""
    from django.shortcuts import get_object_or_404
    from .models import FacultyProfile
    from .forms import AdminCreateTeacherForm
    
    # Get teacher to edit
    teacher = get_object_or_404(FacultyProfile, id=teacher_id)
    
    # Handle form submission
    if request.method == 'POST':
        form = AdminCreateTeacherForm(request.POST, instance=teacher.user)
        if form.is_valid():
            user = form.save()
            
            # Update teacher profile fields
            teacher.employee_id = form.cleaned_data['employee_id']
            teacher.department = form.cleaned_data['department']
            teacher.phone = form.cleaned_data.get('phone', '')
            teacher.address = form.cleaned_data.get('address', '')
            teacher.save()
            
            messages.success(request, f'Teacher "{user.get_full_name()}" has been updated successfully!')
            return redirect('admin_unified_dashboard', page='teachers')
    else:
        form = AdminCreateTeacherForm(instance=teacher.user)
    
    return render(request, 'core/admin/edit_teacher.html', {
        'form': form,
        'teacher': teacher,
        'title': 'Edit Teacher Account'
    })

@login_required
@user_passes_test(is_admin)
def admin_delete_teacher(request, teacher_id):
    """View for admins to delete teacher accounts"""
    from django.shortcuts import get_object_or_404
    from .models import FacultyProfile
    
    # Get teacher to delete
    teacher = get_object_or_404(FacultyProfile, id=teacher_id)
    
    # Handle deletion
    if request.method == 'POST':
        confirm_text = request.POST.get('confirm_text', '').strip()
        
        if confirm_text != 'DELETE':
            messages.error(request, 'Invalid confirmation. Please type DELETE exactly to confirm.')
            return redirect('admin_unified_dashboard', page='delete-teacher') + f'?teacher_id={teacher_id}'
        
        teacher_name = teacher.user.get_full_name()
        teacher_employee_id = teacher.employee_id
        
        # Delete teacher profile and User
        teacher.user.delete()
        
        messages.success(request, f'Teacher "{teacher_name}" (Employee ID: {teacher_employee_id}) has been deleted successfully!')
        return redirect('admin_unified_dashboard', page='teachers')
    
    return render(request, 'core/admin/delete_teacher.html', {
        'teacher': teacher,
        'title': 'Delete Teacher Account'
    })

@login_required
@user_passes_test(is_admin)
def admin_edit_headmaster(request, headmaster_id):
    """View for admins to edit headmaster accounts"""
    from django.shortcuts import get_object_or_404
    from .models import HeadmasterProfile
    from .forms import AdminCreateHeadmasterForm
    
    # Get headmaster to edit
    headmaster = get_object_or_404(HeadmasterProfile, id=headmaster_id)
    
    # Handle form submission
    if request.method == 'POST':
        form = AdminCreateHeadmasterForm(request.POST, instance=headmaster.user)
        if form.is_valid():
            user = form.save()
            
            # Update headmaster profile fields
            headmaster.employee_id = form.cleaned_data['employee_id']
            headmaster.phone = form.cleaned_data.get('phone', '')
            headmaster.address = form.cleaned_data.get('address', '')
            headmaster.save()
            
            messages.success(request, f'Headmaster "{user.get_full_name()}" has been updated successfully!')
            return redirect('admin_unified_dashboard', page='users')
    else:
        form = AdminCreateHeadmasterForm(instance=headmaster.user)
    
    return render(request, 'core/admin/edit_headmaster.html', {
        'form': form,
        'headmaster': headmaster,
        'title': 'Edit Headmaster Account'
    })

@login_required
@user_passes_test(is_admin)
def admin_delete_headmaster(request, headmaster_id):
    """View for admins to delete headmaster accounts"""
    from django.shortcuts import get_object_or_404
    from .models import HeadmasterProfile
    
    # Get headmaster to delete
    headmaster = get_object_or_404(HeadmasterProfile, id=headmaster_id)
    
    # Handle deletion
    if request.method == 'POST':
        confirm_text = request.POST.get('confirm_text', '').strip()
        
        if confirm_text != 'DELETE':
            messages.error(request, 'Invalid confirmation. Please type DELETE exactly to confirm.')
            return redirect('admin_unified_dashboard', page='delete-headmaster') + f'?headmaster_id={headmaster_id}'
        
        headmaster_name = headmaster.user.get_full_name()
        headmaster_employee_id = headmaster.employee_id
        
        # Delete headmaster profile and User
        headmaster.user.delete()
        
        messages.success(request, f'Headmaster "{headmaster_name}" (Employee ID: {headmaster_employee_id}) has been deleted successfully!')
        return redirect('admin_unified_dashboard', page='users')
    
    return render(request, 'core/admin/delete_headmaster.html', {
        'headmaster': headmaster,
        'title': 'Delete Headmaster Account'
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
