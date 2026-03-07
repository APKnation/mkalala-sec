def is_student(user):
    return hasattr(user, 'student_profile')

def is_faculty(user):
    return hasattr(user, 'faculty_profile')

def is_admin(user):
    return hasattr(user, 'admin_profile') or (hasattr(user, 'role') and user.role == 'admin') or user.is_superuser

def is_parent(user):
    return hasattr(user, 'parent_profile')  # or however your model is named
