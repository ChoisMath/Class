from flask import Flask, render_template, session, redirect, url_for, request
from google.auth.transport.requests import Request
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import os
import pathlib
import requests

# 개발 환경에서만 .env 파일 로드 (Railway에서는 무시됨)
try:
    if os.getenv('RAILWAY_ENVIRONMENT') is None:  # Railway 환경이 아닌 경우만
        from dotenv import load_dotenv
        load_dotenv()
except ImportError:
    # dotenv가 설치되지 않은 경우 (프로덕션)
    pass

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Google OAuth 설정
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

# 환경에 따라 redirect URI 설정
def get_redirect_uri():
    if os.getenv('RAILWAY_ENVIRONMENT'):
        # Railway 환경: 자동으로 도메인을 감지하거나 환경변수에서 가져옴
        base_url = os.getenv('RAILWAY_PUBLIC_DOMAIN', 'your-app.railway.app')
        if not base_url.startswith('http'):
            base_url = f'https://{base_url}'
        return f'{base_url}/callback'
    else:
        # 로컬 개발 환경
        return 'http://localhost:5000/callback'

def get_client_secrets_file():
    return {
        "web": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [get_redirect_uri()]
        }
    }

def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "email" not in session:
            return redirect(url_for('login'))
        else:
            return function(*args, **kwargs)
    wrapper.__name__ = function.__name__
    return wrapper

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/login")
def login():
    flow = Flow.from_client_config(
        get_client_secrets_file(),
        scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
        redirect_uri=get_redirect_uri()
    )
    
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@app.route("/callback")
def callback():
    flow = Flow.from_client_config(
        get_client_secrets_file(),
        scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
        redirect_uri=get_redirect_uri(),
        state=session["state"]
    )
    
    flow.fetch_token(authorization_response=request.url)
    
    if not session["state"] == request.args.get("state"):
        return "State does not match!", 500
    
    credentials = flow.credentials
    request_session = requests.session()
    cached_session = Request(session=request_session)
    
    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=cached_session,
        audience=GOOGLE_CLIENT_ID
    )
    
    session["name"] = id_info.get("name")
    session["email"] = id_info.get("email")
    
    return redirect(url_for('protected_area'))

@app.route("/protected_area")
@login_is_required
def protected_area():
    return render_template('protected.html', name=session.get('name'))

@app.route("/logout")
@login_is_required
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == "__main__":
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run(host='localhost', port=5000, debug=True)