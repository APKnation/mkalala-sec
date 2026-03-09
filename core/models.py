from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.utils.text import slugify


# Constants for consistent field lengths
MAX_NAME_LENGTH = 100
MAX_TITLE_LENGTH = 255
MAX_CODE_LENGTH = 20

class Department(models.Model):
    EDUCATION_LEVEL_CHOICES = [
        ('olevel', 'O-Level (Form 1-4)'),
        ('alevel', 'A-Level (Form 5-6)'),
        ('primary', 'Primary School'),
        ('tertiary', 'Tertiary/University'),
    ]
    
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=MAX_NAME_LENGTH)
    education_level = models.CharField(max_length=10, choices=EDUCATION_LEVEL_CHOICES, default='olevel')
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        indexes = [models.Index(fields=['code'])]

    def __str__(self):
        return f"{self.code} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.code}-{self.name}")
        super().save(*args, **kwargs)

class Subject(models.Model):
    """Tanzanian O-Level National Curriculum Subjects"""
    SUBJECT_CHOICES = [
        ('MAT', 'Mathematics'),
        ('ENG', 'English Language'),
        ('PHY', 'Physics'),
        ('CHE', 'Chemistry'),
        ('KIS', 'Kiswahili'),
        ('BIO', 'Biology'),
        ('HIS', 'History'),
        ('GEO', 'Geography'),
        ('CIV', 'Civics'),
        ('COM', 'Commerce'),
        ('BK', 'Book Keeping'),
        ('ICS', 'Information and Computer Studies'),
        ('PE', 'Physical Education'),
    ]
    
    FORM_LEVELS = [
        ('1', 'Form 1'),
        ('2', 'Form 2'),
        ('3', 'Form 3'),
        ('4', 'Form 4'),
    ]
    
    code = models.CharField(max_length=5, choices=SUBJECT_CHOICES, unique=True)
    name = models.CharField(max_length=100)
    form_level = models.CharField(max_length=1, choices=FORM_LEVELS)
    is_core = models.BooleanField(default=True, help_text="Core subjects are compulsory")
    is_optional = models.BooleanField(default=False, help_text="Optional subjects can be chosen by students")
    
    class Meta:
        ordering = ['form_level', 'code']
        unique_together = ['code', 'form_level']
    
    def __str__(self):
        return f"{self.get_code_display()} - Form {self.form_level}"
    
    @property
    def full_name(self):
        return f"{self.get_code_display()} - Form {self.form_level}"

class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', _('Student')),
        ('teacher', _('Teacher')),
        ('headmaster', _('Head of School')),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    is_student = models.BooleanField(default=False)
    is_faculty = models.BooleanField(default=False)
    is_parent = models.BooleanField(default=False)
    is_headmaster = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        related_name='custom_user_set',
        related_query_name='custom_user',
    )

    def get_profile_picture_url(self):
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        return '/static/images/default-avatar.png'
    
    def is_normal_user(self):
        return self.role == 'normal'
    
    def is_teacher_role(self):
        return self.role == 'teacher'
    
    def is_headmaster_role(self):
        return self.role == 'headmaster'
    
    def is_school_admin(self):
        return self.role == 'admin'
    
    def get_role_display_name(self):
        return dict(self.ROLE_CHOICES).get(self.role, 'Unknown')

