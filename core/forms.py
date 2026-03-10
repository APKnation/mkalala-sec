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
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
                'placeholder': 'Enter username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
                'placeholder': 'Enter email address'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
                'placeholder': 'Enter first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
                'placeholder': 'Enter last name'
            }),
            'role': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 bg-white'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Enter username'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Enter email address'})
        self.fields['first_name'].widget.attrs.update({'placeholder': 'Enter first name'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Enter last name'})
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        
        if password:
            user.set_password(password)
        
        if commit:
            user.save()
        
        return user

class UserForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Enter username'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Enter email address'})
        self.fields['first_name'].widget.attrs.update({'placeholder': 'Enter first name'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Enter last name'})

class PublicUserRegistrationForm(UserCreationForm):
    """Registration form for students only"""
    # Hidden role field - always set to student for public registration
    role = forms.CharField(
        widget=forms.HiddenInput(),
        initial='student'
    )
    
    # Name fields for personalization
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Enter first name'
        }),
        help_text="Enter your first name"
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Enter last name'
        }),
        help_text="Enter your last name"
    )
    
    # Additional fields for detailed user information
    date_of_birth = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
            'type': 'date'
        }),
        help_text="Enter your date of birth"
    )
    
    gender = forms.ChoiceField(
        choices=[('', 'Select Gender'), ('M', 'Male'), ('F', 'Female')],
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 bg-white'
        }),
        help_text="Select your gender"
    )
    
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
        help_text="Enter your previous school attended (optional)"
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2', 
                  'phone', 'address', 'date_of_birth', 'gender', 
                  'birth_certificate_number', 'previous_school']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
                'placeholder': 'Enter username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
                'placeholder': 'Enter email address'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
                'placeholder': 'Enter first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
                'placeholder': 'Enter last name'
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
                'placeholder': 'Enter password',
                'id': 'id_password1'
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
                'placeholder': 'Confirm password',
                'id': 'id_password2'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
                'placeholder': 'Enter phone number'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
                'rows': 3,
                'placeholder': 'Enter your home address'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200'
            }),
            'birth_certificate_number': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
                'placeholder': 'Enter birth certificate number'
            }),
            'previous_school': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
                'placeholder': 'Enter previous school'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].label = "Select Your Role"
        self.fields['role'].help_text = "Choose your role in the school system"
        # Update widget classes for new fields
        self.fields['phone'].widget.attrs.update({'class': 'form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200'})
        self.fields['address'].widget.attrs.update({'class': 'form-textarea w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200'})
        self.fields['date_of_birth'].widget.attrs.update({'class': 'form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200'})
        self.fields['gender'].widget.attrs.update({'class': 'form-select w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200'})
        self.fields['birth_certificate_number'].widget.attrs.update({'class': 'form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200'})
        self.fields['previous_school'].widget.attrs.update({'class': 'form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200'})

