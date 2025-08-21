#!/usr/bin/env python3
"""
Flask 애플리케이션 실행 스크립트
"""

import os
from app import create_app, db
from app.models.user import User

app = create_app()

@app.cli.command()
def init_db():
    """데이터베이스 초기화"""
    db.create_all()
    print('데이터베이스가 초기화되었습니다.')

@app.cli.command()
def create_admin():
    """최고관리자 계정 생성 (테스트용)"""
    admin_email = input('관리자 이메일: ')
    admin_name = input('관리자 이름: ')
    admin_google_id = input('Google ID (테스트용): ')
    
    # 기존 사용자 확인
    existing_user = User.query.filter_by(email=admin_email).first()
    if existing_user:
        print(f'이미 존재하는 사용자입니다: {existing_user.email}')
        return
    
    # 관리자 생성
    admin = User(
        google_id=admin_google_id,
        email=admin_email,
        name=admin_name,
        role='super_admin'
    )
    
    db.session.add(admin)
    db.session.commit()
    print(f'관리자 계정이 생성되었습니다: {admin.email}')

if __name__ == '__main__':
    # 개발 환경에서만 HTTPS 비활성화
    if os.getenv('FLASK_ENV') != 'production':
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    
    # 데이터베이스 자동 생성
    with app.app_context():
        db.create_all()
    
    # 프로덕션 환경에서는 Railway가 포트를 지정
    port = int(os.getenv('PORT', 5000))
    host = '0.0.0.0' if os.getenv('FLASK_ENV') == 'production' else 'localhost'
    debug = os.getenv('FLASK_ENV') != 'production'
    
    app.run(host=host, port=port, debug=debug)