class StudentProfile(models.Model):
    FORM_CHOICES = [
        (1, 'Form 1'),
        (2, 'Form 2'),
        (3, 'Form 3'),
        (4, 'Form 4'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    roll_number = models.CharField(max_length=MAX_CODE_LENGTH, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    admission_year = models.PositiveIntegerField(validators=[MinValueValidator(2000), MaxValueValidator(2100)])
    current_form = models.PositiveIntegerField(choices=FORM_CHOICES, default=1, help_text="Current form level for O-level students")
    current_semester = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 9)], blank=True, null=True, help_text="For university-level students")
    gpa = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0.0), MaxValueValidator(4.0)])
    cgpa = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0.0), MaxValueValidator(4.0)])
    batch = models.CharField(max_length=10, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='student_pics/', blank=True, null=True)
    
    # Personal information fields
    date_of_birth = models.DateField(null=True, blank=True, help_text="Student's date of birth")
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')], null=True, blank=True, help_text="Student's gender")
    
    # Tanzania O-level specific fields
    necta_exam_number = models.CharField(max_length=20, blank=True, null=True, help_text="NECTA examination number")
    birth_certificate_number = models.CharField(max_length=50, blank=True, null=True)
    previous_school = models.CharField(max_length=200, blank=True, null=True, help_text="Previous primary school")
    primary_school_leaving_exam_number = models.CharField(max_length=20, blank=True, null=True, help_text="PSLE number")
    
    # Subject enrollments for O-Level students
    enrolled_subjects = models.ManyToManyField(Subject, through='SubjectEnrollment', related_name='students')

    class Meta:
        indexes = [models.Index(fields=['roll_number'])]

    def __str__(self):
        return f"{self.roll_number} - {self.user.get_full_name()}"
    
    def get_current_level_display(self):
        """Display current form or semester based on education level"""
        if self.department.education_level == 'olevel':
            return f"Form {self.current_form}"
        else:
            return f"Semester {self.current_semester}" if self.current_semester else "N/A"

class NECTAExam(models.Model):
    EXAM_TYPES = [
        ('csee', 'Certificate of Secondary Education Examination (CSEE)'),
        ('ftna', 'Form Two National Assessment (FTNA)'),
        ('mock', 'Mock Examination'),
        ('terminal', 'Terminal Examination'),
        ('annual', 'Annual Examination'),
    ]
    
    SUBJECT_CHOICES = [
        ('math', 'Mathematics'),
        ('eng', 'English Language'),
        ('kisw', 'Kiswahili'),
        ('bio', 'Biology'),
        ('phy', 'Physics'),
        ('chem', 'Chemistry'),
        ('hist', 'History'),
        ('geo', 'Geography'),
        ('civ', 'Civics'),
        ('bkee', 'Bookkeeping'),
        ('comm', 'Commerce'),
        ('ict', 'Information & Computer Studies'),
        ('agri', 'Agriculture'),
        ('arb', 'Arabic Language'),
        ('fre', 'French Language'),
        ('home', 'Home Economics'),
        ('art', 'Art & Design'),
        ('music', 'Music'),
        ('p_e', 'Physical Education'),
    ]
    
    GRADE_CHOICES = [
        ('A', 'A (75-100)'),
        ('B', 'B (65-74)'),
        ('C', 'C (45-64)'),
        ('D', 'D (30-44)'),
        ('F', 'F (0-29)'),
    ]
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='necta_exams')
    exam_type = models.CharField(max_length=10, choices=EXAM_TYPES)
    subject = models.CharField(max_length=10, choices=SUBJECT_CHOICES)
    grade = models.CharField(max_length=1, choices=GRADE_CHOICES)
    marks_obtained = models.PositiveIntegerField(null=True, blank=True, help_text="Marks out of 100")
    exam_year = models.PositiveIntegerField()
    exam_month = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 13)])
    is_mock = models.BooleanField(default=False)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'exam_type', 'subject', 'exam_year', 'exam_month']
        ordering = ['-exam_year', '-exam_month', 'subject']
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.get_exam_type_display()} - {self.get_subject_display()}: {self.grade}"
    
    def get_grade_points(self):
        """Convert grade to points for division calculation"""
        grade_points = {'A': 5, 'B': 4, 'C': 3, 'D': 2, 'F': 1}
        return grade_points.get(self.grade, 0)

class SubjectEnrollment(models.Model):
    """Manages student enrollment in specific subjects for each form level"""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='subject_enrollments')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='enrollments')
    academic_year = models.PositiveIntegerField(help_text="Academic year for this enrollment")
    enrollment_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['student', 'subject', 'academic_year']
        ordering = ['academic_year', 'subject__code']
    
    def __str__(self):
        return f"{self.student} - {self.subject} ({self.academic_year})"

