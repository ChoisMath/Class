#!/usr/bin/env python3
"""
Google OAuth 설정 디버깅 도구
"""

import os
from app import create_app
from config import Config

def debug_oauth_configuration():
    """OAuth 설정 디버깅"""
    print("=== Google OAuth Configuration Debug ===\n")
    
    # 환경 변수 확인
    print("1. Environment Variables:")
    print(f"   GOOGLE_CLIENT_ID: {'[SET]' if os.getenv('GOOGLE_CLIENT_ID') else '[NOT SET]'}")
    print(f"   GOOGLE_CLIENT_SECRET: {'[SET]' if os.getenv('GOOGLE_CLIENT_SECRET') else '[NOT SET]'}")
    print(f"   RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT', '[NOT SET] (로컬 개발)')}")
    print(f"   PORT: {os.getenv('PORT', '5000 (기본값)')}")
    print()
    
    # URL 생성 확인
    print("2. Generated URLs:")
    base_url = Config.get_base_url()
    print(f"   Base URL: {base_url}")
    print(f"   Login URL: {base_url}/auth/login")
    print(f"   Callback URL: {base_url}/auth/callback")
    print()
    
    # Google Console 설정 가이드
    print("3. Google Console Configuration:")
    print("   다음 URL을 Google Console에 등록하세요:")
    print(f"   [REQUIRED] Authorized redirect URI: {base_url}/auth/callback")
    print()
    
    # 환경별 설정 확인
    print("4. Environment-specific Settings:")
    if os.getenv('RAILWAY_ENVIRONMENT'):
        print("   [PRODUCTION] Railway Environment")
        print("   - HTTPS 필수")
        print("   - Railway 도메인 사용")
        print("   - OAUTHLIB_INSECURE_TRANSPORT 비활성화")
    else:
        print("   [DEVELOPMENT] Local Environment")
        print("   - HTTP 허용 (OAUTHLIB_INSECURE_TRANSPORT=1)")
        print("   - localhost:5000 사용")
        print("   - 개발 중에만 사용")
    print()
    
    # 문제 해결 가이드
    print("5. Troubleshooting Guide:")
    print("   [ERROR] Redirect URI Mismatch:")
    print(f"      -> Google Console에서 정확히 이 URL을 등록하세요: {base_url}/auth/callback")
    print("   [ERROR] HTTPS 요구 오류:")
    print("      -> 개발 환경: OAUTHLIB_INSECURE_TRANSPORT=1 설정")
    print("      -> 프로덕션: HTTPS 사용 필수")
    print()

if __name__ == '__main__':
    debug_oauth_configuration()