class StaffRegistrationForm(UserCreationForm):
    """Registration form for staff roles (teacher, headmaster, admin)"""
    role = forms.ChoiceField(
        choices=[
            ('teacher', 'Teacher'),
            ('headmaster', 'Head of School'),
            ('admin', 'School Admin'),
        ],
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ['password1', 'password2']:
            self.fields[field].widget.attrs.update({
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            })
        self.fields['username'].help_text = None

class FacultyUserForm(UserCreationForm):
    """Form for creating faculty users by admin"""
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = None

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_faculty = True
        user.role = 'teacher'
        if commit:
            user.save()
        return user

    def clean(self):
        cleaned_data = super().clean()
        roles = ['is_student', 'is_faculty', 'is_admin', 'is_parent']
        if sum(1 for role in roles if cleaned_data.get(role)) > 1:
            raise ValidationError("User can only have one role.")
        return cleaned_data



class CourseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Tailwind classes to all fields automatically
        for field_name, field in self.fields.items():
            if field.widget.input_type == 'select':
                field.widget.attrs.update({
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:placeholder-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500'
                })
            elif field.widget.input_type == 'textarea':
                field.widget.attrs.update({
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:placeholder-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500',
                    'rows': 3
                })
            else:
                field.widget.attrs.update({
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:placeholder-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500'
                })

    class Meta:
        model = Course
        fields = ['name', 'code', 'department', 'credits', 'description']
        labels = {
            'name': 'Course Name',
            'code': 'Course Code',
            'department': 'Department',
            'credits': 'Credit Hours',
            'description': 'Description'
        }
        help_texts = {
            'code': 'Enter course code in uppercase (e.g., CS101)',
            'credits': 'Number of credit hours for this course'
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_code(self):
        code = self.cleaned_data.get('code')
        if not code.isupper():
            raise forms.ValidationError("Course code must be in uppercase.")
        return code

    def clean_credits(self):
        credits = self.cleaned_data.get('credits')
        if credits <= 0:
            raise forms.ValidationError("Credit hours must be greater than zero.")
        return credits




class UserUpdateForm(UserChangeForm):
    password = None

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'profile_picture']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 bg-gray-100',
                'readonly': 'readonly'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'profile_picture': forms.ClearableFileInput(attrs={
                'class': 'w-full px-3 py-2 text-gray-700 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
        }

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = [
            'roll_number', 'department', 'admission_year', 'current_form', 'current_semester',
            'profile_picture', 'phone', 'address', 
            'necta_exam_number', 'birth_certificate_number',
            'previous_school', 'primary_school_leaving_exam_number'
        ]
        widgets = {
            'roll_number': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'department': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'admission_year': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'current_form': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'current_semester': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'profile_picture': forms.ClearableFileInput(attrs={
                'class': 'w-full px-3 py-2 text-gray-700 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': '+255 XXX XXX XXX'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 3,
                'placeholder': 'Enter your residential address'
            }),
            'necta_exam_number': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'PS123456789'
            }),
            'birth_certificate_number': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'BC123456789'
            }),
            'previous_school': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Previous school name'
            }),
            'primary_school_leaving_exam_number': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'PSLE123456789'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['roll_number'].widget.attrs.update({'placeholder': 'Enter roll number'})
        self.fields['phone'].widget.attrs.update({'placeholder': 'Enter phone number'})
        self.fields['address'].widget.attrs.update({'placeholder': 'Enter address'})
        
        # Filter departments to show only O-level departments for O-level students
        if self.instance and self.instance.pk and self.instance.department.education_level == 'olevel':
            self.fields['department'].queryset = Department.objects.filter(education_level='olevel')
        
        # Make current_semester optional for O-level students
        if self.instance and self.instance.pk and self.instance.department.education_level == 'olevel':
            self.fields['current_semester'].required = False
            self.fields['current_form'].required = True
        else:
            self.fields['current_semester'].required = True
            self.fields['current_form'].required = False

class FacultyProfileForm(forms.ModelForm):
    class Meta:
        model = FacultyProfile
        fields = ['department', 'designation', 'specialization', 'profile_picture']
        widgets = {
            'department': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'designation': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'specialization': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 3
            }),
            'profile_picture': forms.ClearableFileInput(attrs={
                'class': 'w-full px-3 py-2 text-gray-700 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
        }

class AdminProfileForm(forms.ModelForm):
    class Meta:
        model = AdminProfile
        fields = ['department', 'access_level', 'profile_picture']
        widgets = {
            'department': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'access_level': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'profile_picture': forms.ClearableFileInput(attrs={
                'class': 'w-full px-3 py-2 text-gray-700 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
        }

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['code', 'name', 'slug', 'description']
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if not slug:
            slug = slugify(f"{self.cleaned_data.get('code')}-{self.cleaned_data.get('name')}")
        return slug

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'code', 'department', 'credits', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'code': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'department': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'credits': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
        }

    def clean_code(self):
        code = self.cleaned_data.get('code')
        if not code.isupper():
            raise ValidationError("Course code must be in uppercase.")
        return code

class CourseOfferingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['faculty'].queryset = FacultyProfile.objects.select_related('user')
        self.fields['course'].queryset = Course.objects.select_related('department')
        self.fields['semester'].queryset = Semester.objects.all()

    class Meta:
        model = CourseOffering
        fields = ['course', 'faculty', 'semester', 'section']
        widgets = {
            'course': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'faculty': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'semester': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
        }


class AssignmentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter course offerings to only show courses taught by the current teacher
        if 'teacher' in kwargs:
            teacher = kwargs.pop('teacher')
            self.fields['course_offering'].queryset = CourseOffering.objects.filter(
                faculty=teacher
            ).select_related('course', 'semester')
    
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'course_offering', 'due_date', 'max_marks']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Enter assignment title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 4,
                'placeholder': 'Enter assignment description'
            }),
            'course_offering': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'type': 'date'
            }),
            'max_marks': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Maximum marks',
                'min': 1
            }),
        }


