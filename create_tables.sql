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
('complete860127@gmail.com', 'Chois', 'super_admin', true);

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
    teacher_name VARCHAR(100), -- 담임교사 명
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

-- 테스트용 샘플 데이터 (개발 및 데모용)
-- 운영 환경에서는 주석 처리하거나 삭제하세요

-- 추가 사용자 데이터
INSERT INTO users (email, name, role, is_active) VALUES
('teacher1@school.com', '김영희', 'teacher', true),
('teacher2@school.com', '박철수', 'teacher', true),
('teacher3@school.com', '이미숙', 'teacher', true),
('admin@school.com', '관리자', 'admin', true),
('student1@school.com', '홍길동', 'student', true),
('student2@school.com', '김철수', 'student', true),
('student3@school.com', '이영희', 'student', true),
('student4@school.com', '박민수', 'student', true),
('student5@school.com', '최지현', 'student', true),
('student6@school.com', '정하늘', 'student', true),
('student7@school.com', '강감찬', 'student', true),
('student8@school.com', '윤보선', 'student', true),
('student9@school.com', '서장훈', 'student', true),
('student10@school.com', '김유신', 'student', true)
ON CONFLICT (email) DO NOTHING;

-- 교사 프로필 데이터
INSERT INTO teacher_profiles (user_id, employee_id, subject, responsibility, position, department, hire_date, phone) VALUES
((SELECT id FROM users WHERE email = 'teacher1@school.com'), 'T2024001', '수학', '1학년 담임', '교사', '수학과', '2024-03-01', '010-1234-5678'),
((SELECT id FROM users WHERE email = 'teacher2@school.com'), 'T2024002', '국어', '2학년 담임', '교사', '국어과', '2024-03-01', '010-2345-6789'),
((SELECT id FROM users WHERE email = 'teacher3@school.com'), 'T2024003', '영어', '3학년 담임', '부장교사', '영어과', '2023-03-01', '010-3456-7890')
ON CONFLICT (employee_id) DO NOTHING;

-- 학생 프로필 데이터
INSERT INTO student_profiles (user_id, student_id, grade, class_number, admission_year, department, phone, parent_phone) VALUES
((SELECT id FROM users WHERE email = 'student1@school.com'), '11001', 1, 1, 2024, '일반계', '010-1111-1111', '010-9111-1111'),
((SELECT id FROM users WHERE email = 'student2@school.com'), '11002', 1, 1, 2024, '일반계', '010-1111-1112', '010-9111-1112'),
((SELECT id FROM users WHERE email = 'student3@school.com'), '11003', 1, 1, 2024, '일반계', '010-1111-1113', '010-9111-1113'),
((SELECT id FROM users WHERE email = 'student4@school.com'), '11004', 1, 1, 2024, '일반계', '010-1111-1114', '010-9111-1114'),
((SELECT id FROM users WHERE email = 'student5@school.com'), '11005', 1, 1, 2024, '일반계', '010-1111-1115', '010-9111-1115'),
((SELECT id FROM users WHERE email = 'student6@school.com'), '21001', 2, 1, 2023, '일반계', '010-2111-1111', '010-9211-1111'),
((SELECT id FROM users WHERE email = 'student7@school.com'), '21002', 2, 1, 2023, '일반계', '010-2111-1112', '010-9211-1112'),
((SELECT id FROM users WHERE email = 'student8@school.com'), '21003', 2, 1, 2023, '일반계', '010-2111-1113', '010-9211-1113'),
((SELECT id FROM users WHERE email = 'student9@school.com'), '31001', 3, 1, 2022, '일반계', '010-3111-1111', '010-9311-1111'),
((SELECT id FROM users WHERE email = 'student10@school.com'), '31002', 3, 1, 2022, '일반계', '010-3111-1112', '010-9311-1112')
ON CONFLICT (student_id) DO NOTHING;

-- 샘플 학교 데이터
INSERT INTO schools (name, grade_count, address, phone, email, principal_name, website) VALUES
('대한고등학교', 3, '서울시 강남구 테헤란로 123', '02-1234-5678', 'info@daehan.school.kr', '김대한', 'http://www.daehan.school.kr'),
('서울과학고등학교', 3, '서울시 서초구 과학로 456', '02-2345-6789', 'info@seoul-science.hs.kr', '이과학', 'http://www.seoul-science.hs.kr'),
('미래국제고등학교', 3, '서울시 송파구 미래로 789', '02-3456-7890', 'info@future-intl.hs.kr', '박미래', 'http://www.future-intl.hs.kr')
ON CONFLICT DO NOTHING;

