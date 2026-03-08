from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.utils import timezone
from django.db.models import Q
from .models import (
    Department, AdminProfile, StudentProfile, FacultyProfile,
    Course, CourseOffering, Enrollment, Grade, Attendance,
    Fee, FeeCategory, Semester, LeaveRequest,
    Message, ForumTopic, ForumPost, Material, NECTAExam, SchoolCalendar,
    Subject, SubjectEnrollment, Announcement, TimeTable, StudentClass, Assignment, BorrowedBook
)

User = get_user_model()

class UserUpdateForm(forms.ModelForm):
    """Form for updating user information (not creating new user)"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
                'placeholder': 'Last Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
                'placeholder': 'Email Address'
            }),
        }

class UserUpdateForm(forms.ModelForm):
    """Form for updating user information"""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Leave blank to keep current password'
        }),
        required=False
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Confirm new password'
        }),
        required=False
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
                'placeholder': 'Last Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
                'placeholder': 'Email Address'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and password != confirm_password:
            raise ValidationError("Passwords don't match")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = [
            'roll_number', 'department', 'admission_year', 'current_form', 'current_semester',
            'profile_picture', 'phone', 'address', 'necta_exam_number', 'birth_certificate_number',
            'previous_school', 'primary_school_leaving_exam_number'
        ]
        widgets = {
            'roll_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
                'placeholder': 'Roll Number'
            }),
            'department': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200'
            }),
            'admission_year': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
                'placeholder': 'Admission Year'
            }),
            'current_form': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200'
            }),
            'current_semester': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200'
            }),
            'profile_picture': forms.ClearableFileInput(attrs={
                'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
                'placeholder': 'Phone Number'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
                'rows': 3,
                'placeholder': 'Home Address'
            }),
            'necta_exam_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
                'placeholder': 'NECTA Exam Number'
            }),
            'birth_certificate_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
                'placeholder': 'Birth Certificate Number'
            }),
            'previous_school': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
                'placeholder': 'Previous School'
            }),
            'primary_school_leaving_exam_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
                'placeholder': 'Primary School Leaving Exam Number'
            }),
        }

class PublicUserRegistrationForm(UserCreationForm):
    """Registration form for students only"""
    # Hidden role field - always set to student for public registration
    role = forms.CharField(
        widget=forms.HiddenInput(),
        initial='student'
    )
    
    # Additional fields for detailed user information
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Enter phone number'
        }),
        help_text="Enter your phone number (optional)"
    )
    
    address = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
            'rows': 3,
            'placeholder': 'Enter your home address'
        }),
        help_text="Enter your complete home address (optional)"
    )
    
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
            'type': 'date'
        }),
        help_text="Enter your date of birth (optional)"
    )
    
    gender = forms.ChoiceField(
        choices=[('', 'Select Gender'), ('M', 'Male'), ('F', 'Female')],
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 bg-white'
        }),
        help_text="Select your gender (optional)"
    )
    
    necta_exam_number = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Enter NECTA exam number'
        }),
        help_text="Enter your NECTA examination number (optional)"
    )
    
    birth_certificate_number = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Enter birth certificate number'
        }),
        help_text="Enter your birth certificate number (optional)"
    )
    
    previous_school = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Enter previous school'
        }),
        help_text="Enter your previous school (optional)"
    )
    
    primary_school_leaving_exam_number = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Enter primary school leaving exam number'
        }),
        help_text="Enter your primary school leaving examination number (optional)"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Enter username'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Enter email address'})
        self.fields['first_name'].widget.attrs.update({'placeholder': 'Enter first name'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Enter last name'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.save()
        return user


# Admin User Creation Forms
class AdminCreateStudentForm(UserCreationForm):
    """Form for admins to create student accounts"""
    role = forms.CharField(
        widget=forms.HiddenInput(),
        initial='student'
    )
    
    # Additional student fields
    roll_number = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Enter roll number'
        })
    )
    
    admission_year = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Enter admission year'
        })
    )
    
    current_form = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Enter current form'
        })
    )
    
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Enter phone number'
        })
    )
    
    address = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
            'rows': 3,
            'placeholder': 'Enter address'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Tailwind CSS classes to all form fields
        for field_name, field in self.fields.items():
            if field_name != 'role':  # Skip the hidden role field
                field.widget.attrs.update({
                    'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200'
                })
                # Add placeholders for common fields
                if field_name == 'username':
                    field.widget.attrs['placeholder'] = 'Enter username'
                elif field_name == 'email':
                    field.widget.attrs['placeholder'] = 'Enter email address'
                elif field_name == 'first_name':
                    field.widget.attrs['placeholder'] = 'Enter first name'
                elif field_name == 'last_name':
                    field.widget.attrs['placeholder'] = 'Enter last name'
                elif field_name == 'password1':
                    field.widget.attrs['placeholder'] = 'Enter password'
                elif field_name == 'password2':
                    field.widget.attrs['placeholder'] = 'Confirm password'


class AdminCreateTeacherForm(UserCreationForm):
    """Form for admins/headmasters to create teacher accounts"""
    role = forms.CharField(
        widget=forms.HiddenInput(),
        initial='teacher'
    )
    
    # Teacher-specific fields
    employee_id = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Enter employee ID'
        })
    )
    
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200'
        })
    )
    
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Enter phone number'
        })
    )
    
    address = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
            'rows': 3,
            'placeholder': 'Enter address'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Tailwind CSS classes to all form fields
        for field_name, field in self.fields.items():
            if field_name != 'role':  # Skip the hidden role field
                field.widget.attrs.update({
                    'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200'
                })
                # Add placeholders for common fields
                if field_name == 'username':
                    field.widget.attrs['placeholder'] = 'Enter username'
                elif field_name == 'email':
                    field.widget.attrs['placeholder'] = 'Enter email address'
                elif field_name == 'first_name':
                    field.widget.attrs['placeholder'] = 'Enter first name'
                elif field_name == 'last_name':
                    field.widget.attrs['placeholder'] = 'Enter last name'
                elif field_name == 'password1':
                    field.widget.attrs['placeholder'] = 'Enter password'
                elif field_name == 'password2':
                    field.widget.attrs['placeholder'] = 'Confirm password'


class AdminCreateHeadmasterForm(UserCreationForm):
    """Form for admins to create headmaster accounts"""
    role = forms.CharField(
        widget=forms.HiddenInput(),
        initial='headmaster'
    )
    
    # Headmaster-specific fields
    employee_id = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Enter employee ID'
        })
    )
    
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Enter phone number'
        })
    )
    
    address = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
            'rows': 3,
            'placeholder': 'Enter address'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Tailwind CSS classes to all form fields
        for field_name, field in self.fields.items():
            if field_name != 'role':  # Skip the hidden role field
                field.widget.attrs.update({
                    'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200'
                })
                # Add placeholders for common fields
                if field_name == 'username':
                    field.widget.attrs['placeholder'] = 'Enter username'
                elif field_name == 'email':
                    field.widget.attrs['placeholder'] = 'Enter email address'
                elif field_name == 'first_name':
                    field.widget.attrs['placeholder'] = 'Enter first name'
                elif field_name == 'last_name':
                    field.widget.attrs['placeholder'] = 'Enter last name'
                elif field_name == 'password1':
                    field.widget.attrs['placeholder'] = 'Enter password'
                elif field_name == 'password2':
                    field.widget.attrs['placeholder'] = 'Confirm password'