class BookBorrowForm(forms.ModelForm):
    class Meta:
        model = BorrowedBook
        fields = ['book']
        widgets = {
            'book': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
        }

class EnrollmentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        course_offering = kwargs.pop('course_offering', None)
        super().__init__(*args, **kwargs)
        if course_offering:
            self.fields['course_offering'].initial = course_offering
            self.fields['course_offering'].disabled = True
            self.fields['student'].queryset = StudentProfile.objects.exclude(
                enrollments__course_offering=course_offering
            ).select_related('user')

    class Meta:
        model = Enrollment
        fields = ['student', 'course_offering']
        widgets = {
            'student': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'course_offering': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 bg-gray-100'
            }),
        }

class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['enrollment', 'grade', 'remarks']
        widgets = {
            'enrollment': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'grade': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'remarks': forms.Textarea(attrs={
                'rows': 2,
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
        }

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['enrollment', 'date', 'status']
        widgets = {
            'enrollment': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
        }

class FeeForm(forms.ModelForm):
    class Meta:
        model = Fee
        fields = ['student', 'category', 'amount', 'due_date', 'paid_date', 'is_paid', 'semester']
        widgets = {
            'student': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'due_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'paid_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'is_paid': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'
            }),
            'semester': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('is_paid') and not cleaned_data.get('paid_date'):
            raise ValidationError("Paid date is required when fee is marked as paid.")
        return cleaned_data

class LeaveRequestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and hasattr(user, 'studentprofile'):
            self.fields['student'].initial = user.studentprofile
            self.fields['student'].disabled = True
        self.fields['course'].queryset = Course.objects.select_related('department')

    class Meta:
        model = LeaveRequest
        fields = ['student', 'course', 'start_date', 'end_date', 'reason']
        widgets = {
            'student': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 bg-gray-100'
            }),
            'course': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'reason': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date and start_date > end_date:
            raise ValidationError("End date must be after start date.")
        return cleaned_data

class NECTAExamForm(forms.ModelForm):
    class Meta:
        model = NECTAExam
        fields = [
            'student', 'exam_type', 'subject', 'grade', 'marks_obtained', 
            'exam_year', 'exam_month', 'is_mock', 'remarks'
        ]
        widgets = {
            'student': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'exam_type': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'subject': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'grade': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'marks_obtained': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'min': '0', 'max': '100'
            }),
            'exam_year': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'min': '2020', 'max': '2035'
            }),
            'exam_month': forms.Select(choices=[(i, i) for i in range(1, 13)], attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'is_mock': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500'
            }),
            'remarks': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 3
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter students to only show O-level students for NECTA exams
        self.fields['student'].queryset = StudentProfile.objects.filter(
            department__education_level='olevel'
        ).select_related('user')

class SchoolCalendarForm(forms.ModelForm):
    class Meta:
        model = SchoolCalendar
        fields = [
            'academic_year', 'term', 'start_date', 'end_date', 
            'teaching_weeks', 'exam_weeks', 'holiday_weeks'
        ]
        widgets = {
            'academic_year': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'term': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'type': 'date'
            }),
            'teaching_weeks': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'min': '1', 'max': '20'
            }),
            'exam_weeks': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'min': '1', 'max': '10'
            }),
            'holiday_weeks': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'min': '1', 'max': '20'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date and start_date > end_date:
            raise ValidationError("End date must be after start date.")
        return cleaned_data

class MaterialUploadForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['course', 'title', 'file', 'description']
        widgets = {
            'course': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'title': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'file': forms.ClearableFileInput(attrs={
                'class': 'w-full px-3 py-2 text-gray-700 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 3
            }),
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['recipient', 'subject', 'body']
        widgets = {
            'recipient': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'body': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 4
            }),
        }

