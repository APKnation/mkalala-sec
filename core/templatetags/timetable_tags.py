from django import template

register = template.Library()

@register.filter
def filter_by_day(schedules, day):
    return schedules.filter(day=day)

@register.filter
def filter_by_form(schedules, form_name):
    return schedules.filter(course_offering__course__department__name__icontains=form_name)
