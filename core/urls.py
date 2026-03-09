from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from . import views
from . import views_dashboard
from . import views_role_dashboard
from . import views_admin
from . import views_ajax
from .views import CourseUpdateView
from .views import CreateCourseView  # <--this is correct now
from .views import CourseListView
from .views import CourseDetailView
from .views import CourseDeleteView
from .views import CourseManagementView
from .views import SubjectListView, SubjectCreateView, SubjectUpdateView, SubjectDeleteView, SubjectEnrollmentListView

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Public-facing URLs
    path('', views.public_home, name='public_home'),
    path('home/', views.public_home, name='public_home_alt'),
    path('about/', views.public_about, name='public_about'),
    path('courses/', views.public_courses, name='public_courses'),
    path('subjects/', views.public_courses, name='public_subjects'),
    path('admissions/', views.public_admissions, name='public_admissions'),
    path('contact/', views.public_contact, name='public_contact'),
    
    # Authentication URLs
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    
    # Registration URL - Single unified registration
    path('register/', views.PublicRegisterView.as_view(), name='register'),
    
    # Dashboard URLs
    path('dashboard/', views.RoleBasedDashboardView.as_view(), name='dashboard'),  # Role-based redirect view
    
    # Role-Specific Dashboard URLs (put first to be more specific)
    path('student/dashboard/<str:page>/', views_role_dashboard.student_unified_dashboard, name='student_unified_dashboard'),
    path('student/dashboard/load/<str:page>/', views_role_dashboard.load_student_dashboard_page, name='load_student_dashboard_page'),
    path('student/dashboard/notifications', views_role_dashboard.get_student_notifications, name='student_dashboard_notifications'),
    
    path('admin/dashboard/<str:page>/', views_role_dashboard.admin_unified_dashboard, name='admin_unified_dashboard'),
    path('admin/dashboard/load/<str:page>/', views_role_dashboard.load_admin_dashboard_page, name='load_admin_dashboard_page'),
    path('admin/dashboard/notifications', views_role_dashboard.get_admin_notifications, name='admin_dashboard_notifications'),
    
    path('headmaster/dashboard/<str:page>/', views_role_dashboard.headmaster_unified_dashboard, name='headmaster_unified_dashboard'),
    path('headmaster/dashboard/load/<str:page>/', views_role_dashboard.load_headmaster_dashboard_page, name='load_headmaster_dashboard_page'),
    path('headmaster/dashboard/notifications', views_role_dashboard.get_headmaster_notifications, name='headmaster_dashboard_notifications'),
    
    # Unified Dashboard URLs (more generic, put after specific ones)
    path('dashboard/<str:page>/', views_dashboard.unified_dashboard, name='unified_dashboard'),
    path('dashboard/load/<str:page>/', views_dashboard.load_dashboard_page, name='load_dashboard_page'),
    path('dashboard/notifications/', views_dashboard.get_notifications, name='dashboard_notifications'),
    
    # Legacy Dashboard URLs (keep for compatibility)
    path('dashboard/student/', views.StudentDashboardView.as_view(), name='student_dashboard'),
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/headmaster/', views.headmaster_dashboard, name='headmaster_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    
    # Dashboard AJAX URLs
    path('dashboard/announcements/create/', views_dashboard.CreateAnnouncementAjaxView.as_view(), name='dashboard_create_announcement'),
    path('dashboard/attendance/mark/', views_dashboard.MarkAttendanceAjaxView.as_view(), name='dashboard_mark_attendance'),
    
    path('teacher/timetable/', views.teacher_timetable, name='teacher_timetable'),
