from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import CourseUpdateView
from .views import faculty_register  # ✅ This matches the function name
from .views import CreateCourseView  # <-- this is correct now
from .views import CourseListView
from .views import CourseDetailView
from .views import CourseDeleteView
from .views import CourseManagementView

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Authentication URLs
    path('', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    
    # Registration URLs
    path('register/student/', views.RegisterStudentView.as_view(), name='register'),
    path('faculty/register/', faculty_register, name='faculty_register'),
    
    # Dashboard URLs
    path('dashboard', views.DashboardView.as_view(), name='dashboard'),  # Role-based redirect view
    path('student/dashboard/', views.StudentDashboardView.as_view(), name='student_dashboard'),
    path('faculty/dashboard/', views.FacultyDashboardView.as_view(), name='faculty_dashboard'),
    path('dashboard/admin/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('activity-logs/', views.ActivityLogView.as_view(), name='system_logs'),
    path('user-management/', views.UserManagementView.as_view(), name='user_management'),

    # Profile URLs
    path('profile/', views.ProfileView.as_view(), name='profile'),
    # path('profile/update/', views.ProfileUpdateView.as_view(), name='profile_update'),
    path('profile/update/', views.ProfileUpdateView.as_view(), name='update_profile'),

    
    # User Management URLs
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/add/', views.add_user, name='add_user'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/edit/', views.UserUpdateView.as_view(), name='edit_user'),
    path('users/<int:user_id>/deactivate/', views.deactivate_user, name='deactivate_user'),
    path('users/pending/', views.UserApprovalView.as_view(), name='user_approval'),
    path('users/<int:user_id>/approve/', views.user_approve, name='user_approve'),
    
    # Student URLs
    path('students/', views.StudentListView.as_view(), name='student_list'),
    path('students/<int:pk>/', views.StudentDetailView.as_view(), name='student_detail'),
    path('students/<int:pk>/edit/', views.StudentUpdateView.as_view(), name='student_edit'),
    
    # Faculty URLs
    path('faculty/', views.FacultyListView.as_view(), name='faculty_list'),
    path('faculty/<int:pk>/', views.FacultyDetailView.as_view(), name='faculty_detail'),
    path('faculty/<int:pk>/edit/', views.FacultyUpdateView.as_view(), name='faculty_edit'),
    path('grades/add/', views.GradeCreateView.as_view(), name='grade_create'),
    path('grades/<int:pk>/edit/', views.GradeUpdateView.as_view(), name='grade_edit'),
    
    # Attendance URLs
    path('attendance/', views.AttendanceListView.as_view(), name='attendance_list'),
    path('attendance/add/', views.AttendanceCreateView.as_view(), name='attendance_create'),
    path('attendance/<int:pk>/edit/', views.AttendanceUpdateView.as_view(), name='attendance_edit'),
    
    # Fee URLs
    path('fees/', views.FeeListView.as_view(), name='fee_list'),
    path('fees/add/', views.FeeCreateView.as_view(), name='fee_create'),
    path('fees/<int:pk>/edit/', views.FeeUpdateView.as_view(), name='fee_edit'),
    
    # System URLs
    path('activity-logs/', views.ActivityLogView.as_view(), name='activity_log'),
    path('system-settings/', views.SystemSettingsView.as_view(), name='system_settings'),
    path('reports/', views.ReportsView.as_view(), name='reports'),
    
    # Additional feature URLs
    path('leave-requests/', views.leave_requests_list, name='leave_requests_list'),
    path('leave-requests/add/', views.LeaveRequestCreateView.as_view(), name='leave_request_create'),
    path('attendance/summary/', views.attendance_summary, name='attendance_summary'),
    path('exam-schedule/', views.exam_schedule_view, name='exam_schedule'),
    path('payment-history/', views.payment_history, name='payment_history'),
    path('announcements/', views.announcement_list, name='announcement_list'),
    path('inbox/', views.inbox, name='inbox'),
    path('send-message/', views.send_message, name='send_message'),
    path('forum/', views.forum_topics, name='forum_topics'),
    path('forum/<int:topic_id>/', views.topic_detail, name='topic_detail'),
    path('library/', views.search_books, name='book_search'),
    path('borrowed-books/', views.borrowed_books, name='borrowed_books'),
    path('elibrary/', views.elibrary, name='elibrary'),
    path('activities/', views.activity_list, name='activity_list'),
    path('achievements/', views.achievement_list, name='achievement_list'),
    path('fee-structure/', views.view_fee_structure, name='fee_structure'),
    path('gradebook/', views.gradebook_view, name='gradebook'),
    path('report-cards/', views.report_cards_view, name='report_cards'),
    path('materials/', views.view_materials, name='materials'),
    path('enroll/', views.enroll_course, name='enroll_course'),
    path('timetable/', views.view_timetable, name='timetable'),
    
    # Parent URLs
    path('parent/attendance/', views.view_child_attendance, name='view_child_attendance'),
    path('parent/grades/', views.view_child_grades, name='view_child_grades'),
    path('parent/fees/', views.view_fee_alerts, name='view_fee_alerts'),
    path('parent/send-message/', views.parent_send_message, name='parent_send_message'),
    path('parent/inbox/', views.inbox, name='parent_inbox'),






# COURSES
path('courses-new', views.course_list, name='course_list'),
path('add/', views.course_create, name='course_create'),
path('edit/<int:pk>/', views.course_update, name='course_update'),
path('delete/<int:pk>/', views.course_delete, name='course_delete'),
path('courses/manage/', CourseManagementView.as_view(), name='course_management'),  # ✅ this name matters


]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)