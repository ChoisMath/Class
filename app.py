from flask import Flask, render_template, session, redirect, url_for, request
from google.auth.transport.requests import Request
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import os
from dotenv import load_dotenv
import pathlib
import requests

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Google OAuth 설정
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

client_secrets_file = {
    "web": {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["http://localhost:5000/callback"]
    }
}

def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
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
        client_secrets_file,
        scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
        redirect_uri=url_for('callback', _external=True)
    )
    
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@app.route("/callback")
def callback():
    flow = Flow.from_client_config(
        client_secrets_file,
        scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
        redirect_uri=url_for('callback', _external=True),
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
    
    session["google_id"] = id_info.get("sub")
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