-- 샘플 학급 데이터
INSERT INTO classes (school_id, grade, class_number, teacher_name, teacher_email, room_number, max_students) VALUES
((SELECT id FROM schools WHERE name = '대한고등학교'), 1, 1, '김영희', 'teacher1@school.com', '101', 30),
((SELECT id FROM schools WHERE name = '대한고등학교'), 1, 2, '김영희', 'teacher1@school.com', '102', 30),
((SELECT id FROM schools WHERE name = '대한고등학교'), 2, 1, '박철수', 'teacher2@school.com', '201', 28),
((SELECT id FROM schools WHERE name = '대한고등학교'), 2, 2, '박철수', 'teacher2@school.com', '202', 28),
((SELECT id FROM schools WHERE name = '대한고등학교'), 3, 1, '이미숙', 'teacher3@school.com', '301', 25),
((SELECT id FROM schools WHERE name = '서울과학고등학교'), 1, 1, '김영희', 'teacher1@school.com', 'S101', 20),
((SELECT id FROM schools WHERE name = '미래국제고등학교'), 1, 1, '박철수', 'teacher2@school.com', 'I101', 25)
ON CONFLICT (school_id, grade, class_number) DO NOTHING;

-- 학생-학급 연결 데이터
INSERT INTO student_classes (student_email, class_id) VALUES
('student1@school.com', (SELECT id FROM classes WHERE grade = 1 AND class_number = 1 AND school_id = (SELECT id FROM schools WHERE name = '대한고등학교'))),
('student2@school.com', (SELECT id FROM classes WHERE grade = 1 AND class_number = 1 AND school_id = (SELECT id FROM schools WHERE name = '대한고등학교'))),
('student3@school.com', (SELECT id FROM classes WHERE grade = 1 AND class_number = 1 AND school_id = (SELECT id FROM schools WHERE name = '대한고등학교'))),
('student4@school.com', (SELECT id FROM classes WHERE grade = 1 AND class_number = 1 AND school_id = (SELECT id FROM schools WHERE name = '대한고등학교'))),
('student5@school.com', (SELECT id FROM classes WHERE grade = 1 AND class_number = 1 AND school_id = (SELECT id FROM schools WHERE name = '대한고등학교'))),
('student6@school.com', (SELECT id FROM classes WHERE grade = 2 AND class_number = 1 AND school_id = (SELECT id FROM schools WHERE name = '대한고등학교'))),
('student7@school.com', (SELECT id FROM classes WHERE grade = 2 AND class_number = 1 AND school_id = (SELECT id FROM schools WHERE name = '대한고등학교'))),
('student8@school.com', (SELECT id FROM classes WHERE grade = 2 AND class_number = 1 AND school_id = (SELECT id FROM schools WHERE name = '대한고등학교'))),
('student9@school.com', (SELECT id FROM classes WHERE grade = 3 AND class_number = 1 AND school_id = (SELECT id FROM schools WHERE name = '대한고등학교'))),
('student10@school.com', (SELECT id FROM classes WHERE grade = 3 AND class_number = 1 AND school_id = (SELECT id FROM schools WHERE name = '대한고등학교')))
ON CONFLICT (student_email, class_id) DO NOTHING;

-- =============================================================================
-- 자리배치표 기반 자율학습 관리 시스템 테이블
-- =============================================================================

-- 자리배치 관리 테이블
CREATE TABLE IF NOT EXISTS seat_arrangements (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    classroom VARCHAR(50) NOT NULL, -- 교실명 (예: grade_1, grade_2, grade_3)
    position_key VARCHAR(20) NOT NULL, -- 좌석 위치 키 (예: "1-A-L", "2-B-R", "3-C-N")
    student_emails TEXT[] DEFAULT '{}', -- 학생 이메일 배열 (PostgreSQL 배열)
    arrangement_date DATE DEFAULT CURRENT_DATE,
    created_by UUID REFERENCES users(id), -- 배치를 만든 사용자
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(classroom, position_key, arrangement_date)
);

