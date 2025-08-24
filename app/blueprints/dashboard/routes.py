from flask import render_template, redirect, url_for, request, jsonify, flash
from flask_login import login_required, current_user
from app.utils.decorators import admin_required, permission_required
from app.models.user import User
from app.services.supabase_service import supabase_service
from . import dashboard_bp

@dashboard_bp.route('/')
@login_required
def index():
    """통합 대시보드 메인 페이지 - 홈으로 리다이렉트"""
    return redirect(url_for('dashboard.home'))

@dashboard_bp.route('/home')
@login_required
def home():
    """시스템 현황 페이지"""
    navigation_items = get_navigation_items(current_user.role, 'home')
    return render_template('dashboard/home.html', 
                         user=current_user,
                         navigation_items=navigation_items)

def get_navigation_items(role, current_page='home'):
    """역할별 네비게이션 메뉴 구성 - 직접 URL 라우팅"""
    items = []
    
    if role == 'super_admin':
        items = [
            {'id': 'home', 'title': '시스템현황', 'icon': 'fas fa-chart-line', 'url': '/dashboard/', 'active': current_page == 'home'},
            {'id': 'user_management', 'title': '사용자 관리', 'icon': 'fas fa-users', 'url': '/dashboard/users', 'active': current_page == 'user_management'},
            {'id': 'school_management', 'title': '학교관리', 'icon': 'fas fa-school', 'url': '/dashboard/schools', 'active': current_page == 'school_management'},
            {'id': 'class_management', 'title': '학급관리', 'icon': 'fas fa-chalkboard-teacher', 'url': '/dashboard/classes', 'active': current_page == 'class_management'},
            {'id': 'attendance', 'title': '출석체크', 'icon': 'fas fa-calendar-check', 'url': '/dashboard/attendance', 'active': current_page == 'attendance'},
            {'id': 'seating', 'title': '자리배치 관리', 'icon': 'fas fa-chair', 'url': '/seating/', 'active': current_page == 'seating'}
        ]
    elif role == 'admin':
        items = [
            {'id': 'home', 'title': '시스템현황', 'icon': 'fas fa-chart-line', 'url': '/dashboard/', 'active': current_page == 'home'},
            {'id': 'user_management', 'title': '사용자 관리', 'icon': 'fas fa-users', 'url': '/dashboard/users', 'active': current_page == 'user_management'},
            {'id': 'school_management', 'title': '학교관리', 'icon': 'fas fa-school', 'url': '/dashboard/schools', 'active': current_page == 'school_management'},
            {'id': 'class_management', 'title': '학급관리', 'icon': 'fas fa-chalkboard-teacher', 'url': '/dashboard/classes', 'active': current_page == 'class_management'},
            {'id': 'attendance', 'title': '출석체크', 'icon': 'fas fa-calendar-check', 'url': '/dashboard/attendance', 'active': current_page == 'attendance'},
            {'id': 'seating', 'title': '자리배치 관리', 'icon': 'fas fa-chair', 'url': '/seating/', 'active': current_page == 'seating'}
        ]
    elif role == 'teacher':
        items = [
            {'id': 'home', 'title': '교사 대시보드', 'icon': 'fas fa-tachometer-alt', 'url': '/dashboard/', 'active': current_page == 'home'},
            {'id': 'class_management', 'title': '학급관리', 'icon': 'fas fa-chalkboard-teacher', 'url': '/dashboard/classes', 'active': current_page == 'class_management'},
            {'id': 'attendance', 'title': '출석체크', 'icon': 'fas fa-calendar-check', 'url': '/dashboard/attendance', 'active': current_page == 'attendance'},
            {'id': 'seating', 'title': '자리배치 관리', 'icon': 'fas fa-chair', 'url': '/seating/', 'active': current_page == 'seating'}
        ]
    elif role == 'student':
        items = [
            {'id': 'home', 'title': '학생 대시보드', 'icon': 'fas fa-tachometer-alt', 'url': '/dashboard/', 'active': current_page == 'home'},
            {'id': 'attendance', 'title': '출석체크', 'icon': 'fas fa-calendar-check', 'url': '/dashboard/attendance', 'active': current_page == 'attendance'}
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

# 개별 페이지 라우트들
@dashboard_bp.route('/users')
@login_required
@permission_required('manage_users')
def users():
    """사용자 관리 페이지"""
    navigation_items = get_navigation_items(current_user.role, 'user_management')
    return render_template('dashboard/users.html', 
                         user=current_user,
                         navigation_items=navigation_items,
                         current_page='user_management')

@dashboard_bp.route('/schools')
@login_required  
@permission_required('manage_schools')
def schools():
    """학교 관리 페이지"""
    navigation_items = get_navigation_items(current_user.role, 'school_management')
    return render_template('dashboard/schools.html', 
                         user=current_user,
                         navigation_items=navigation_items,
                         current_page='school_management')

@dashboard_bp.route('/classes')
@login_required
def classes():
    """학급 관리 페이지"""
    navigation_items = get_navigation_items(current_user.role, 'class_management') 
    return render_template('dashboard/classes.html', 
                         user=current_user,
                         navigation_items=navigation_items,
                         current_page='class_management')

@dashboard_bp.route('/attendance')
@login_required
def attendance():
    """출석체크 페이지"""
    navigation_items = get_navigation_items(current_user.role, 'attendance')
    return render_template('dashboard/attendance.html', 
                         user=current_user,
                         navigation_items=navigation_items,
                         current_page='attendance')

def has_page_access(role, page_type):
    """역할별 페이지 접근 권한 체크"""
    access_matrix = {
        'super_admin': ['home', 'user_management', 'school_management', 'class_management', 'attendance'],
        'admin': ['home', 'user_management', 'school_management', 'class_management', 'attendance'],
        'teacher': ['home', 'class_management', 'attendance'],
        'student': ['home', 'attendance']
    }
    
    return page_type in access_matrix.get(role, [])

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