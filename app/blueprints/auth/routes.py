from flask import render_template, redirect, url_for, request, session, flash, current_app
from flask_login import login_user, logout_user, current_user, login_required
from google.auth.transport.requests import Request
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import requests
import os

from . import auth_bp
from app.models.user import User
from app.services.supabase_service import supabase_service
from app import db

def get_base_url():
    """환경별 기본 URL 생성"""
    # Railway 프로덕션 환경
    if os.getenv('RAILWAY_ENVIRONMENT'):
        railway_domain = os.getenv('RAILWAY_STATIC_URL') or os.getenv('RAILWAY_PUBLIC_DOMAIN')
        if railway_domain:
            return f"https://{railway_domain}"
        # Railway 동적 도메인 패턴
        project_name = os.getenv('RAILWAY_PROJECT_NAME', 'testproject')
        return f"https://{project_name}.up.railway.app"
    
    # 개발 환경
    host = 'localhost'
    port = int(os.getenv('PORT', 5000))
    return f"http://{host}:{port}"

def get_client_secrets_config():
    """Google OAuth 클라이언트 설정 반환"""
    # 환경별 기본 URL 생성
    base_url = get_base_url()
    callback_url = f"{base_url}/auth/callback"
    
    return {
        "web": {
            "client_id": current_app.config['GOOGLE_CLIENT_ID'],
            "client_secret": current_app.config['GOOGLE_CLIENT_SECRET'],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [callback_url]
        }
    }

@auth_bp.route('/login')
def login():
    """Google OAuth 로그인"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # 환경별 기본 URL 생성
    base_url = get_base_url()
    callback_url = f"{base_url}/auth/callback"
    
    flow = Flow.from_client_config(
        get_client_secrets_config(),
        scopes=["https://www.googleapis.com/auth/userinfo.profile", 
                "https://www.googleapis.com/auth/userinfo.email", 
                "openid"],
        redirect_uri=callback_url
    )
    
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@auth_bp.route('/callback')
def callback():
    """Google OAuth 콜백 처리"""
    try:
        current_app.logger.info(f'OAuth callback started - URL: {request.url}')
        current_app.logger.info(f'Session state: {session.get("state")}')
        current_app.logger.info(f'Request state: {request.args.get("state")}')
        
        # 상태 확인
        if "state" not in session:
            current_app.logger.error('No state in session')
            flash('인증 세션이 만료되었습니다. 다시 로그인해주세요.', 'error')
            return redirect(url_for('auth.login'))
        
        # 환경별 기본 URL 생성 (로그인과 동일한 URL 사용)
        base_url = get_base_url()
        callback_url = f"{base_url}/auth/callback"
        current_app.logger.info(f'Using callback URL: {callback_url}')
        
        flow = Flow.from_client_config(
            get_client_secrets_config(),
            scopes=["https://www.googleapis.com/auth/userinfo.profile", 
                    "https://www.googleapis.com/auth/userinfo.email", 
                    "openid"],
            redirect_uri=callback_url,
            state=session["state"]
        )
        
        flow.fetch_token(authorization_response=request.url)
        current_app.logger.info('Token fetched successfully')
        
        if not session["state"] == request.args.get("state"):
            current_app.logger.error(f'State mismatch: session={session["state"]}, request={request.args.get("state")}')
            flash('인증 상태가 일치하지 않습니다.', 'error')
            return redirect(url_for('auth.login'))
        
        credentials = flow.credentials
        request_session = requests.session()
        cached_session = Request(session=request_session)
        
        id_info = id_token.verify_oauth2_token(
            id_token=credentials._id_token,
            request=cached_session,
            audience=current_app.config['GOOGLE_CLIENT_ID']
        )
        current_app.logger.info(f'ID token verified for email: {id_info.get("email")}')
        
        # Supabase에서 이메일로 사용자 확인
        user_email = id_info.get('email')
        current_app.logger.info(f'Checking user in Supabase: {user_email}')
        supabase_user = supabase_service.get_user_by_email(user_email)
        
        if not supabase_user:
            current_app.logger.warning(f'User not found in Supabase: {user_email}')
            flash(f'등록되지 않은 이메일입니다: {user_email}\n관리자에게 문의하세요.', 'error')
            return redirect(url_for('auth.login'))
        
        # is_active가 None이거나 False인 경우만 체크 (기본값 true 처리)
        is_active = supabase_user.get('is_active', True)  # 기본값 True
        if is_active is False:  # 명시적으로 False인 경우만
            current_app.logger.warning(f'Inactive user: {user_email}')
            flash('비활성화된 계정입니다. 관리자에게 문의하세요.', 'error')
            return redirect(url_for('auth.login'))
        
        # 프로필 이미지 업데이트
        try:
            current_app.logger.info(f'Updating profile image for user: {user_email}')
            result = supabase_service.update_user(supabase_user['id'], {
                'profile_image': id_info.get('picture')
            })
            if result:
                current_app.logger.info('Profile image updated successfully')
                supabase_user['profile_image'] = id_info.get('picture')
            else:
                current_app.logger.warning('Failed to update profile image in Supabase, continuing with login')
        except Exception as e:
            current_app.logger.warning(f'Error updating profile image: {e}, continuing with login')
        
        # Google 프로필 이미지를 포함한 사용자 데이터
        supabase_user_with_profile = supabase_user.copy()
        supabase_user_with_profile['profile_image'] = id_info.get('picture')
        
        # Flask-Login용 로컬 사용자 생성/업데이트 (email 기반)
        user = User.create_or_update_from_supabase(supabase_user_with_profile)
        current_app.logger.info(f'User created/updated: {user.email}, Role: {user.role}')
        
        # 로그인 처리
        login_user(user, remember=True)
        
        # Supabase에서 마지막 로그인 시간 업데이트
        supabase_service.update_last_login(supabase_user['id'])
        
        flash(f'환영합니다, {user.name}님!', 'success')
        
        # 다음 페이지로 리디렉션 또는 역할별 대시보드로 이동
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        
        return redirect(url_for('main.index'))
        
    except Exception as e:
        current_app.logger.error(f'OAuth callback error: {str(e)}', exc_info=True)
        flash('로그인 중 오류가 발생했습니다. 다시 시도해주세요.', 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
@login_required
def logout():
    """로그아웃"""
    user_name = current_user.name
    logout_user()
    session.clear()
    flash(f'{user_name}님, 안전하게 로그아웃되었습니다.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile')
@login_required
def profile():
    """사용자 프로필 페이지"""
    return render_template('auth/profile.html', user=current_user)