-- 출석 및 부재 관리 테이블
CREATE TABLE IF NOT EXISTS attendance_records (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    attendance_date DATE NOT NULL,
    period INTEGER NOT NULL CHECK (period >= 1 AND period <= 25), -- 교시 (1-7: 일반교시, 11-15: 자습, 21-25: 식사/외박)
    student_id UUID REFERENCES users(id) ON DELETE CASCADE,
    student_email VARCHAR(255) NOT NULL, -- 이메일도 저장 (성능 최적화)
    status VARCHAR(20) DEFAULT 'present' CHECK (status IN ('present', 'absent', 'returned', 'activity')),
    marked_by UUID REFERENCES users(id), -- 처리한 교사
    marked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    returned_by UUID REFERENCES users(id), -- 복귀 처리한 교사
    returned_at TIMESTAMP WITH TIME ZONE,
    notes TEXT, -- 특이사항
    activity_type VARCHAR(100), -- 활동 유형 (분임토의실, 특별활동 등)
    activity_location VARCHAR(100), -- 활동 장소
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 교시 설정 테이블
CREATE TABLE IF NOT EXISTS period_configs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    config_date DATE NOT NULL UNIQUE,
    is_holiday BOOLEAN DEFAULT false,
    regular_periods INTEGER[] DEFAULT ARRAY[1,2,3,4,5,6,7], -- 일반교시
    study_periods INTEGER[] DEFAULT ARRAY[11,12,13,14,15], -- 자습시간
    meal_periods INTEGER[] DEFAULT ARRAY[22,23], -- 중식, 석식
    special_periods INTEGER[] DEFAULT ARRAY[21,25], -- 조식, 외박
    period_info JSONB, -- 교시별 상세 정보 (시간, 설명 등)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 교실 레이아웃 설정 테이블
CREATE TABLE IF NOT EXISTS classroom_layouts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    classroom_key VARCHAR(50) NOT NULL UNIQUE, -- grade_1, grade_2, grade_3
    classroom_name VARCHAR(100) NOT NULL, -- 1학년, 2학년, 3학년
    layout_config JSONB NOT NULL, -- 교실 레이아웃 설정 (JSON)
    bottom_left_info VARCHAR(200), -- 하단 왼쪽 정보 (출입구 등)
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 감독교사 스케줄 테이블
CREATE TABLE IF NOT EXISTS supervisor_schedules (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    schedule_date DATE NOT NULL,
    grade INTEGER NOT NULL CHECK (grade >= 1 AND grade <= 3),
    teacher_id UUID REFERENCES users(id) ON DELETE SET NULL,
    teacher_email VARCHAR(255) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 자율학습 그룹 관리 테이블 (분임토의실 등)
CREATE TABLE IF NOT EXISTS study_groups (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    group_name VARCHAR(100) NOT NULL,
    group_type VARCHAR(50) DEFAULT 'study', -- study, discussion, project
    creator_id UUID REFERENCES users(id) ON DELETE SET NULL,
    creator_email VARCHAR(255) NOT NULL,
    student_emails TEXT[] DEFAULT '{}', -- 참여 학생 이메일 배열
    room_location VARCHAR(100), -- 활동 장소
    is_active BOOLEAN DEFAULT true,
    is_deleted BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 인덱스 생성 (성능 최적화)
CREATE INDEX IF NOT EXISTS idx_seat_arrangements_classroom ON seat_arrangements(classroom);
CREATE INDEX IF NOT EXISTS idx_seat_arrangements_date ON seat_arrangements(arrangement_date);
CREATE INDEX IF NOT EXISTS idx_seat_arrangements_position ON seat_arrangements(position_key);

CREATE INDEX IF NOT EXISTS idx_attendance_records_date_period ON attendance_records(attendance_date, period);
CREATE INDEX IF NOT EXISTS idx_attendance_records_student_email ON attendance_records(student_email);
CREATE INDEX IF NOT EXISTS idx_attendance_records_student_id ON attendance_records(student_id);
CREATE INDEX IF NOT EXISTS idx_attendance_records_status ON attendance_records(status);

CREATE INDEX IF NOT EXISTS idx_period_configs_date ON period_configs(config_date);
CREATE INDEX IF NOT EXISTS idx_classroom_layouts_key ON classroom_layouts(classroom_key);

CREATE INDEX IF NOT EXISTS idx_supervisor_schedules_date ON supervisor_schedules(schedule_date);
CREATE INDEX IF NOT EXISTS idx_supervisor_schedules_grade ON supervisor_schedules(grade);
CREATE INDEX IF NOT EXISTS idx_supervisor_schedules_teacher_email ON supervisor_schedules(teacher_email);

CREATE INDEX IF NOT EXISTS idx_study_groups_creator_email ON study_groups(creator_email);
CREATE INDEX IF NOT EXISTS idx_study_groups_active ON study_groups(is_active, is_deleted);

-- 업데이트 트리거 추가
CREATE TRIGGER update_seat_arrangements_updated_at 
    BEFORE UPDATE ON seat_arrangements 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_attendance_records_updated_at 
    BEFORE UPDATE ON attendance_records 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_period_configs_updated_at 
    BEFORE UPDATE ON period_configs 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_classroom_layouts_updated_at 
    BEFORE UPDATE ON classroom_layouts 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_supervisor_schedules_updated_at 
    BEFORE UPDATE ON supervisor_schedules 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_study_groups_updated_at 
    BEFORE UPDATE ON study_groups 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- 초기 데이터 삽입

-- 기본 교시 설정 (오늘 날짜)
INSERT INTO period_configs (config_date, is_holiday, regular_periods, study_periods, meal_periods, special_periods, period_info) 
VALUES (
    CURRENT_DATE, 
    false, 
    ARRAY[1,2,3,4,5,6,7], 
    ARRAY[11,12,13,14,15], 
    ARRAY[22,23], 
    ARRAY[21,25],
    '{
        "1": {"name": "1교시", "start_time": "08:30", "end_time": "09:20"},
        "2": {"name": "2교시", "start_time": "09:30", "end_time": "10:20"},
        "3": {"name": "3교시", "start_time": "10:30", "end_time": "11:20"},
        "4": {"name": "4교시", "start_time": "11:30", "end_time": "12:20"},
        "5": {"name": "5교시", "start_time": "13:10", "end_time": "14:00"},
        "6": {"name": "6교시", "start_time": "14:10", "end_time": "15:00"},
        "7": {"name": "7교시", "start_time": "15:10", "end_time": "16:00"},
        "11": {"name": "1차자습", "start_time": "19:00", "end_time": "20:50"},
        "12": {"name": "2차자습", "start_time": "21:00", "end_time": "22:50"},
        "13": {"name": "3차자습", "start_time": "07:00", "end_time": "08:20"},
        "14": {"name": "4차자습", "start_time": "16:10", "end_time": "17:00"},
        "15": {"name": "5차자습", "start_time": "17:10", "end_time": "18:00"},
        "21": {"name": "조식", "start_time": "06:30", "end_time": "07:30"},
        "22": {"name": "중식", "start_time": "12:20", "end_time": "13:10"},
        "23": {"name": "석식", "start_time": "18:00", "end_time": "19:00"},
        "25": {"name": "외박", "start_time": "22:50", "end_time": "07:00"}
    }'::jsonb
) ON CONFLICT (config_date) DO NOTHING;

-- 교실 레이아웃 초기 데이터
INSERT INTO classroom_layouts (classroom_key, classroom_name, layout_config, bottom_left_info) VALUES 
(
    'grade_1',
    '1학년',
    '{
        "sections": [
            {"name": "3학년", "type": "break", "cols": [{"col": "B"}]},
            {"name": "3-J", "type": "single", "cols": [{"col": "R", "line": "L"}]},
            {"name": "3-I", "type": "double", "cols": [{"col": "L", "line": "R"}, {"col": "R", "line": "L"}]},
            {"name": "3-H", "type": "single", "cols": [{"col": "N", "line": "R"}]},
            {"name": "3-G", "type": "break", "cols": [{"col": "B"}]},
            {"name": "3-F", "type": "single", "cols": [{"col": "N", "line": "L"}], "stick": true},
            {"name": "3-E", "type": "double", "cols": [{"col": "L", "line": "R"}, {"col": "R", "line": "L"}]},
            {"name": "3-D", "type": "double", "cols": [{"col": "L", "line": "R"}, {"col": "R", "line": "L"}]},
            {"name": "3-C", "type": "double", "cols": [{"col": "L", "line": "R"}, {"col": "R", "line": "L"}]},
            {"name": "3-B", "type": "double", "cols": [{"col": "L", "line": "R"}, {"col": "R", "line": "L"}]},
            {"name": "3-A", "type": "single", "cols": [{"col": "N", "line": "R"}]}
        ]
    }'::jsonb,
    '남쪽 출입구'
),
(
    'grade_2',
    '2학년',
    '{
        "sections": [
            {"name": "2-A", "type": "single", "cols": [{"col": "N", "line": "L"}]},
            {"name": "2-B", "type": "double", "cols": [{"col": "L", "line": "R"}, {"col": "R", "line": "L"}]},
            {"name": "2-C", "type": "double", "cols": [{"col": "L", "line": "R"}, {"col": "R", "line": "L"}]},
            {"name": "2-D", "type": "single", "cols": [{"col": "N", "line": "R"}]},
            {"name": "라운지", "type": "break", "cols": [{"col": "B"}]},
            {"name": "2-E", "type": "single", "cols": [{"col": "N", "line": "L"}]},
            {"name": "2-F", "type": "double", "cols": [{"col": "L", "line": "R"}, {"col": "R", "line": "L"}]},
            {"name": "2-G", "type": "double", "cols": [{"col": "L", "line": "R"}, {"col": "R", "line": "L"}]},
            {"name": "2-H", "type": "double", "cols": [{"col": "L", "line": "R"}, {"col": "R", "line": "L"}]},
            {"name": "2-I", "type": "single", "cols": [{"col": "L", "line": "R"}]},
            {"name": "3학년", "type": "break", "cols": [{"col": "B"}], "stick": true}
        ]
    }'::jsonb,
    '서쪽 출입구 (화장실)'
),
(
    'grade_3',
    '3학년',
    '{
        "sections": [
            {"name": "3-M", "type": "single", "cols": [{"col": "N", "line": "L"}]},
            {"name": "3-L", "type": "double", "cols": [{"col": "L", "line": "R"}, {"col": "R", "line": "L"}]},
            {"name": "3-K", "type": "double", "cols": [{"col": "L", "line": "R"}, {"col": "R", "line": "L"}]},
            {"name": "3-J", "type": "single", "cols": [{"col": "L", "line": "R"}]},
            {"name": "1학년", "type": "break", "cols": [{"col": "B"}], "stick": true}
        ]
    }'::jsonb,
    '동쪽 출입구'
) 
ON CONFLICT (classroom_key) DO NOTHING;

