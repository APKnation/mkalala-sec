from django import template
from core.models import Course

register = template.Library()

@register.filter
def course_or_subject(course):
    """Returns 'Subject' or 'Course' based on the course's department education level"""
    if isinstance(course, Course):
        return 'Subject' if course.is_subject else 'Course'
    return 'Course'

@register.filter
def courses_or_subjects(courses):
    """Returns 'Subjects' or 'Courses' based on the first course's department education level"""
    if courses and hasattr(courses[0], 'course'):
        # Handle CourseOffering objects
        course_obj = courses[0].course
    elif courses:
        # Handle Course objects
        course_obj = courses[0]
    else:
        return 'Courses'
    
    return 'Subjects' if course_obj.is_subject else 'Courses'

@register.simple_tag
def get_course_term(student):
    """Returns 'subject' or 'course' based on the student's department education level"""
    return 'subject' if student.department.education_level == 'olevel' else 'course'

@register.simple_tag
def get_course_term_plural(student):
    """Returns 'subjects' or 'courses' based on the student's department education level"""
    return 'subjects' if student.department.education_level == 'olevel' else 'courses'

@register.simple_tag
def get_course_term_capitalized(student):
    """Returns 'Subject' or 'Course' based on the student's department education level"""
    return 'Subject' if student.department.education_level == 'olevel' else 'Course'

@register.simple_tag
def get_course_term_plural_capitalized(student):
    """Returns 'Subjects' or 'Courses' based on the student's department education level"""
    return 'Subjects' if student.department.education_level == 'olevel' else 'Courses'
