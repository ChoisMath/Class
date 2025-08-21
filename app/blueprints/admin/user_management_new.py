from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.utils.decorators import admin_required, permission_required
from app.services.supabase_service import supabase_service
from .admin_auth import admin_password_required
from . import admin_bp

@admin_bp.route('/users-management')
@login_required
@admin_required
@admin_password_required
def user_management():
    """사용자 관리 페이지"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Supabase에서 사용자 목록 조회
    all_users = supabase_service.get_all_users(limit=per_page * 5)  # 충분한 데이터 가져오기
    
    # 간단한 페이지네이션 (실제로는 Supabase에서 offset 사용)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    users_page = all_users[start_idx:end_idx]
    
    # 페이지네이션 정보
    pagination_info = {
        'page': page,
        'per_page': per_page,
        'total': len(all_users),
        'pages': (len(all_users) + per_page - 1) // per_page,
        'has_prev': page > 1,
        'has_next': end_idx < len(all_users)
    }
    
    return render_template('admin/users.html', 
                         users=users_page, 
                         pagination=pagination_info)

@admin_bp.route('/users-management/create', methods=['GET', 'POST'])
@login_required
@admin_required
@admin_password_required
def create_user_admin():
    """새 사용자 생성"""
    if request.method == 'POST':
        try:
            # 기본 사용자 정보 (Google ID는 첫 로그인 시 자동 설정)
            user_data = {
                'email': request.form.get('email'),
                'name': request.form.get('name'),
                'role': request.form.get('role'),
                'is_active': request.form.get('is_active') == 'on'
            }
            
            # 사용자 생성
            new_user = supabase_service.create_user(user_data)
            
            if new_user:
                # 역할별 프로필 생성
                if user_data['role'] == 'student':
                    profile_data = {
                        'user_id': new_user[0]['id'],
                        'student_id': request.form.get('student_id'),
                        'grade': int(request.form.get('grade', 1)),
                        'class_number': int(request.form.get('class_number', 1)),
                        'admission_year': int(request.form.get('admission_year', 2024)),
                        'department': request.form.get('department'),
                        'phone': request.form.get('phone'),
                        'parent_phone': request.form.get('parent_phone')
                    }
                    supabase_service.create_student_profile(profile_data)
                    
                elif user_data['role'] == 'teacher':
                    profile_data = {
                        'user_id': new_user[0]['id'],
                        'employee_id': request.form.get('employee_id'),
                        'subject': request.form.get('subject'),
                        'responsibility': request.form.get('responsibility'),
                        'position': request.form.get('position'),
                        'department': request.form.get('department'),
                        'phone': request.form.get('phone'),
                        'office_location': request.form.get('office_location')
                    }
                    supabase_service.create_teacher_profile(profile_data)
                
                flash(f'{user_data["name"]} 사용자가 성공적으로 생성되었습니다.', 'success')
                return redirect(url_for('admin.user_management'))
            else:
                flash('사용자 생성 중 오류가 발생했습니다.', 'error')
                
        except Exception as e:
            flash(f'오류가 발생했습니다: {str(e)}', 'error')
    
    return render_template('admin/create_user.html')

@admin_bp.route('/users-management/<user_id>')
@login_required
@admin_required
@admin_password_required
def user_detail_admin(user_id):
    """사용자 상세 정보"""
    # Supabase에서 사용자 정보 조회
    all_users = supabase_service.get_all_users()
    user = next((u for u in all_users if u['id'] == user_id), None)
    
    if not user:
        flash('사용자를 찾을 수 없습니다.', 'error')
        return redirect(url_for('admin.user_management'))
    
    # 프로필 정보 조회
    profile = None
    if user['role'] == 'student':
        profile = supabase_service.get_student_profile(user_id)
    elif user['role'] == 'teacher':
        profile = supabase_service.get_teacher_profile(user_id)
    
    return render_template('admin/user_detail.html', user=user, profile=profile)

@admin_bp.route('/users-management/<user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
@admin_password_required
def toggle_user_status_admin(user_id):
    """사용자 활성화/비활성화 토글"""
    try:
        # 현재 사용자 상태 조회
        all_users = supabase_service.get_all_users()
        user = next((u for u in all_users if u['id'] == user_id), None)
        
        if not user:
            return jsonify({'error': '사용자를 찾을 수 없습니다.'}), 404
        
        # 상태 토글
        new_status = not user.get('is_active', True)
        result = supabase_service.update_user(user_id, {'is_active': new_status})
        
        if result:
            status_text = '활성화' if new_status else '비활성화'
            return jsonify({
                'message': f'{user["name"]}님의 계정이 {status_text}되었습니다.',
                'new_status': new_status
            })
        else:
            return jsonify({'error': '상태 업데이트에 실패했습니다.'}), 500
            
    except Exception as e:
        return jsonify({'error': f'오류가 발생했습니다: {str(e)}'}), 500

@admin_bp.route('/users-management/<user_id>/delete', methods=['POST'])
@login_required
@admin_required
@admin_password_required
def delete_user_admin(user_id):
    """사용자 삭제"""
    try:
        # 사용자 정보 조회
        all_users = supabase_service.get_all_users()
        user = next((u for u in all_users if u['id'] == user_id), None)
        
        if not user:
            flash('사용자를 찾을 수 없습니다.', 'error')
            return redirect(url_for('admin.user_management'))
        
        # 자기 자신 삭제 방지
        current_supabase_user = supabase_service.get_user_by_google_id(current_user.google_id)
        if current_supabase_user and current_supabase_user['id'] == user_id:
            flash('자기 자신의 계정은 삭제할 수 없습니다.', 'error')
            return redirect(url_for('admin.user_management'))
        
        # 사용자 삭제
        if supabase_service.delete_user(user_id):
            flash(f'{user["name"]} 사용자가 성공적으로 삭제되었습니다.', 'success')
        else:
            flash('사용자 삭제 중 오류가 발생했습니다.', 'error')
            
    except Exception as e:
        flash(f'오류가 발생했습니다: {str(e)}', 'error')
    
    return redirect(url_for('admin.user_management'))

@admin_bp.route('/logout-admin')
@login_required
@admin_required
def logout_admin():
    """관리자 모드 로그아웃"""
    from .admin_auth import clear_admin_session
    clear_admin_session()
    flash('관리자 모드에서 로그아웃되었습니다.', 'info')
    return redirect(url_for('main.index'))