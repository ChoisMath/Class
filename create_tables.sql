-- Supabase 데이터베이스 테이블 생성 스크립트
-- 이 스크립트를 Supabase SQL 에디터에서 실행하세요

-- 사용자 기본 정보 테이블
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    google_id VARCHAR(255) UNIQUE, -- NULL 허용 (처음 로그인 시 자동 설정)
    email VARCHAR(255) UNIQUE NOT NULL, -- 이메일을 주요 식별자로 사용
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('student', 'teacher', 'admin', 'super_admin')),
    profile_image VARCHAR(500),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);

-- 학생 상세 정보 테이블
CREATE TABLE IF NOT EXISTS student_profiles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    student_id VARCHAR(50) UNIQUE, -- 학번
    grade INTEGER CHECK (grade >= 1 AND grade <= 12), -- 학년 (1-12)
    class_number INTEGER CHECK (class_number >= 1), -- 반
    admission_year INTEGER CHECK (admission_year >= 1900), -- 입학년도
    department VARCHAR(100), -- 학과/전공
    phone VARCHAR(20),
    parent_phone VARCHAR(20), -- 보호자 연락처
    address TEXT,
    birth_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 교사 상세 정보 테이블
CREATE TABLE IF NOT EXISTS teacher_profiles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    employee_id VARCHAR(50) UNIQUE, -- 직원번호
    subject VARCHAR(100), -- 담당교과
    responsibility VARCHAR(200), -- 담당업무
    position VARCHAR(100), -- 직위 (교사, 부장교사, 교감, 교장 등)
    department VARCHAR(100), -- 소속 부서
    hire_date DATE, -- 입사일
    office_location VARCHAR(100), -- 사무실 위치
    extension_number VARCHAR(20), -- 내선번호
    phone VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 인덱스 생성 (성능 최적화)
CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_student_profiles_user_id ON student_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_student_profiles_student_id ON student_profiles(student_id);
CREATE INDEX IF NOT EXISTS idx_teacher_profiles_user_id ON teacher_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_teacher_profiles_employee_id ON teacher_profiles(employee_id);

-- 업데이트 시간 자동 갱신 함수
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 트리거 생성
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_student_profiles_updated_at 
    BEFORE UPDATE ON student_profiles 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_teacher_profiles_updated_at 
    BEFORE UPDATE ON teacher_profiles 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS) 정책 설정
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE teacher_profiles ENABLE ROW LEVEL SECURITY;

-- 사용자는 자신의 정보만 조회 가능
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid()::text = google_id);

-- 관리자는 모든 사용자 정보 관리 가능
CREATE POLICY "Admins can manage all users" ON users
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE google_id = auth.uid()::text 
            AND role IN ('admin', 'super_admin')
        )
    );

-- 학생은 자신의 프로필만 조회 가능
CREATE POLICY "Students can view own profile" ON student_profiles
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id = student_profiles.user_id 
            AND google_id = auth.uid()::text
        )
    );

-- 교사는 자신의 프로필만 조회 가능
CREATE POLICY "Teachers can view own profile" ON teacher_profiles
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id = teacher_profiles.user_id 
            AND google_id = auth.uid()::text
        )
    );

-- 샘플 데이터 삽입 (테스트용)
-- 이제 이메일만으로 사용자를 식별합니다

-- 초기 관리자 계정 생성 예시 (실제 이메일로 교체하세요)
INSERT INTO users (email, name, role, is_active) VALUES
('your-email@gmail.com', '관리자 이름', 'super_admin', true);

-- 추가 사용자 예시
/*
INSERT INTO users (email, name, role, is_active) VALUES
('teacher@example.com', '김선생', 'teacher', true),
('student@example.com', '이학생', 'student', true);

INSERT INTO teacher_profiles (user_id, employee_id, subject, responsibility, position, department, hire_date) VALUES
((SELECT id FROM users WHERE email = 'teacher@example.com'), 'T2024001', '수학', '3학년 담임', '교사', '수학과', '2024-03-01');

INSERT INTO student_profiles (user_id, student_id, grade, class_number, admission_year, department) VALUES
((SELECT id FROM users WHERE email = 'student@example.com'), '2024001', 11, 1, 2024, '일반계');
*/