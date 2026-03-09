from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.contrib import messages
from .models import StudentProfile, Department
from .utils import is_admin
import json

@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
@csrf_exempt
def ajax_student_edit(request, student_id):
    """AJAX view for inline student editing"""
    try:
        student = get_object_or_404(StudentProfile.objects.select_related('user'), pk=student_id)
        
        # Parse JSON data from request body
        data = json.loads(request.body)
        
        # Update user information
        if 'first_name' in data:
            student.user.first_name = data['first_name']
        if 'last_name' in data:
            student.user.last_name = data['last_name']
        if 'email' in data:
            student.user.email = data['email']
        
        # Update password if provided
        if 'password' in data and data['password']:
            student.user.set_password(data['password'])
        
        student.user.save()
        
        # Update student profile
        if 'roll_number' in data:
            student.roll_number = data['roll_number']
        if 'phone' in data:
            student.phone = data['phone']
        if 'address' in data:
            student.address = data['address']
        if 'current_form' in data:
            student.current_form = data['current_form']
        if 'father_name' in data:
            student.father_name = data['father_name']
        if 'mother_name' in data:
            student.mother_name = data['mother_name']
        if 'guardian_name' in data:
            student.guardian_name = data['guardian_name']
        if 'guardian_phone' in data:
            student.guardian_phone = data['guardian_phone']
        
        # Update department
        if 'department' in data and data['department']:
            student.department = get_object_or_404(Department, id=data['department'])
        
        student.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Student {student.user.get_full_name()} updated successfully!',
            'student': {
                'id': student.id,
                'first_name': student.user.first_name,
                'last_name': student.user.last_name,
                'email': student.user.email,
                'roll_number': student.roll_number,
                'phone': student.phone,
                'address': student.address,
                'current_form': student.current_form,
                'department': student.department.name if student.department else '',
                'department_id': student.department.id if student.department else '',
                'father_name': student.father_name,
                'mother_name': student.mother_name,
                'guardian_name': student.guardian_name,
                'guardian_phone': student.guardian_phone,
                'is_active': student.user.is_active,
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating student: {str(e)}'
        }, status=500)

@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET"])
def ajax_student_detail(request, student_id):
    """AJAX view to get student details for inline editing"""
    try:
        student = get_object_or_404(
            StudentProfile.objects.select_related('user', 'department'), 
            pk=student_id
        )
        
        return JsonResponse({
            'success': True,
            'student': {
                'id': student.id,
                'first_name': student.user.first_name,
                'last_name': student.user.last_name,
                'email': student.user.email,
                'roll_number': student.roll_number,
                'phone': student.phone,
                'address': student.address,
                'current_form': student.current_form,
                'department': student.department.name if student.department else '',
                'department_id': student.department.id if student.department else '',
                'father_name': student.father_name,
                'mother_name': student.mother_name,
                'guardian_name': student.guardian_name,
                'guardian_phone': student.guardian_phone,
                'is_active': student.user.is_active,
                'date_joined': student.user.date_joined.strftime('%Y-%m-%d') if student.user.date_joined else '',
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching student details: {str(e)}'
        }, status=500)
