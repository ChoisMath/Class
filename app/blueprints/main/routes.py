from flask import render_template, redirect, url_for, current_app
from flask_login import current_user
from . import main_bp

@main_bp.route('/')
def index():
    """메인 페이지 - 사용자 역할에 따라 적절한 대시보드로 리디렉션"""
    current_app.logger.info(f'main.index 접근 - 인증상태: {current_user.is_authenticated}')
    
    if current_user.is_authenticated:
        current_app.logger.info(f'인증된 사용자: {current_user.email}, 역할: {current_user.role}')
        if current_user.is_student():
            current_app.logger.info('학생 대시보드로 리디렉션')
            return redirect(url_for('student.dashboard'))
        elif current_user.is_teacher():
            current_app.logger.info('교사 대시보드로 리디렉션')
            return redirect(url_for('teacher.dashboard'))
        elif current_user.is_admin():
            current_app.logger.info('관리자 대시보드로 리디렉션')
            return redirect(url_for('admin.dashboard'))
    
    current_app.logger.info('홈페이지 템플릿 렌더링')
    return render_template('main/index.html')

@main_bp.route('/about')
def about():
    """소개 페이지"""
    return render_template('main/about.html')

@main_bp.route('/contact')
def contact():
    """연락처 페이지"""
    return render_template('main/contact.html')

@main_bp.route('/sw.js')
def service_worker():
    """서비스 워커 파일 제공"""
    from flask import send_from_directory
    return send_from_directory('static', 'sw.js', mimetype='application/javascript')