class ForumTopicForm(forms.ModelForm):
    class Meta:
        model = ForumTopic
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
        }

class ForumPostForm(forms.ModelForm):
    class Meta:
        model = ForumPost
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 4
            }),
        }

class SubjectEnrollmentForm(forms.ModelForm):
    """Form for enrolling students in Tanzanian O-Level subjects"""
    class Meta:
        model = SubjectEnrollment
        fields = ['subject', 'academic_year']
        widgets = {
            'subject': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'academic_year': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'min': 2020,
                'max': 2030
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter subjects based on student's current form level
        if 'student' in self.initial:
            student = self.initial['student']
            if hasattr(student, 'current_form'):
                form_level = str(student.current_form)
                self.fields['subject'].queryset = Subject.objects.filter(form_level=form_level)

class BulkSubjectEnrollmentForm(forms.Form):
    """Form for bulk enrollment of students in subjects"""
    academic_year = forms.IntegerField(
        min_value=2020,
        max_value=2030,
        initial=timezone.now().year,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['academic_year'].initial = timezone.now().year

class SubjectForm(forms.ModelForm):
    """Form for creating and editing subjects"""
    class Meta:
        model = Subject
        fields = ['code', 'name', 'form_level', 'is_core', 'is_optional']
        widgets = {
            'code': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'form_level': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'is_core': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'
            }),
            'is_optional': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        is_core = cleaned_data.get('is_core')
        is_optional = cleaned_data.get('is_optional')
        
        if is_core and is_optional:
            raise forms.ValidationError("A subject cannot be both core and optional.")
        
        return cleaned_data

class ClassForm(forms.ModelForm):
    """Form for creating and managing classes"""
    class Meta:
        model = StudentProfile
        fields = ['current_form']
        widgets = {
            'current_form': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['current_form'].label = "Form Level"
        self.fields['current_form'].help_text = "Select the form level for this student"
class AnnouncementForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Add common Tailwind classes to all fields
        for field_name, field in self.fields.items():
            if field_name not in ['target_class']:  # Handle target_class separately
                field.widget.attrs.update({
                    'class': (
                        'w-full px-4 py-3 bg-white border border-slate-200 rounded-xl '
                        'text-sm font-medium text-slate-900 placeholder-slate-500 '
                        'focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500/50 '
                        'focus:outline-none transition-all duration-200 shadow-sm '
                        'hover:border-slate-300 hover:shadow-md'
                    )
                })
        
        # Filter target audience options based on user role
        if user and hasattr(user, 'role'):
            if user.role == 'teacher':
                # Teachers can only create announcements for students and specific classes
                self.fields['target_audience'].choices = [
                    ('Students', 'All Students'),
                    ('Class', 'Specific Class'),
                ]
            elif user.role == 'admin':
                # Admins can create announcements for all audiences
                self.fields['target_audience'].choices = [
                    ('All', 'Everyone'),
                    ('Students', 'All Students'),
                    ('Faculty', 'All Faculty'),
                    ('Parents', 'All Parents'),
                    ('Class', 'Specific Class'),
                ]
        
        # Initialize target_class field with enhanced styling
        self.fields['target_class'] = forms.ModelChoiceField(
            queryset=StudentClass.objects.all(),
            required=False,
            empty_label="Select a class",
            widget=forms.Select(attrs={
                'class': (
                    'w-full px-4 py-3 bg-white border border-slate-200 rounded-xl '
                    'text-sm font-medium text-slate-900 focus:ring-4 focus:ring-blue-500/10 '
                    'focus:border-blue-500/50 focus:outline-none transition-all duration-200 '
                    'shadow-sm hover:border-slate-300 hover:shadow-md appearance-none cursor-pointer'
                )
            })
        )
        
        # Update specific field attributes
        self.fields['title'].widget.attrs.update({
            'placeholder': 'Enter announcement title...',
            'autocomplete': 'off'
        })
        
        self.fields['message'].widget.attrs.update({
            'placeholder': 'Write your announcement message...',
            'rows': 4,
            'class': (
                'w-full px-4 py-3 bg-white border border-slate-200 rounded-xl '
                'text-sm font-medium text-slate-900 placeholder-slate-500 '
                'focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500/50 '
                'focus:outline-none transition-all duration-200 shadow-sm resize-y '
                'hover:border-slate-300 hover:shadow-md min-h-[120px]'
            )
        })
        
        self.fields['target_audience'].widget.attrs.update({
            'class': (
                'w-full px-4 py-3 bg-white border border-slate-200 rounded-xl '
                'text-sm font-medium text-slate-900 focus:ring-4 focus:ring-blue-500/10 '
                'focus:border-blue-500/50 focus:outline-none transition-all duration-200 '
                'shadow-sm hover:border-slate-300 hover:shadow-md appearance-none cursor-pointer'
            )
        })
        
        self.fields['expires_at'].widget.attrs.update({
            'type': 'datetime-local',
            'class': (
                'w-full px-4 py-3 bg-white border border-slate-200 rounded-xl '
                'text-sm font-medium text-slate-900 focus:ring-4 focus:ring-blue-500/10 '
                'focus:border-blue-500/50 focus:outline-none transition-all duration-200 '
                'shadow-sm hover:border-slate-300 hover:shadow-md cursor-pointer'
            )
        })
    
    class Meta:
        model = Announcement
        fields = ['title', 'message', 'target_audience', 'target_class', 'expires_at']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-white border border-slate-200 rounded-xl text-sm font-medium text-slate-900 placeholder-slate-500 focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500/50 focus:outline-none transition-all duration-200 shadow-sm hover:border-slate-300 hover:shadow-md',
                'placeholder': 'Enter announcement title...'
            }),
            'message': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 bg-white border border-slate-200 rounded-xl text-sm font-medium text-slate-900 placeholder-slate-500 focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500/50 focus:outline-none transition-all duration-200 shadow-sm resize-y hover:border-slate-300 hover:shadow-md min-h-[120px]',
                'placeholder': 'Write your announcement message...'
            }),
            'target_audience': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-white border border-slate-200 rounded-xl text-sm font-medium text-slate-900 focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500/50 focus:outline-none transition-all duration-200 shadow-sm hover:border-slate-300 hover:shadow-md appearance-none cursor-pointer'
            }),
            'expires_at': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'w-full px-4 py-3 bg-white border border-slate-200 rounded-xl text-sm font-medium text-slate-900 focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500/50 focus:outline-none transition-all duration-200 shadow-sm hover:border-slate-300 hover:shadow-md cursor-pointer'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        target_audience = cleaned_data.get('target_audience')
        target_class = cleaned_data.get('target_class')
        
        # If target audience is 'Class', then target_class is required
        if target_audience == 'Class' and not target_class:
            raise forms.ValidationError("Please select a class when targeting a specific class.")
        
        # If target audience is not 'Class', clear target_class
        if target_audience != 'Class':
            cleaned_data['target_class'] = None
        
        return cleaned_data