class SchoolCalendar(models.Model):
    """Academic calendar for Tanzania school system"""
    ACADEMIC_YEAR_CHOICES = [(i, f"{i}-{i+1}") for i in range(2020, 2035)]
    TERM_CHOICES = [
        (1, 'Term I'),
        (2, 'Term II'), 
        (3, 'Term III'),
    ]
    
    academic_year = models.PositiveIntegerField(choices=ACADEMIC_YEAR_CHOICES)
    term = models.PositiveIntegerField(choices=TERM_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    teaching_weeks = models.PositiveIntegerField(default=12, help_text="Number of teaching weeks")
    exam_weeks = models.PositiveIntegerField(default=2, help_text="Number of examination weeks")
    holiday_weeks = models.PositiveIntegerField(default=4, help_text="Number of holiday weeks")
    
    class Meta:
        unique_together = ['academic_year', 'term']
        ordering = ['-academic_year', 'term']
    
    def __str__(self):
        return f"{self.get_academic_year_display()} - {self.get_term_display()}"
    
    def save(self, *args, **kwargs):
        if self.is_current:
            SchoolCalendar.objects.filter(is_current=True).exclude(id=self.id).update(is_current=False)
        super().save(*args, **kwargs)

class FacultyProfile(models.Model):
    DESIGNATION_CHOICES = [
        ('prof', _('Professor')),
        ('assoc_prof', _('Associate Professor')),
        ('asst_prof', _('Assistant Professor')),
        ('lecturer', _('Lecturer')),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='faculty_profile')
    employee_id = models.CharField(max_length=20, unique=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    designation = models.CharField(max_length=MAX_NAME_LENGTH, choices=DESIGNATION_CHOICES)
    specialization = models.CharField(max_length=200, blank=True)
    joining_date = models.DateField(auto_now_add=True)
    profile_picture = models.ImageField(upload_to='faculty_pics/', blank=True, null=True)

    def save(self, *args, **kwargs):
        # Auto-generate employee_id if not provided
        if not self.employee_id:
            self.employee_id = f"EMP{self.user.id:04d}"
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_designation_display()})"

class AdminProfile(models.Model):
    ACCESS_LEVEL_CHOICES = [
        ('super', _('Super Admin')),
        ('regular', _('Regular Admin')),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    access_level = models.CharField(max_length=50, choices=ACCESS_LEVEL_CHOICES)
    profile_picture = models.ImageField(upload_to='faculty_pics/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_access_level_display()})"

class HeadmasterProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='headmaster_profile')
    appointment_date = models.DateField()
    years_of_experience = models.PositiveIntegerField(default=0)
    qualification = models.CharField(max_length=200, blank=True)
    profile_picture = models.ImageField(upload_to='headmaster_pics/', blank=True, null=True)

    def __str__(self):
        return f"Headmaster {self.user.get_full_name()}"

class ParentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile')
    child = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='parents')
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Parent of {self.child.user.get_full_name()}"