-- 자리배치 샘플 데이터 (실제 사용 가능한 테스트 데이터)
INSERT INTO seat_arrangements (classroom, position_key, student_emails, arrangement_date) VALUES
-- 1학년 자리배치
('grade_1', '3-A-N', ARRAY['student1@school.com'], CURRENT_DATE),
('grade_1', '3-B-L', ARRAY['student2@school.com'], CURRENT_DATE),
('grade_1', '3-B-R', ARRAY['student3@school.com'], CURRENT_DATE),
('grade_1', '3-C-L', ARRAY['student4@school.com'], CURRENT_DATE),
('grade_1', '3-C-R', ARRAY['student5@school.com'], CURRENT_DATE),
('grade_1', '3-D-L', ARRAY[]::TEXT[], CURRENT_DATE), -- 빈 자리
('grade_1', '3-D-R', ARRAY[]::TEXT[], CURRENT_DATE), -- 빈 자리
('grade_1', '3-E-L', ARRAY[]::TEXT[], CURRENT_DATE), -- 빈 자리
('grade_1', '3-E-R', ARRAY[]::TEXT[], CURRENT_DATE), -- 빈 자리
('grade_1', '3-F-N', ARRAY[]::TEXT[], CURRENT_DATE), -- 빈 자리
('grade_1', '3-H-N', ARRAY[]::TEXT[], CURRENT_DATE), -- 빈 자리
('grade_1', '3-I-L', ARRAY[]::TEXT[], CURRENT_DATE), -- 빈 자리
('grade_1', '3-I-R', ARRAY[]::TEXT[], CURRENT_DATE), -- 빈 자리
('grade_1', '3-J-R', ARRAY[]::TEXT[], CURRENT_DATE), -- 빈 자리

