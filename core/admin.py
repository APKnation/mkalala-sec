from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from .models import (
    Department, AdminProfile, StudentProfile, FacultyProfile, ParentProfile,
    Course, Semester, CourseOffering, Enrollment, Grade, Attendance,
    FeeCategory, Fee, Payment, LeaveRequest,
    ExamSchedule, ReportCard, Announcement, Message, ForumTopic, ForumPost,
    Book, BorrowedBook, Activity, Participation, Achievement, Material,
    SystemSetting, ActivityLog
)

User = get_user_model()

# Inline classes for better admin interface
class GradeInline(admin.TabularInline):
    model = Grade
    extra = 0
    readonly_fields = ('awarded_on',)
    can_delete = False

class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 0
    readonly_fields = ('date',)
    can_delete = True

# Custom User Admin
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_student', 'is_faculty', 'is_admin', 'is_parent', 'is_active')
    list_filter = ('role', 'is_student', 'is_faculty', 'is_admin', 'is_parent', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'profile_picture')}),
        (_('Role'), {'fields': ('role',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Role flags'), {'fields': ('is_student', 'is_faculty', 'is_admin', 'is_parent', 'is_headmaster')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'is_student', 'is_faculty', 'is_admin', 'is_parent', 'is_headmaster'),
        }),
    )

# Register the User model with the custom admin
admin.site.register(User, CustomUserAdmin)

# Model Admins
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'slug')
    search_fields = ('code', 'name')
    prepopulated_fields = {'slug': ('code', 'name')}

@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'access_level')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    list_filter = ('access_level', 'department')

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('roll_number', 'user', 'department', 'admission_year', 'current_semester', 'gpa', 'cgpa', 'get_enrollments_count')
    search_fields = ('roll_number', 'user__username', 'user__first_name', 'user__last_name')
    list_filter = ('department', 'admission_year', 'current_semester')
    readonly_fields = ('roll_number',)
    ordering = ('-admission_year', 'roll_number')
    
    def get_enrollments_count(self, obj):
        """Display number of enrollments for this student"""
        count = obj.enrollments.count()
        return f"{count} enrolled"
    get_enrollments_count.short_description = 'Enrollments'

@admin.register(FacultyProfile)
class FacultyProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'designation', 'joining_date')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    list_filter = ('designation', 'department')

@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'child', 'phone')
    search_fields = ('user__username', 'child__roll_number', 'child__user__first_name')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'department', 'credits')
    search_fields = ('code', 'name')
    list_filter = ('department',)

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current',)
    search_fields = ('name',)

@admin.register(CourseOffering)
class CourseOfferingAdmin(admin.ModelAdmin):
    list_display = ('course', 'semester', 'section', 'faculty')
    list_filter = ('semester', 'course__department')
    search_fields = ('course__code', 'course__name', 'section')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student_info', 'course_info', 'enrollment_date', 'get_attendance_rate', 'get_grade')
    list_filter = ('course_offering__semester', 'course_offering__course__department', 'enrollment_date')
    search_fields = ('student__roll_number', 'student__user__first_name', 'course_offering__course__name', 'course_offering__course__code')
    readonly_fields = ('enrollment_date',)
    ordering = ('-enrollment_date',)
    list_per_page = 25
    
    # Add inline editing for related objects
    inlines = [GradeInline, AttendanceInline]
    
    def student_info(self, obj):
        """Display student roll number and name"""
        return f"{obj.student.roll_number} - {obj.student.user.get_full_name()}"
    student_info.short_description = 'Student'
    
    def course_info(self, obj):
        """Display course code and name"""
        course = obj.course_offering.course
        term = 'Subject' if course.is_subject else 'Course'
        return f"{course.code} - {course.name} ({term})"
    course_info.short_description = 'Course/Subject'
    
    def get_attendance_rate(self, obj):
        """Calculate and display attendance rate"""
        total = obj.attendances.count()
        present = obj.attendances.filter(status='P').count()
        if total > 0:
            rate = (present / total) * 100
            return f"{rate:.1f}%"
        return "N/A"
    get_attendance_rate.short_description = 'Attendance'
    
    def get_grade(self, obj):
        """Display grade if available"""
        if hasattr(obj, 'grade') and obj.grade:
            return obj.grade.grade
        return "Pending"
    get_grade.short_description = 'Grade'

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'grade', 'points', 'awarded_on')
    list_filter = ('grade', 'enrollment__course_offering__semester')
    search_fields = ('enrollment__student__roll_number', 'enrollment__course_offering__course__code')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'date', 'status', 'notes')
    list_filter = ('status', 'date', 'enrollment__course_offering__semester')
    search_fields = ('enrollment__student__roll_number', 'enrollment__course_offering__course__code')