class Semester(models.Model):
    name = models.CharField(max_length=50, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_current:
            Semester.objects.filter(is_current=True).exclude(id=self.id).update(is_current=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Course(models.Model):
    name = models.CharField(max_length=MAX_NAME_LENGTH)
    code = models.CharField(max_length=MAX_CODE_LENGTH, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    credits = models.PositiveIntegerField(default=3)
    description = models.TextField(blank=True, null=True)
    syllabus = models.TextField(blank=True, null=True)

    class Meta:
        indexes = [models.Index(fields=['code'])]

    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def is_subject(self):
        """Returns True if this course should be called a 'subject' (for O-Level)"""
        return self.department.education_level == 'olevel'
    
    @property
    def display_name(self):
        """Returns 'Subject' or 'Course' based on education level"""
        return 'Subject' if self.is_subject else 'Course'
    

    

class CourseOffering(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='offerings')
    faculty = models.ForeignKey(FacultyProfile, on_delete=models.SET_NULL, null=True, blank=True)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='course_offerings')
    section = models.CharField(max_length=10)

    class Meta:
        unique_together = ('course', 'semester', 'section')

    def __str__(self):
        return f"{self.course.code} - {self.semester.name} - Section {self.section}"

class Enrollment(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='enrollments')
    course_offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course_offering')

    def __str__(self):
        return f"{self.student} enrolled in {self.course_offering}"

class FeeStructure(models.Model):
    name = models.CharField(max_length=MAX_NAME_LENGTH)
    tuition_fee = models.DecimalField(max_digits=10, decimal_places=2)
    library_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    lab_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    academic_year = models.CharField(max_length=9)  # e.g., '2024-2025'

    def __str__(self):
        return f"{self.name} - {self.academic_year}"

class FeeCategory(models.Model):
    name = models.CharField(max_length=MAX_NAME_LENGTH, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Fee(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE, null=True, blank=True, default=None)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    paid_date = models.DateField(blank=True, null=True)
    receipt_number = models.CharField(max_length=MAX_NAME_LENGTH, blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    semester = models.CharField(max_length=10, default='1')
    category = models.CharField(max_length=100, default='Tuition')


    def __str__(self):
        if self.fee_structure:
            return f"{self.student} - {self.fee_structure.name} - {self.amount}"
        return f"{self.student} - {self.category} - {self.amount}"

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('mobile_money', 'Mobile Money'),
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit/Debit Card'),
    ]
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='payments')
    fee = models.ForeignKey(Fee, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, default='bank_transfer')
    transaction_id = models.CharField(max_length=MAX_NAME_LENGTH, blank=True, null=True)
    receipt_file = models.FileField(upload_to='fee_receipts/', blank=True, null=True)

    def __str__(self):
        return f"Payment of {self.amount} by {self.student} on {self.payment_date}"

class Grade(models.Model):
    GRADE_CHOICES = [
        ('A+', 'A+ (90-100)'), ('A', 'A (85-89)'), ('A-', 'A- (80-84)'),
        ('B+', 'B+ (75-79)'), ('B', 'B (70-74)'), ('B-', 'B- (65-69)'),
        ('C+', 'C+ (60-64)'), ('C', 'C (55-59)'), ('C-', 'C- (50-54)'),
        ('D', 'D (45-49)'), ('F', 'F (Below 45)'), ('I', 'Incomplete'),
    ]
    
    GRADE_POINTS = {
        'A+': 4.0, 'A': 4.0, 'A-': 3.7,
        'B+': 3.3, 'B': 3.0, 'B-': 2.7,
        'C+': 2.3, 'C': 2.0, 'C-': 1.7,
        'D': 1.0, 'F': 0.0, 'I': 0.0,
    }

    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='grade')
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES)
    points = models.DecimalField(max_digits=3, decimal_places=1, editable=False)
    remarks = models.TextField(blank=True)
    awarded_on = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.points = self.GRADE_POINTS.get(self.grade, 0.0)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.enrollment.student} - {self.enrollment.course_offering.course}: {self.grade}"
class Attendance(models.Model):
    STATUS_CHOICES = [
        ('P', _('Present')),
        ('A', _('Absent')),
        ('L', _('Late')),  # Corrected from 'L |' to 'L'
        ('E', _('Excused')),
    ]
    
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    notes = models.TextField(blank=True, null=True)
    check_in_time = models.TimeField(null=True, blank=True, help_text="Time when student checked in")
    check_out_time = models.TimeField(null=True, blank=True, help_text="Time when student checked out")

    class Meta:
        unique_together = ('enrollment', 'date')
        ordering = ['-date']
        verbose_name = _('Attendance Record')
        verbose_name_plural = _('Attendance Records')

    def __str__(self):
        return f"{self.enrollment.student} - {self.date}: {self.get_status_display()}"