-- 2학년 자리배치  
('grade_2', '2-A-N', ARRAY['student6@school.com'], CURRENT_DATE),
('grade_2', '2-B-L', ARRAY['student7@school.com'], CURRENT_DATE),
('grade_2', '2-B-R', ARRAY['student8@school.com'], CURRENT_DATE),
('grade_2', '2-C-L', ARRAY[]::TEXT[], CURRENT_DATE), -- 빈 자리
('grade_2', '2-C-R', ARRAY[]::TEXT[], CURRENT_DATE), -- 빈 자리
('grade_2', '2-D-N', ARRAY[]::TEXT[], CURRENT_DATE), -- 빈 자리
('grade_2', '2-E-N', ARRAY[]::TEXT[], CURRENT_DATE), -- 빈 자리
('grade_2', '2-F-L', ARRAY[]::TEXT[], CURRENT_DATE), -- 빈 자리
('grade_2', '2-F-R', ARRAY[]::TEXT[], CURRENT_DATE), -- 빈 자리
('grade_2', '2-G-L', ARRAY[]::TEXT[], CURRENT_DATE), -- 빈 자리
('grade_2', '2-G-R', ARRAY[]::TEXT[], CURRENT_DATE), -- 빈 자리
('grade_2', '2-H-L', ARRAY[]::TEXT[], CURRENT_DATE), -- 빈 자리
('grade_2', '2-H-R', ARRAY[]::TEXT[], CURRENT_DATE), -- 빈 자리
('grade_2', '2-I-L', ARRAY[]::TEXT[], CURRENT_DATE), -- 빈 자리

