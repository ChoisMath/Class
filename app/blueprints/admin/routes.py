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

@admin_bp.route('/users')
@login_required
@permission_required('manage_users')
def users():
    """사용자 관리"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    users = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/<int:user_id>')
@login_required
@permission_required('manage_users')
def user_detail(user_id):
    """사용자 상세 정보"""
    user = User.query.get_or_404(user_id)
    return render_template('admin/user_detail.html', user=user)

@admin_bp.route('/users/<int:user_id>/role', methods=['POST'])
@login_required
@permission_required('manage_users')
def update_user_role(user_id):
    """사용자 역할 변경"""
    user = User.query.get_or_404(user_id)
    new_role = request.json.get('role')
    
    if new_role not in ['student', 'teacher', 'admin']:
        return jsonify({'error': '유효하지 않은 역할입니다.'}), 400
    
    # 최고관리자만 admin 역할을 부여할 수 있음
    if new_role == 'admin' and current_user.role != 'super_admin':
        return jsonify({'error': '관리자 역할을 부여할 권한이 없습니다.'}), 403
    
    user.role = new_role
    db.session.commit()
    
    return jsonify({'message': f'{user.name}님의 역할이 {user.get_role_name()}로 변경되었습니다.'})

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