class LeaveRequest(models.Model):
    LEAVE_STATUS_CHOICES = [
        ('Pending', _('Pending')),
        ('Approved', _('Approved')),
        ('Rejected', _('Rejected')),
    ]

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='leave_requests')
    course_offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE, related_name='leave_requests', null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)

    status = models.CharField(max_length=10, choices=LEAVE_STATUS_CHOICES, default='Pending')
    submitted_at = models.DateTimeField(auto_now_add=True)
    processed_by = models.ForeignKey(FacultyProfile, on_delete=models.SET_NULL, null=True, blank=True)
    processed_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Leave request by {self.student} for {self.course_offering} from {self.start_date} to {self.end_date}"

class ExamSchedule(models.Model):
    EXAM_TYPE_CHOICES = [
        ('Midterm', _('Midterm')),
        ('Final', _('Final')),
        ('Quiz', _('Quiz')),
        ('Assignment', _('Assignment')),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='exam_schedules')
    exam_type = models.CharField(max_length=50, choices=EXAM_TYPE_CHOICES)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    venue = models.CharField(max_length=MAX_NAME_LENGTH)

    def __str__(self):
        return f"{self.course.code} {self.exam_type} on {self.date} at {self.venue}"

class ReportCard(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='report_cards')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    gpa = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(4.0)])
    cgpa = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(4.0)])
    generated_at = models.DateTimeField(auto_now_add=True)
    report_pdf = models.FileField(upload_to='report_cards/', blank=True, null=True)

    class Meta:
        unique_together = ('student', 'semester')

    def __str__(self):
        return f"ReportCard {self.student} - Semester {self.semester.name}"

class StudentClass(models.Model):
    """Model for managing school classes/forms"""
    name = models.CharField(max_length=50, unique=True, help_text="Class name (e.g., Form 1A, Form 2B)")
    form_level = models.PositiveIntegerField(choices=StudentProfile.FORM_CHOICES, help_text="Form level (1-4)")
    class_teacher = models.ForeignKey(FacultyProfile, on_delete=models.SET_NULL, null=True, blank=True, 
                                     help_text="Class teacher assigned to this class")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, help_text="Department this class belongs to")
    max_students = models.PositiveIntegerField(default=40, help_text="Maximum number of students in this class")
    current_students = models.PositiveIntegerField(default=0, help_text="Current number of students")
    academic_year = models.PositiveIntegerField(help_text="Academic year for this class")
    is_active = models.BooleanField(default=True, help_text="Whether this class is currently active")
    
    class Meta:
        ordering = ['form_level', 'name']
        unique_together = ['name', 'academic_year']
        indexes = [models.Index(fields=['form_level', 'academic_year'])]
    
    def __str__(self):
        return f"{self.name} - {self.academic_year}"
    
    @property
    def available_spaces(self):
        """Calculate available spaces in the class"""
        return max(0, self.max_students - self.current_students)
    
    @property
    def is_full(self):
        """Check if the class is full"""
        return self.current_students >= self.max_students

class Announcement(models.Model):
    TARGET_AUDIENCE_CHOICES = [
        ('All', _('All')),
        ('Students', _('Students')),
        ('Faculty', _('Faculty')),
        ('Parents', _('Parents')),
        ('Class', _('Specific Class')),
    ]

    title = models.CharField(max_length=MAX_TITLE_LENGTH)
    message = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    target_audience = models.CharField(max_length=50, choices=TARGET_AUDIENCE_CHOICES, default='All')
    
    # For class-specific announcements
    target_class = models.ForeignKey('StudentClass', on_delete=models.SET_NULL, null=True, blank=True, 
                                   help_text="Select class when target audience is 'Specific Class'")
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="When should this announcement expire?")

    def __str__(self):
        return self.title
    
    def is_expired(self):
        """Check if announcement has expired"""
        if self.expires_at is None:
            return False
        return timezone.now() > self.expires_at
    
    def get_target_display(self):
        """Get human-readable target description"""
        if self.target_audience == 'Class' and self.target_class:
            return f"Class {self.target_class.name}"
        return self.get_target_audience_display()
    