path('teacher/assignment/create/', views.teacher_assignment_create, name='teacher_assignment_create'),
path('teacher/course/create/', views.teacher_course_create, name='teacher_course_create'),
path('teacher/message/compose/', views.teacher_message_compose, name='teacher_message_compose'),
path('teacher/book/borrow/', views.teacher_book_borrow, name='teacher_book_borrow'),
path('teacher/book/return/<int:book_id>/', views.teacher_book_return, name='teacher_book_return'),
    path('dashboard/faculty/', views.FacultyDashboardView.as_view(), name='faculty_dashboard'),  # Legacy
    
    # Student Navigation URLs
    path('student/courses/', views.student_courses, name='student_courses'),
    path('student/results/', views.student_results, name='student_results'),
    path('student/timetable/', views.student_timetable, name='student_timetable'),
    path('student/assignments/', views.student_assignments, name='student_assignments'),
    path('student/assignments/<int:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),
    path('student/exams/', views.student_exams, name='student_exams'),
    path('student/library/', views.student_library, name='student_library'),
    path('student/achievements/', views.student_achievements, name='student_achievements'),
    path('student/fees/', views.student_fees, name='student_fees'),
    path('student/fees/pay/', views.process_payment, name='process_payment'),
    path('student/messages/', views.student_messages, name='student_messages'),
    path('admin/messages/', views.admin_messages, name='admin_messages'),
    path('student/announcements/', views.student_announcements, name='student_announcements'),
    path('student/activities/', views.student_activities, name='student_activities'),
    path('student/profile/', views.student_profile_view, name='student_profile'),
    path('student/settings/', views.student_settings, name='student_settings'),
    
    # Profile URLs
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/update/', views.ProfileUpdateView.as_view(), name='update_profile'),
    
    # API URLs
    path('api/users/', views.api_users, name='api_users'),
    path('api/users/<int:pk>/', views.api_users, name='api_user_detail'),
    path('api/test/', views.api_test, name='api_test'),
    path('api/test-no-auth/', views.api_test_no_auth, name='api_test_no_auth'),
    path('api/test-plain/', views.api_test_plain, name='api_test_plain'),
    path('api/create-teacher/', views.api_create_teacher, name='api_create_teacher'),
    path('debug/permissions/', views.debug_permissions, name='debug_permissions'),
    
    # User Management URLs
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/all/', views.UserListView.as_view(), name='admin_all_users'),
    path('users/add/', views.add_user, name='add_user'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    
    # Student Management URLs - Redirect to Admin Dashboard
    path('students/', lambda request: redirect('admin_unified_dashboard', page='students') if request.user.is_authenticated and request.user.role == 'admin' else redirect('login'), name='admin_student_list'),
    path('students/add/', views.admin_student_create, name='admin_student_create'),
    path('students/<int:pk>/', views.admin_student_detail, name='admin_student_detail'),
    path('students/<int:pk>/edit/', views.admin_student_edit, name='admin_student_edit'),
    path('students/<int:pk>/delete/', views.admin_student_delete, name='admin_student_delete'),
    
    # Teacher Management URLs
    path('teachers/', views.admin_teacher_list, name='admin_teacher_list'),
    path('teachers/add/', views.admin_teacher_create, name='admin_teacher_create'),
    path('teachers/<int:pk>/', views.admin_teacher_detail, name='admin_teacher_detail'),
    path('teachers/<int:pk>/edit/', views.admin_teacher_edit, name='admin_teacher_edit'),
    path('teachers/<int:pk>/delete/', views.admin_teacher_delete, name='admin_teacher_delete'),
    
    # Admin User Creation URLs
    path('admin/create/student/', views_admin.admin_create_student, name='admin_create_student'),
    path('admin/create/teacher/', views_admin.admin_create_teacher, name='admin_create_teacher'),
    path('admin/create/headmaster/', views_admin.admin_create_headmaster, name='admin_create_headmaster'),
    
    # Headmaster User Creation URLs
    path('headmaster/create/student/', views_admin.headmaster_create_student, name='headmaster_create_student'),
    path('headmaster/create/teacher/', views_admin.headmaster_create_teacher, name='headmaster_create_teacher'),
    
    # AJAX URLs for inline editing
    path('ajax/student/<int:student_id>/edit/', views_ajax.ajax_student_edit, name='ajax_student_edit'),
    path('ajax/student/<int:student_id>/detail/', views_ajax.ajax_student_detail, name='ajax_student_detail'),
    
    # Fee Management URLs
    path('fees/', views.admin_fees, name='admin_fees'),
    path('fees/add/', views.admin_fee_create, name='admin_fee_create'),
    path('fees/<int:pk>/edit/', views.admin_fee_edit, name='admin_fee_edit'),
    path('fees/<int:pk>/delete/', views.admin_fee_delete, name='admin_fee_delete'),
    
    # Timetable Management URLs
    path('timetable/', views.admin_timetable, name='admin_timetable'),
    path('timetable/add/', views.admin_timetable_create, name='admin_timetable_create'),
    path('timetable/<int:pk>/edit/', views.admin_timetable_edit, name='admin_timetable_edit'),
    path('timetable/<int:pk>/delete/', views.admin_timetable_delete, name='admin_timetable_delete'),
    
    # Additional Admin URLs
    path('admin/timetable/', views.admin_timetable, name='admin_timetable'),
    path('admin/timetable/<int:pk>/delete/', views.admin_timetable_delete, name='admin_timetable_delete'),
    path('admin/exams/', views.admin_exams, name='admin_exams'),
    path('admin/exams/create/', views.admin_exam_create, name='admin_exam_create'),
    path('admin/library/', views.admin_library, name='admin_library'),
    path('admin/fees/', views.admin_fees, name='admin_fees'),
    path('admin/reports/', views.admin_reports, name='admin_reports'),
    path('admin/settings/', views.admin_settings, name='admin_settings'),
    path('admin/school-info/edit/', views.admin_school_info_edit, name='admin_school_info_edit'),
    path('admin/school-info/create/', views.admin_school_info_edit, name='admin_school_info_create'),
    path('users/<int:pk>/edit/', views.UserUpdateView.as_view(), name='edit_user'),
    path('users/<int:pk>/delete/', views.delete_user, name='delete_user'),
    path('users/<int:user_id>/deactivate/', views.deactivate_user, name='deactivate_user'),
    path('users/pending/', views.UserApprovalView.as_view(), name='user_approval'),
    path('users/<int:user_id>/approve/', views.user_approve, name='user_approve'),
    
    # Faculty URLs
    path('faculty/', views.FacultyListView.as_view(), name='faculty_list'),
    path('faculty/<int:pk>/', views.FacultyDetailView.as_view(), name='faculty_detail'),
    path('faculty/<int:pk>/edit/', views.FacultyUpdateView.as_view(), name='faculty_edit'),
    path('grades/add/', views.GradeCreateView.as_view(), name='grade_create'),
    path('grades/<int:pk>/edit/', views.GradeUpdateView.as_view(), name='grade_edit'),
    
    # Debug URLs
    path('debug/permissions/', views.debug_permissions, name='debug_permissions'),
    path('attendance/test/', views.attendance_test, name='attendance_test'),
    
    # Attendance URLs - Redirect to Role-Specific Dashboards
    path('attendance/', lambda request: redirect('unified_dashboard', page='attendance') if request.user.role == 'teacher' else 
                                              redirect('student_unified_dashboard', page='attendance') if request.user.role == 'student' else
                                              redirect('admin_unified_dashboard', page='attendance') if request.user.role == 'admin' else
                                              redirect('headmaster_unified_dashboard', page='attendance'), name='attendance_list'),
    path('attendance/add/', lambda request: redirect('unified_dashboard', page='attendance'), name='attendance_create'),
    path('attendance/<int:pk>/edit/', lambda request: redirect('unified_dashboard', page='attendance'), name='attendance_edit'),
    
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
    path('admin/announcements/', views.admin_announcements, name='admin_announcements'),
    path('teacher/announcements/', lambda request: redirect('unified_dashboard', page='announcements'), name='teacher_announcements'),
    path('announcements/', lambda request: redirect('unified_dashboard', page='announcements') if request.user.role == 'teacher' else 
                                          redirect('student_unified_dashboard', page='announcements') if request.user.role == 'student' else
                                          redirect('admin_unified_dashboard', page='announcements') if request.user.role == 'admin' else
                                          redirect('headmaster_unified_dashboard', page='announcements'), name='announcement_list'),
    path('inbox/', lambda request: redirect('unified_dashboard', page='messages') if request.user.role == 'teacher' else 
                              redirect('student_unified_dashboard', page='messages') if request.user.role == 'student' else
                              redirect('admin_unified_dashboard', page='messages') if request.user.role == 'admin' else
                              redirect('headmaster_unified_dashboard', page='messages'), name='inbox'),
    
    # Student enrollment URLs
    path('enroll/', views.enroll_course, name='enroll_course'),
    path('send-message/', views.send_message, name='send_message'),
    path('forum/', views.forum_topics, name='forum_topics'),
    path('forum/<int:topic_id>/', views.topic_detail, name='topic_detail'),
    path('library/', lambda request: redirect('unified_dashboard', page='library') if request.user.role == 'teacher' else 
                           redirect('student_unified_dashboard', page='library') if request.user.role == 'student' else
                           redirect('admin_unified_dashboard', page='library') if request.user.role == 'admin' else
                           redirect('headmaster_unified_dashboard', page='library'), name='book_search'),
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






# SUBJECTS MANAGEMENT
path('subjects/', CourseListView.as_view(), name='subjects_list'),
path('subjects/manage/', CourseManagementView.as_view(), name='subjects_management'),
path('subjects/add/', CreateCourseView.as_view(), name='course_create'),
path('subjects/<int:pk>/', CourseDetailView.as_view(), name='course_detail'),
path('subjects/<int:pk>/edit/', CourseUpdateView.as_view(), name='course_update'),
path('subjects/<int:pk>/delete/', CourseDeleteView.as_view(), name='course_delete'),

# SUBJECT ENROLLMENT FOR TANZANIAN O-LEVEL
path('subjects/enrollment/', SubjectEnrollmentListView.as_view(), name='subject_enrollment_list'),
path('subjects/enrollment/dashboard/', views.subject_enrollment_dashboard, name='subject_enrollment_dashboard'),
path('subjects/enroll/<int:student_id>/', views.enroll_student_subjects, name='enroll_student_subjects'),
path('subjects/bulk-enroll/', views.bulk_subject_enrollment, name='bulk_subject_enrollment'),

# SUBJECT MANAGEMENT (ADMIN)
path('manage/subjects/', SubjectListView.as_view(), name='subject_list'),
path('manage/subjects/add/', SubjectCreateView.as_view(), name='subject_create'),
path('manage/subjects/<int:pk>/edit/', SubjectUpdateView.as_view(), name='subject_update'),
path('manage/subjects/<int:pk>/delete/', SubjectDeleteView.as_view(), name='subject_delete'),

# CLASS MANAGEMENT
path('manage/classes/', views.class_management, name='class_management'),
path('manage/classes/assign/<int:student_id>/', views.assign_student_class, name='assign_student_class'),
path('manage/classes/bulk-assign/', views.bulk_class_assignment, name='bulk_class_assignment'),


]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)