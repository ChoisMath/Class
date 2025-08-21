from flask import render_template, request, jsonify, flash, redirect, url_for, session
from flask_login import login_required, current_user
from app.utils.decorators import admin_required, permission_required
from app.models.user import User
from app.services.supabase_service import supabase_service
from .admin_auth import admin_password_required, clear_admin_session
from app import db
from . import admin_bp

@admin_bp.route('/dashboard')
@login_required
@admin_required
@admin_password_required
def dashboard():
    """관리자 대시보드"""
    # Supabase에서 통계 데이터 조회
    all_users = supabase_service.get_all_users()
    
    stats = {
        'total_users': len(all_users),
        'total_students': len([u for u in all_users if u.get('role') == 'student']),
        'total_teachers': len([u for u in all_users if u.get('role') == 'teacher']),
        'total_admins': len([u for u in all_users if u.get('role') in ['admin', 'super_admin']]),
        'active_users': len([u for u in all_users if u.get('is_active', True)])
    }
    
    return render_template('admin/dashboard.html', 
                         user=current_user, 
                         stats=stats)

# users 경로는 user_management.py에서 처리됨

# 사용자 관련 모든 경로는 user_management.py에서 처리됨

@admin_bp.route('/system')
@login_required
@permission_required('manage_system')
def system():
    """시스템 설정"""
    return render_template('admin/system.html')

@admin_bp.route('/logs')
@login_required
@admin_required
def logs():
    """시스템 로그"""
    # TODO: 로그 데이터 조회 로직 구현
    logs = []
    return render_template('admin/logs.html', logs=logs)

@admin_bp.route('/backup')
@login_required
@permission_required('manage_system')
def backup():
    """백업 관리"""
    # TODO: 백업 관리 로직 구현
    return render_template('admin/backup.html')

@admin_bp.route('/reports')
@login_required
@admin_required
def reports():
    """관리자 리포트"""
    # TODO: 종합 리포트 데이터 조회 로직 구현
    report_data = {}
    return render_template('admin/reports.html', reports=report_data)