class Schedule(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField(default=timezone.now)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.name} ({self.date})"

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    subject = models.CharField(max_length=MAX_TITLE_LENGTH)
    body = models.TextField()
    # receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)  # ✅ Add this

    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"From {self.sender} to {self.recipient} - {self.subject}"

class ForumTopic(models.Model):
    title = models.CharField(max_length=MAX_TITLE_LENGTH)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ForumPost(models.Model):
    topic = models.ForeignKey(ForumTopic, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post by {self.author} in {self.topic.title}"

class Book(models.Model):
    title = models.CharField(max_length=MAX_TITLE_LENGTH)
    author = models.CharField(max_length=MAX_TITLE_LENGTH)
    isbn = models.CharField(max_length=13, unique=True)
    category = models.CharField(max_length=MAX_NAME_LENGTH)
    available_copies = models.PositiveIntegerField(default=1)
    total_copies = models.PositiveIntegerField(default=1)
    is_ebook = models.BooleanField(default=False)
    ebook_file = models.FileField(upload_to='ebooks/', blank=True, null=True)

    def __str__(self):
        return f"{self.title} by {self.author}"

class BorrowedBook(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(blank=True, null=True)

    def is_overdue(self):
        return self.return_date is None and self.due_date < timezone.now().date()

    def fine_amount(self):
        try:
            fine_rate = float(SystemSetting.objects.get(key='library_fine_per_day').value)
        except SystemSetting.DoesNotExist:
            fine_rate = 100  # Default fine rate
        if self.is_overdue():
            days_late = (timezone.now().date() - self.due_date).days
            return days_late * fine_rate
        return 0

    def __str__(self):
        return f"{self.book.title} borrowed by {self.student.user.username}"

class Activity(models.Model):
    ACTIVITY_TYPES = [
        ('Sports', _('Sports')),
        ('Club', _('Club')),
        ('Workshop', _('Workshop')),
        ('Other', _('Other')),
    ]
    
    title = models.CharField(max_length=MAX_TITLE_LENGTH)
    description = models.TextField(blank=True)
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    date = models.DateField()
    venue = models.CharField(max_length=MAX_TITLE_LENGTH, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.activity_type})"

class Participation(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    registered_on = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.activity.title}"

class Achievement(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=MAX_TITLE_LENGTH)
    description = models.TextField(blank=True)
    date_awarded = models.DateField()
    awarded_by = models.CharField(max_length=MAX_NAME_LENGTH, blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.student.user.get_full_name()}"

class Material(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=MAX_TITLE_LENGTH)
    file = models.FileField(upload_to='course_materials/')
    description = models.TextField(blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.course.code})"
class SystemSetting(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.key}: {self.value}"

class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('deleted', 'Deleted'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('viewed', 'Viewed'),
        ('downloaded', 'Downloaded'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    model = models.CharField(max_length=100)
    object_id = models.PositiveIntegerField()
    details = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} performed {self.action} on {self.model} with object_id {self.object_id}"

# Advanced Models for Modern Features

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('success', 'Success'),
        ('error', 'Error'),
        ('announcement', 'Announcement'),
        ('reminder', 'Reminder'),
    ]
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    action_url = models.URLField(blank=True, null=True)
    action_text = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['recipient', 'is_read'])]
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username}"
    
    def mark_as_read(self):
        self.is_read = True
        self.read_at = timezone.now()
        self.save()

class TimeTable(models.Model):
    DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    
    course_offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE)
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('course_offering', 'day', 'start_time', 'semester')
        ordering = ['day', 'start_time']
    
    def __str__(self):
        return f"{self.course_offering.course.code} - {self.get_day_display()} {self.start_time}"

class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    course_offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE, related_name='assignments')
    due_date = models.DateTimeField()
    max_marks = models.PositiveIntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.title} - {self.course_offering.course.code}"

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='assignments/')
    marks_obtained = models.PositiveIntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    is_late = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('assignment', 'student')
    
    def __str__(self):
        return f"{self.student.user.username} - {self.assignment.title}"
    
    def save(self, *args, **kwargs):
        if self.submitted_at > self.assignment.due_date:
            self.is_late = True
        super().save(*args, **kwargs)

