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
-- 주의: 현재 email 기반 인증을 사용하므로 RLS는 비활성화됩니다
-- 필요시 나중에 email 기반 RLS 정책으로 업데이트 가능

-- ALTER TABLE users ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE student_profiles ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE teacher_profiles ENABLE ROW LEVEL SECURITY;

-- 향후 email 기반 RLS 정책 예시 (현재 비활성화)
-- CREATE POLICY "Users can view own profile" ON users
--     FOR SELECT USING (email = current_setting('app.current_user_email', true));

-- CREATE POLICY "Admins can manage all users" ON users
--     FOR ALL USING (
--         EXISTS (
--             SELECT 1 FROM users 
--             WHERE email = current_setting('app.current_user_email', true)
--             AND role IN ('admin', 'super_admin')
--         )
--     );

-- 샘플 데이터 삽입 (테스트용)
-- 이제 이메일만으로 사용자를 식별합니다

-- 초기 관리자 계정 생성 예시 (실제 이메일로 교체하세요)
INSERT INTO users (email, name, role, is_active) VALUES
('your-email@gmail.com', '관리자 이름', 'super_admin', true);

-- 학교 정보 테이블
CREATE TABLE IF NOT EXISTS schools (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    grade_count INTEGER CHECK (grade_count >= 1 AND grade_count <= 12),
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(255),
    website VARCHAR(255),
    principal_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 학급 정보 테이블
CREATE TABLE IF NOT EXISTS classes (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    grade INTEGER CHECK (grade >= 1 AND grade <= 12),
    class_number INTEGER CHECK (class_number >= 1),
    class_name VARCHAR(100), -- 학급명 (예: 1-1, 컴퓨터과 1반)
    teacher_email VARCHAR(255), -- 담임교사 이메일
    room_number VARCHAR(50), -- 교실 번호
    max_students INTEGER DEFAULT 30,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(school_id, grade, class_number)
);

-- 출석 기록 테이블
CREATE TABLE IF NOT EXISTS attendance (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    student_email VARCHAR(255) NOT NULL,
    class_id UUID REFERENCES classes(id) ON DELETE CASCADE,
    attendance_date DATE NOT NULL,
    period INTEGER CHECK (period >= 1 AND period <= 10), -- 교시 (1-10교시)
    status VARCHAR(20) CHECK (status IN ('출석', '지각', '조퇴', '결석', '공결')) DEFAULT '출석',
    note TEXT, -- 특이사항
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(student_email, class_id, attendance_date, period)
);

-- 학생-학급 연결 테이블 (학생이 여러 학급에 속할 수 있도록)
CREATE TABLE IF NOT EXISTS student_classes (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    student_email VARCHAR(255) NOT NULL,
    class_id UUID REFERENCES classes(id) ON DELETE CASCADE,
    enrollment_date DATE DEFAULT CURRENT_DATE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(student_email, class_id)
);

-- 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_schools_name ON schools(name);
CREATE INDEX IF NOT EXISTS idx_classes_school_id ON classes(school_id);
CREATE INDEX IF NOT EXISTS idx_classes_teacher_email ON classes(teacher_email);
CREATE INDEX IF NOT EXISTS idx_attendance_student_email ON attendance(student_email);
CREATE INDEX IF NOT EXISTS idx_attendance_class_id ON attendance(class_id);
CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance(attendance_date);
CREATE INDEX IF NOT EXISTS idx_student_classes_student_email ON student_classes(student_email);
CREATE INDEX IF NOT EXISTS idx_student_classes_class_id ON student_classes(class_id);

-- 업데이트 트리거 추가
CREATE TRIGGER update_schools_updated_at 
    BEFORE UPDATE ON schools 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_classes_updated_at 
    BEFORE UPDATE ON classes 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_attendance_updated_at 
    BEFORE UPDATE ON attendance 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_student_classes_updated_at 
    BEFORE UPDATE ON student_classes 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- 추가 사용자 예시
/*
INSERT INTO users (email, name, role, is_active) VALUES
('teacher@example.com', '김선생', 'teacher', true),
('student@example.com', '이학생', 'student', true);

INSERT INTO teacher_profiles (user_id, employee_id, subject, responsibility, position, department, hire_date) VALUES
((SELECT id FROM users WHERE email = 'teacher@example.com'), 'T2024001', '수학', '3학년 담임', '교사', '수학과', '2024-03-01');

INSERT INTO student_profiles (user_id, student_id, grade, class_number, admission_year, department) VALUES
((SELECT id FROM users WHERE email = 'student@example.com'), '2024001', 11, 1, 2024, '일반계');

-- 샘플 학교 및 학급 데이터
INSERT INTO schools (name, grade_count, address, phone, principal_name) VALUES
('테스트 고등학교', 3, '서울시 강남구', '02-1234-5678', '김교장');

INSERT INTO classes (school_id, grade, class_number, class_name, teacher_email, room_number) VALUES
((SELECT id FROM schools WHERE name = '테스트 고등학교'), 1, 1, '1학년 1반', 'teacher@example.com', '101');

INSERT INTO student_classes (student_email, class_id) VALUES
('student@example.com', (SELECT id FROM classes WHERE class_name = '1학년 1반'));
*/