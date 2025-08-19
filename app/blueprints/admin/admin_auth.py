from flask import request, render_template, redirect, url_for, session, flash
from functools import wraps
import os

def admin_password_required(f):
    """관리자 비밀번호 인증이 필요한 라우트를 보호하는 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 이미 관리자 인증을 통과한 경우
        if session.get('admin_authenticated'):
            return f(*args, **kwargs)
        
        # POST 요청으로 비밀번호가 전송된 경우
        if request.method == 'POST' and request.form.get('admin_password'):
            admin_password = os.getenv('ADMIN_PASSWORD', 'admin')
            entered_password = request.form.get('admin_password')
            
            if entered_password == admin_password:
                session['admin_authenticated'] = True
                session.permanent = True  # 세션 지속
                flash('관리자 모드로 접속되었습니다.', 'success')
                return f(*args, **kwargs)
            else:
                flash('잘못된 관리자 비밀번호입니다.', 'error')
        
        # 비밀번호 입력 폼 표시
        return render_template('admin/admin_login.html')
    
    return decorated_function

def clear_admin_session():
    """관리자 세션 정리"""
    if 'admin_authenticated' in session:
        del session['admin_authenticated']