from functools import wraps
from flask import abort, redirect, url_for, request, flash
from flask_login import current_user

def role_required(*roles):
    """특정 역할이 필요한 라우트를 보호하는 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login', next=request.url))
            
            if current_user.role not in roles:
                flash('접근 권한이 없습니다.', 'error')
                abort(403)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def permission_required(permission):
    """특정 권한이 필요한 라우트를 보호하는 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login', next=request.url))
            
            if not current_user.has_permission(permission):
                flash('해당 기능을 사용할 권한이 없습니다.', 'error')
                abort(403)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def student_required(func):
    """학생 전용 데코레이터"""
    return role_required('student')(func)

def teacher_required(func):
    """교사 전용 데코레이터"""
    return role_required('teacher')(func)

def admin_required(func):
    """관리자 전용 데코레이터"""
    return role_required('admin', 'super_admin')(func)

def ajax_required(func):
    """AJAX 요청만 허용하는 데코레이터"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not request.is_json:
            abort(400)
        return func(*args, **kwargs)
    return wrapper