from flask import render_template, redirect, url_for, request, jsonify, flash
from flask_login import login_required, current_user
from app.utils.decorators import admin_required, permission_required
from app.models.user import User
from app.services.supabase_service import supabase_service
from . import dashboard_bp

@dashboard_bp.route('/')
@login_required
def index():
    """통합 대시보드 메인 페이지"""
    # 사용자 역할에 따른 네비게이션 메뉴 구성
    navigation_items = get_navigation_items(current_user.role)
    
    # 기본 통계 데이터
    stats = get_dashboard_stats(current_user)
    
    return render_template('dashboard/index.html', 
                         user=current_user,
                         navigation_items=navigation_items,
                         stats=stats)

def get_navigation_items(role):
    """역할별 네비게이션 메뉴 구성 (DSHSLIFE 기준)"""
    items = []
    
    if role == 'super_admin':
        items = [
            {'id': 'home', 'title': '시스템현황', 'icon': 'fas fa-chart-line', 'active': True},
            {'id': 'user_management', 'title': '사용자 관리', 'icon': 'fas fa-users'},
            {'id': 'school_management', 'title': '학교관리', 'icon': 'fas fa-school'},
            {'id': 'class_management', 'title': '학급관리', 'icon': 'fas fa-chalkboard-teacher'},
            {'id': 'attendance', 'title': '출석체크', 'icon': 'fas fa-calendar-check'},
            {'id': 'seating', 'title': '자리배치 관리', 'icon': 'fas fa-chair', 'url': '/seating/'}
        ]
    elif role == 'admin':
        items = [
            {'id': 'home', 'title': '시스템현황', 'icon': 'fas fa-chart-line', 'active': True},
            {'id': 'user_management', 'title': '사용자 관리', 'icon': 'fas fa-users'},
            {'id': 'school_management', 'title': '학교관리', 'icon': 'fas fa-school'},
            {'id': 'class_management', 'title': '학급관리', 'icon': 'fas fa-chalkboard-teacher'},
            {'id': 'attendance', 'title': '출석체크', 'icon': 'fas fa-calendar-check'},
            {'id': 'seating', 'title': '자리배치 관리', 'icon': 'fas fa-chair', 'url': '/seating/'}
        ]
    elif role == 'teacher':
        items = [
            {'id': 'home', 'title': '교사 대시보드', 'icon': 'fas fa-tachometer-alt', 'active': True},
            {'id': 'class_management', 'title': '학급관리', 'icon': 'fas fa-chalkboard-teacher'},
            {'id': 'attendance', 'title': '출석체크', 'icon': 'fas fa-calendar-check'},
            {'id': 'seating', 'title': '자리배치 관리', 'icon': 'fas fa-chair', 'url': '/seating/'}
        ]
    elif role == 'student':
        items = [
            {'id': 'home', 'title': '학생 대시보드', 'icon': 'fas fa-tachometer-alt', 'active': True},
            {'id': 'attendance', 'title': '출석체크', 'icon': 'fas fa-calendar-check'}
        ]
    
    return items

def get_dashboard_stats(user):
    """대시보드 통계 데이터 조회"""
    stats = {}
    
    try:
        if user.role == 'super_admin':
            # 전체 시스템 통계
            all_users = supabase_service.get_all_users()
            stats = {
                'total_users': len(all_users),
                'total_students': len([u for u in all_users if u.get('role') == 'student']),
                'total_teachers': len([u for u in all_users if u.get('role') == 'teacher']),
                'total_admins': len([u for u in all_users if u.get('role') in ['admin', 'super_admin']]),
                'active_users': len([u for u in all_users if u.get('is_active', True)])
            }
        elif user.role == 'admin':
            # 학교 관리 통계
            stats = {
                'message': '학교 관리 기능을 이용하여 학교 정보를 설정하세요.'
            }
        elif user.role == 'teacher':
            # 학급 관리 통계
            stats = {
                'message': '학급 관리 기능을 이용하여 학급 정보를 관리하세요.'
            }
        elif user.role == 'student':
            # 출석 통계
            stats = {
                'message': '출석체크 기능을 이용하여 출석을 확인하세요.'
            }
    except Exception as e:
        print(f"Dashboard stats error: {e}")
        stats = {'message': '통계를 불러오는 중 오류가 발생했습니다.'}
    
    return stats

# AJAX 라우트 - 컨텐츠 동적 로딩
@dashboard_bp.route('/content/<content_type>')
@login_required  
def load_content(content_type):
    """역할별 컨텐츠 동적 로딩"""
    
    # 권한 체크
    if not has_content_access(current_user.role, content_type):
        return jsonify({'error': '접근 권한이 없습니다.'}), 403
    
    try:
        if content_type == 'home':
            return render_template('dashboard/content/home.html', user=current_user)
        elif content_type == 'user_management':
            return render_template('dashboard/content/user_management.html', user=current_user)
        elif content_type == 'school_management':
            return render_template('dashboard/content/school_management.html', user=current_user)
        elif content_type == 'class_management':
            return render_template('dashboard/content/class_management.html', user=current_user)
        elif content_type == 'attendance':
            return render_template('dashboard/content/attendance.html', user=current_user)
        else:
            return jsonify({'error': '존재하지 않는 컨텐츠입니다.'}), 404
            
    except Exception as e:
        return jsonify({'error': f'컨텐츠 로딩 중 오류가 발생했습니다: {str(e)}'}), 500

def has_content_access(role, content_type):
    """역할별 컨텐츠 접근 권한 체크 (DSHSLIFE 기준)"""
    access_matrix = {
        'super_admin': ['home', 'user_management', 'school_management', 'class_management', 'attendance'],
        'admin': ['home', 'user_management', 'school_management', 'class_management', 'attendance'],
        'teacher': ['home', 'class_management', 'attendance'],
        'student': ['home', 'attendance']
    }
    
    return content_type in access_matrix.get(role, [])

# API 엔드포인트 - 실시간 통계 데이터
@dashboard_bp.route('/api/stats')
@login_required
def get_stats_api():
    """실시간 시스템 통계 API"""
    try:
        stats = get_dashboard_stats(current_user)
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500