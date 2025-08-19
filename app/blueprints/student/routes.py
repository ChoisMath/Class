from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app.utils.decorators import student_required, permission_required
from . import student_bp

@student_bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    """학생 대시보드"""
    return render_template('student/dashboard.html', user=current_user)

@student_bp.route('/assignments')
@login_required
@permission_required('view_assignments')
def assignments():
    """과제 목록"""
    # TODO: 과제 데이터 조회 로직 구현
    assignments = []
    return render_template('student/assignments.html', assignments=assignments)

@student_bp.route('/grades')
@login_required
@permission_required('view_grades')
def grades():
    """성적 조회"""
    # TODO: 성적 데이터 조회 로직 구현
    grades = []
    return render_template('student/grades.html', grades=grades)

@student_bp.route('/schedule')
@login_required
@student_required
def schedule():
    """시간표"""
    # TODO: 시간표 데이터 조회 로직 구현
    schedule_data = {}
    return render_template('student/schedule.html', schedule=schedule_data)

@student_bp.route('/submissions')
@login_required
@permission_required('submit_assignments')
def submissions():
    """과제 제출 내역"""
    # TODO: 제출 내역 조회 로직 구현
    submissions = []
    return render_template('student/submissions.html', submissions=submissions)