class OnlineClass(models.Model):
    title = models.CharField(max_length=200)
    course_offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE)
    scheduled_time = models.DateTimeField()
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    meeting_link = models.URLField(blank=True, null=True)
    meeting_id = models.CharField(max_length=100, blank=True, null=True)
    password = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.course_offering.course.code}"

class AttendanceSession(models.Model):
    course_offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(FacultyProfile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('course_offering', 'date')
    
    def __str__(self):
        return f"{self.course_offering.course.code} - {self.date}"

class LiveAttendance(models.Model):
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='live_attendances')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=1, choices=Attendance.STATUS_CHOICES, default='P')
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('session', 'student')
    
    def __str__(self):
        return f"{self.student.user.username} - {self.session.date}"

class Resource(models.Model):
    RESOURCE_TYPES = [
        ('document', 'Document'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('image', 'Image'),
        ('link', 'Link'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=10, choices=RESOURCE_TYPES)
    file = models.FileField(upload_to='resources/', blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='resources')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.title} - {self.course.code}"

class Event(models.Model):
    EVENT_TYPES = [
        ('holiday', 'Holiday'),
        ('exam', 'Exam'),
        ('meeting', 'Meeting'),
        ('workshop', 'Workshop'),
        ('seminar', 'Seminar'),
        ('sports', 'Sports'),
        ('cultural', 'Cultural'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    type = models.CharField(max_length=10, choices=EVENT_TYPES)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    venue = models.CharField(max_length=200)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)
    is_all_day = models.BooleanField(default=False)
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.CharField(max_length=100, blank=True, null=True)
    attendees = models.ManyToManyField(User, related_name='events', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['start_date']
    
    def __str__(self):
        return f"{self.title} - {self.start_date.date()}"

class Poll(models.Model):
    question = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    ends_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    allow_multiple_choices = models.BooleanField(default=False)
    
    def __str__(self):
        return self.question
    
    def is_expired(self):
        return timezone.now() > self.ends_at

class PollOption(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=200)
    votes = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.text} - {self.poll.question}"

class PollVote(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    option = models.ForeignKey(PollOption, on_delete=models.CASCADE)
    voter = models.ForeignKey(User, on_delete=models.CASCADE)
    voted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('poll', 'voter')
    
    def __str__(self):
        return f"{self.voter.username} - {self.poll.question}"

class ChatRoom(models.Model):
    ROOM_TYPES = [
        ('course', 'Course'),
        ('general', 'General'),
        ('private', 'Private'),
        ('announcement', 'Announcement'),
    ]
    
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=15, choices=ROOM_TYPES)
    course_offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE, null=True, blank=True)
    members = models.ManyToManyField(User, related_name='chat_rooms')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['sent_at']
    
    def __str__(self):
        return f"{self.sender.username} - {self.room.name}"

class Analytics(models.Model):
    METRIC_TYPES = [
        ('login', 'Login Count'),
        ('page_view', 'Page View'),
        ('course_access', 'Course Access'),
        ('resource_download', 'Resource Download'),
        ('assignment_submit', 'Assignment Submission'),
        ('attendance_mark', 'Attendance Marked'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES)
    count = models.PositiveIntegerField(default=1)
    date = models.DateField()
    additional_data = models.JSONField(blank=True, null=True)
    
    class Meta:
        unique_together = ('user', 'metric_type', 'date')
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.username} - {self.metric_type} - {self.date}"

class SystemConfiguration(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.key}: {self.value}"

class Backup(models.Model):
    BACKUP_TYPES = [
        ('full', 'Full Backup'),
        ('incremental', 'Incremental Backup'),
        ('database', 'Database Only'),
        ('files', 'Files Only'),
    ]
    
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=15, choices=BACKUP_TYPES)
    file = models.FileField(upload_to='backups/')
    size = models.BigIntegerField(help_text="Size in bytes")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_successful = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.created_at.date()}"

class APIKey(models.Model):
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    last_used = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"