# Supabase 통합 학습 관리 시스템 설정 가이드

## 🗄️ 데이터베이스 설정

### 1. Supabase 프로젝트 생성
1. [Supabase](https://supabase.com)에 접속하여 새 프로젝트 생성
2. 프로젝트 대시보드에서 다음 정보 확인:
   - Project URL: `https://your-project-id.supabase.co`
   - API Key (anon public): `eyJ...`
   - API Key (service_role): `eyJ...`

### 2. 환경 변수 설정
`.env` 파일을 다음과 같이 업데이트하세요:

```env
# Google OAuth (기존)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
SECRET_KEY=your-secret-key

# Supabase 설정
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-public-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# 관리자 접근 비밀번호
ADMIN_PASSWORD=admin

# 로컬 데이터베이스 (Flask-Login용)
DATABASE_URL=sqlite:///app.db
```

### 3. 데이터베이스 테이블 생성
1. Supabase 대시보드 → SQL Editor로 이동
2. `create_tables.sql` 파일의 내용을 복사하여 실행
3. 테이블이 정상적으로 생성되었는지 확인

## 🚀 시스템 사용법

### 관리자 계정 설정 (간단해짐!)
1. Supabase → SQL Editor에서 `create_tables.sql` 실행
2. 파일 안의 관리자 계정 생성 부분을 실제 이메일로 수정:

```sql
-- 이 부분을 실제 이메일로 수정하세요
INSERT INTO users (email, name, role, is_active) VALUES
('your-actual-email@gmail.com', '관리자 이름', 'super_admin', true);
```

**이제 Google ID 없이 이메일만 있으면 됩니다!**

### 시스템 흐름 (개선됨!)
1. **Google OAuth 로그인** → Google에서 사용자 정보 받음
2. **이메일로 확인** → 해당 이메일이 Supabase에 등록되어 있는지 확인
3. **Google ID 자동 업데이트** → 첫 로그인 시 Google ID 자동 저장
4. **접근 제어** → 등록된 이메일만 로그인 허용
5. **역할별 리디렉션** → 학생/교사/관리자별 대시보드로 이동

## 📋 사용자 관리

### 관리자 모드 접속
1. `/admin/dashboard`로 접속
2. 환경변수에 설정된 관리자 비밀번호 입력 (기본값: `admin`)
3. 사용자 관리 기능 사용

### 사용자 생성
- **학생**: 학번, 학년, 반, 입학년도, 학과 등 설정
- **교사**: 직원번호, 담당교과, 담당업무, 직위 등 설정
- **관리자**: 기본 정보만 설정

## 🔐 보안 기능

### 접근 제어
- **데이터베이스 기반**: Supabase에 등록된 사용자만 로그인 가능
- **역할 기반**: 각 역할별로 접근 가능한 페이지 제한
- **관리자 보호**: 환경변수 비밀번호로 관리자 기능 보호

### Row Level Security (RLS)
- 사용자는 자신의 정보만 조회 가능
- 관리자만 전체 사용자 정보 관리 가능

## 🔧 개발 모드 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# 애플리케이션 실행
python run.py
```

## 📊 데이터베이스 구조

### users 테이블
- 기본 사용자 정보 (Google ID, 이메일, 이름, 역할 등)

### student_profiles 테이블
- 학생 상세 정보 (학번, 학년, 반, 입학년도 등)

### teacher_profiles 테이블
- 교사 상세 정보 (직원번호, 담당교과, 직위 등)

## 🚨 주의사항

1. **Supabase 설정**: 실제 프로젝트 URL과 API 키로 교체 필요
2. **관리자 비밀번호**: 운영 환경에서는 강력한 비밀번호 사용
3. **초기 데이터**: 첫 관리자 계정은 수동으로 데이터베이스에 추가
4. **Google OAuth**: redirect URI에 올바른 도메인 설정 필요

## ✨ 주요 기능

- ✅ Google OAuth 로그인
- ✅ 데이터베이스 기반 사용자 관리
- ✅ 역할별 접근 제어 (학생/교사/관리자)
- ✅ 관리자 비밀번호 보호
- ✅ 사용자 생성/수정/삭제
- ✅ 학생/교사별 상세 프로필
- ✅ 반응형 웹 디자인
- ✅ 성능 최적화