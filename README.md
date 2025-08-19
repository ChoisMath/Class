# Flask Google Login App

Google OAuth를 사용하여 로그인 기능을 구현한 Flask 애플리케이션입니다.

## 설정 방법

### 1. Google Cloud Console 설정

1. [Google Cloud Console](https://console.cloud.google.com/)에 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. "APIs & Services" > "Credentials" 이동
4. "CREATE CREDENTIALS" > "OAuth client ID" 선택
5. Application type을 "Web application"으로 선택
6. Authorized redirect URIs에 `http://localhost:5000/callback` 추가
7. Client ID와 Client Secret을 복사

### 2. 환경 변수 설정

`.env` 파일을 수정하여 Google OAuth 정보를 입력하세요:

```
GOOGLE_CLIENT_ID=your_actual_google_client_id
GOOGLE_CLIENT_SECRET=your_actual_google_client_secret
SECRET_KEY=your_random_secret_key
```

### 3. 의존성 설치 및 실행

```bash
pip install -r requirements.txt
python app.py
```

애플리케이션이 http://localhost:5000에서 실행됩니다.

## 사용 방법

1. 홈페이지에서 "Google로 로그인" 버튼 클릭
2. Google 계정으로 로그인
3. 로그인 성공 시 "hello, this is my class" 메시지가 표시됩니다
4. "로그아웃" 버튼으로 로그아웃 가능