class TimeTableForm(forms.ModelForm):
    class Meta:
        model = TimeTable
        fields = ['course_offering', 'day', 'start_time', 'end_time', 'room', 'semester']
        widgets = {
            'course_offering': forms.Select(attrs={'class': 'w-full px-4 py-3 bg-slate-50 border border-slate-100 rounded-xl text-sm font-medium focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500/50 outline-none appearance-none'}),
            'day': forms.Select(attrs={'class': 'w-full px-4 py-3 bg-slate-50 border border-slate-100 rounded-xl text-sm font-medium focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500/50 outline-none appearance-none'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'w-full px-4 py-3 bg-slate-50 border border-slate-100 rounded-xl text-sm font-medium focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500/50 outline-none'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'w-full px-4 py-3 bg-slate-50 border border-slate-100 rounded-xl text-sm font-medium focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500/50 outline-none'}),
            'room': forms.TextInput(attrs={'class': 'w-full px-4 py-3 bg-slate-50 border border-slate-100 rounded-xl text-sm font-medium focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500/50 outline-none'}),
            'semester': forms.Select(attrs={'class': 'w-full px-4 py-3 bg-slate-50 border border-slate-100 rounded-xl text-sm font-medium focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500/50 outline-none appearance-none'}),
        }
