from flask import render_template, redirect, url_for
from flask_login import current_user
from . import main_bp

@main_bp.route('/')
def index():
    """메인 페이지 - 사용자 역할에 따라 적절한 대시보드로 리디렉션"""
    if current_user.is_authenticated:
        if current_user.is_student():
            return redirect(url_for('student.dashboard'))
        elif current_user.is_teacher():
            return redirect(url_for('teacher.dashboard'))
        elif current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
    
    return render_template('main/index.html')

@main_bp.route('/about')
def about():
    """소개 페이지"""
    return render_template('main/about.html')

@main_bp.route('/contact')
def contact():
    """연락처 페이지"""
    return render_template('main/contact.html')