@admin.register(FeeCategory)
class FeeCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    list_display = ('student', 'fee_structure', 'amount', 'due_date', 'is_paid')
    list_filter = ('is_paid', 'semester', 'fee_structure')
    search_fields = ('student__roll_number', 'student__user__first_name')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'fee', 'amount', 'payment_date', 'transaction_id')
    list_filter = ('payment_date',)
    search_fields = ('student__roll_number', 'transaction_id')

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('student', 'course_offering', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('student__roll_number', 'course_offering__course__code')

@admin.register(ExamSchedule)
class ExamScheduleAdmin(admin.ModelAdmin):
    list_display = ('course', 'exam_type', 'date', 'start_time', 'venue')
    list_filter = ('exam_type', 'date')
    search_fields = ('course__code', 'course__name', 'venue')

@admin.register(ReportCard)
class ReportCardAdmin(admin.ModelAdmin):
    list_display = ('student', 'semester', 'gpa', 'cgpa', 'generated_at')
    list_filter = ('semester',)
    search_fields = ('student__roll_number', 'student__user__first_name')

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_at', 'target_audience')
    list_filter = ('target_audience', 'created_at')
    search_fields = ('title', 'message')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'subject', 'sent_at', 'is_read')
    list_filter = ('is_read', 'sent_at')
    search_fields = ('sender__username', 'recipient__username', 'subject')

@admin.register(ForumTopic)
class ForumTopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_at')
    search_fields = ('title', 'created_by__username')

@admin.register(ForumPost)
class ForumPostAdmin(admin.ModelAdmin):
    list_display = ('topic', 'author', 'created_at')
    search_fields = ('topic__title', 'author__username', 'content')
    list_filter = ('created_at',)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'available_copies', 'total_copies')
    search_fields = ('title', 'author', 'isbn')
    list_filter = ('is_ebook',)

@admin.register(BorrowedBook)
class BorrowedBookAdmin(admin.ModelAdmin):
    list_display = ('student', 'book', 'issue_date', 'due_date', 'return_date', 'is_overdue', 'fine_amount')
    list_filter = ('issue_date', 'due_date', 'return_date')
    search_fields = ('student__roll_number', 'book__title', 'book__isbn')

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'activity_type', 'date', 'venue')
    list_filter = ('activity_type', 'date')
    search_fields = ('title', 'venue')

@admin.register(Participation)
class ParticipationAdmin(admin.ModelAdmin):
    list_display = ('student', 'activity', 'registered_on', 'attended')
    list_filter = ('attended', 'activity__activity_type')
    search_fields = ('student__roll_number', 'activity__title')

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('student', 'title', 'date_awarded')
    list_filter = ('date_awarded',)
    search_fields = ('student__roll_number', 'title')

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'uploaded_by', 'uploaded_at')
    list_filter = ('uploaded_at', 'course__department')
    search_fields = ('title', 'course__code', 'uploaded_by__username')

@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'value')
    search_fields = ('key', 'value')

# class ActivityLog(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     action = models.CharField(max_length=255)
#     timestamp = models.DateTimeField(auto_now_add=True)
#     model = models.CharField(max_length=100)
#     object_id = models.PositiveIntegerField()  # Ensure this field exists or calculate it dynamically if needed

    # def __str__(self):
    #     return f"{self.user.username} performed {self.action}"

    # # If 'object_id' refers to another field, define it as a method
    # def get_object_id(self):
    #     return self.object_id

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'model', 'object_id')  # Use 'object_id' directly
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'model', 'details')