-- 3학년 자리배치
('grade_3', '3-M-N', ARRAY['student9@school.com'], CURRENT_DATE),
('grade_3', '3-L-L', ARRAY['student10@school.com'], CURRENT_DATE),
('grade_3', '3-L-R', ARRAY[]::TEXT[], CURRENT_DATE), -- 빈 자리
('grade_3', '3-K-L', ARRAY[]::TEXT[], CURRENT_DATE), -- 빈 자리
('grade_3', '3-K-R', ARRAY[]::TEXT[], CURRENT_DATE), -- 빈 자리
('grade_3', '3-J-L', ARRAY[]::TEXT[], CURRENT_DATE)  -- 빈 자리

ON CONFLICT (classroom, position_key, arrangement_date) DO NOTHING;

-- 오늘 출석 샘플 데이터 (자습시간 11교시)
INSERT INTO attendance_records (attendance_date, period, student_id, student_email, status, notes) VALUES
(CURRENT_DATE, 11, (SELECT id FROM users WHERE email = 'student1@school.com'), 'student1@school.com', 'present', '정상 출석'),
(CURRENT_DATE, 11, (SELECT id FROM users WHERE email = 'student2@school.com'), 'student2@school.com', 'present', '정상 출석'),
(CURRENT_DATE, 11, (SELECT id FROM users WHERE email = 'student3@school.com'), 'student3@school.com', 'absent', '화장실'),
(CURRENT_DATE, 11, (SELECT id FROM users WHERE email = 'student4@school.com'), 'student4@school.com', 'activity', '분임토의실'),
(CURRENT_DATE, 11, (SELECT id FROM users WHERE email = 'student5@school.com'), 'student5@school.com', 'present', '정상 출석'),
(CURRENT_DATE, 11, (SELECT id FROM users WHERE email = 'student6@school.com'), 'student6@school.com', 'present', '정상 출석'),
(CURRENT_DATE, 11, (SELECT id FROM users WHERE email = 'student7@school.com'), 'student7@school.com', 'present', '정상 출석'),
(CURRENT_DATE, 11, (SELECT id FROM users WHERE email = 'student8@school.com'), 'student8@school.com', 'absent', '의무실'),
(CURRENT_DATE, 11, (SELECT id FROM users WHERE email = 'student9@school.com'), 'student9@school.com', 'present', '정상 출석'),
(CURRENT_DATE, 11, (SELECT id FROM users WHERE email = 'student10@school.com'), 'student10@school.com', 'present', '정상 출석')
ON CONFLICT (attendance_date, period, student_id) DO NOTHING;