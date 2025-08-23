import os
from datetime import datetime
from typing import Optional, Dict, Any, List
import requests
import json

class SupabaseService:
    """Supabase 데이터베이스 서비스"""
    
    def __init__(self):
        self.url = os.getenv('SUPABASE_URL', 'https://your-project.supabase.co')
        self.anon_key = os.getenv('SUPABASE_KEY', 'your-anon-key')
        self.service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY', 'your-service-role-key')
        
        self.headers = {
            'apikey': self.anon_key,
            'Authorization': f'Bearer {self.anon_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
        
        self.service_headers = {
            'apikey': self.service_role_key,
            'Authorization': f'Bearer {self.service_role_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None, use_service_role: bool = False) -> Dict:
        """Supabase API 요청"""
        headers = self.service_headers if use_service_role else self.headers
        url = f"{self.url}/rest/v1/{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=data)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method == 'PATCH':
                response = requests.patch(url, headers=headers, json=data)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)
            
            response.raise_for_status()
            return response.json() if response.content else {}
            
        except requests.exceptions.RequestException as e:
            print(f"Supabase API 오류 - URL: {url}")
            print(f"Method: {method}, Data: {data}")
            print(f"Error: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response Status: {e.response.status_code}")
                print(f"Response Body: {e.response.text}")
            return {}
    
    # 사용자 관리
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """이메일로 사용자 조회"""
        endpoint = f"users?email=eq.{email}&select=*"
        result = self._make_request('GET', endpoint)
        return result[0] if result else None
    
    def create_user(self, user_data: Dict) -> Optional[Dict]:
        """사용자 생성"""
        endpoint = "users"
        return self._make_request('POST', endpoint, user_data, use_service_role=True)
    
    def update_user(self, user_id: str, user_data: Dict) -> Optional[Dict]:
        """사용자 정보 업데이트"""
        endpoint = f"users?id=eq.{user_id}"
        return self._make_request('PATCH', endpoint, user_data, use_service_role=True)
    
    def delete_user(self, user_id: str) -> bool:
        """사용자 삭제"""
        endpoint = f"users?id=eq.{user_id}"
        result = self._make_request('DELETE', endpoint, use_service_role=True)
        return result is not None
    
    def get_all_users(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """전체 사용자 목록 조회"""
        endpoint = f"users?select=*&limit={limit}&offset={offset}&order=created_at.desc"
        return self._make_request('GET', endpoint, use_service_role=True)
    
    # 학생 프로필 관리
    def get_student_profile(self, user_id: str) -> Optional[Dict]:
        """학생 프로필 조회"""
        endpoint = f"student_profiles?user_id=eq.{user_id}&select=*"
        result = self._make_request('GET', endpoint)
        return result[0] if result else None
    
    def create_student_profile(self, profile_data: Dict) -> Optional[Dict]:
        """학생 프로필 생성"""
        endpoint = "student_profiles"
        return self._make_request('POST', endpoint, profile_data, use_service_role=True)
    
    def update_student_profile(self, user_id: str, profile_data: Dict) -> Optional[Dict]:
        """학생 프로필 업데이트"""
        endpoint = f"student_profiles?user_id=eq.{user_id}"
        return self._make_request('PATCH', endpoint, profile_data, use_service_role=True)
    
    # 교사 프로필 관리
    def get_teacher_profile(self, user_id: str) -> Optional[Dict]:
        """교사 프로필 조회"""
        endpoint = f"teacher_profiles?user_id=eq.{user_id}&select=*"
        result = self._make_request('GET', endpoint)
        return result[0] if result else None
    
    def create_teacher_profile(self, profile_data: Dict) -> Optional[Dict]:
        """교사 프로필 생성"""
        endpoint = "teacher_profiles"
        return self._make_request('POST', endpoint, profile_data, use_service_role=True)
    
    def update_teacher_profile(self, user_id: str, profile_data: Dict) -> Optional[Dict]:
        """교사 프로필 업데이트"""
        endpoint = f"teacher_profiles?user_id=eq.{user_id}"
        return self._make_request('PATCH', endpoint, profile_data, use_service_role=True)
    
    # 통합 사용자 정보 조회
    def get_user_with_profile(self, email: str) -> Optional[Dict]:
        """이메일로 사용자 정보와 프로필을 함께 조회"""
        user = self.get_user_by_email(email)
        if not user:
            return None
        
        profile = None
        if user['role'] == 'student':
            profile = self.get_student_profile(user['id'])
        elif user['role'] == 'teacher':
            profile = self.get_teacher_profile(user['id'])
        
        user['profile'] = profile
        return user
    
    def update_last_login(self, user_id: str):
        """마지막 로그인 시간 업데이트"""
        data = {'last_login': datetime.utcnow().isoformat()}
        return self.update_user(user_id, data)
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """ID로 사용자 조회"""
        endpoint = f"users?id=eq.{user_id}&select=*"
        result = self._make_request('GET', endpoint, use_service_role=True)
        return result[0] if result else None
    
    def search_users(self, query: str) -> List[Dict]:
        """사용자 검색 (이름, 이메일로 검색)"""
        # Supabase의 ilike 연산자를 사용하여 대소문자 구분 없이 검색
        endpoint = f"users?or=(name.ilike.*{query}*,email.ilike.*{query}*)&select=*&limit=20&order=name"
        return self._make_request('GET', endpoint, use_service_role=True)
    
    # 학교 관리
    def get_schools(self) -> List[Dict]:
        """학교 목록 조회"""
        endpoint = "schools?select=*&order=created_at.desc"
        return self._make_request('GET', endpoint, use_service_role=True)
    
    def create_school(self, school_data: Dict) -> Optional[Dict]:
        """학교 생성"""
        endpoint = "schools"
        return self._make_request('POST', endpoint, school_data, use_service_role=True)
    
    def update_school(self, school_id: str, school_data: Dict) -> Optional[Dict]:
        """학교 정보 업데이트"""
        endpoint = f"schools?id=eq.{school_id}"
        return self._make_request('PATCH', endpoint, school_data, use_service_role=True)
    
    def delete_school(self, school_id: str) -> bool:
        """학교 삭제"""
        endpoint = f"schools?id=eq.{school_id}"
        result = self._make_request('DELETE', endpoint, use_service_role=True)
        return result is not None
    
    # 학급 관리
    def get_all_classes(self) -> List[Dict]:
        """전체 학급 목록 조회"""
        endpoint = "classes?select=*,schools(name)&order=grade,class_number"
        return self._make_request('GET', endpoint, use_service_role=True)
    
    def get_classes_by_teacher(self, teacher_email: str) -> List[Dict]:
        """특정 교사의 담당 학급 조회"""
        endpoint = f"classes?teacher_email=eq.{teacher_email}&select=*,schools(name)&order=grade,class_number"
        return self._make_request('GET', endpoint, use_service_role=True)
    
    def get_classes_by_school(self, school_id: str) -> List[Dict]:
        """특정 학교의 학급 목록 조회"""
        endpoint = f"classes?school_id=eq.{school_id}&select=*&order=grade,class_number"
        return self._make_request('GET', endpoint, use_service_role=True)
    
    def create_class(self, class_data: Dict) -> Optional[Dict]:
        """학급 생성"""
        endpoint = "classes"
        return self._make_request('POST', endpoint, class_data, use_service_role=True)
    
    def update_class(self, class_id: str, class_data: Dict) -> Optional[Dict]:
        """학급 정보 업데이트"""
        endpoint = f"classes?id=eq.{class_id}"
        return self._make_request('PATCH', endpoint, class_data, use_service_role=True)
    
    def delete_class(self, class_id: str) -> bool:
        """학급 삭제"""
        endpoint = f"classes?id=eq.{class_id}"
        result = self._make_request('DELETE', endpoint, use_service_role=True)
        return result is not None
    
    # 학생-학급 연결 관리
    def get_student_classes(self, student_email: str) -> List[Dict]:
        """학생이 속한 학급 목록 조회"""
        endpoint = f"student_classes?student_email=eq.{student_email}&select=*,classes(*,schools(name))&is_active=eq.true"
        return self._make_request('GET', endpoint, use_service_role=True)
    
    def get_class_students(self, class_id: str) -> List[Dict]:
        """특정 학급의 학생 목록 조회"""
        endpoint = f"student_classes?class_id=eq.{class_id}&select=student_email,users(name,email)&is_active=eq.true"
        return self._make_request('GET', endpoint, use_service_role=True)
    
    def enroll_student_to_class(self, student_email: str, class_id: str) -> Optional[Dict]:
        """학생을 학급에 등록"""
        data = {
            'student_email': student_email,
            'class_id': class_id,
            'is_active': True
        }
        endpoint = "student_classes"
        return self._make_request('POST', endpoint, data, use_service_role=True)
    
    def remove_student_from_class(self, student_email: str, class_id: str) -> bool:
        """학생을 학급에서 제거"""
        endpoint = f"student_classes?student_email=eq.{student_email}&class_id=eq.{class_id}"
        result = self._make_request('DELETE', endpoint, use_service_role=True)
        return result is not None
    
    # 출석 관리
    def get_student_attendance(self, student_email: str, start_date: str = None, end_date: str = None) -> List[Dict]:
        """특정 학생의 출석 기록 조회"""
        endpoint = f"attendance?student_email=eq.{student_email}&select=*,classes(class_name,schools(name))&order=attendance_date.desc,period"
        
        if start_date and end_date:
            endpoint += f"&attendance_date=gte.{start_date}&attendance_date=lte.{end_date}"
        
        return self._make_request('GET', endpoint, use_service_role=True)
    
    def get_attendance_records(self, class_id: str = None, date: str = None) -> List[Dict]:
        """출석 기록 조회 (학급별, 날짜별)"""
        endpoint = "attendance?select=*,classes(class_name,schools(name))&order=attendance_date.desc,period"
        
        if class_id:
            endpoint += f"&class_id=eq.{class_id}"
        if date:
            endpoint += f"&attendance_date=eq.{date}"
        
        return self._make_request('GET', endpoint, use_service_role=True)
    
    def mark_attendance(self, attendance_data: Dict) -> Optional[Dict]:
        """출석 체크"""
        endpoint = "attendance"
        return self._make_request('POST', endpoint, attendance_data, use_service_role=True)
    
    def update_attendance(self, attendance_id: str, attendance_data: Dict) -> Optional[Dict]:
        """출석 기록 수정"""
        endpoint = f"attendance?id=eq.{attendance_id}"
        return self._make_request('PATCH', endpoint, attendance_data, use_service_role=True)
    
    def delete_attendance(self, attendance_id: str) -> bool:
        """출석 기록 삭제"""
        endpoint = f"attendance?id=eq.{attendance_id}"
        result = self._make_request('DELETE', endpoint, use_service_role=True)
        return result is not None
    
    # =============================================================================
    # 자리배치표 관리 메소드 (Seating Management)
    # =============================================================================
    
    def get_seat_arrangements(self, classroom: str, arrangement_date: str) -> List[Dict]:
        """자리배치 조회"""
        endpoint = f"seat_arrangements?classroom=eq.{classroom}&arrangement_date=eq.{arrangement_date}&is_active=eq.true&select=*&order=position_key"
        return self._make_request('GET', endpoint, use_service_role=True)
    
    def get_seat_data_with_students(self, classroom: str, arrangement_date: str) -> Dict:
        """학생 정보와 함께 자리배치 데이터 조회"""
        # 자리배치 조회
        arrangements = self.get_seat_arrangements(classroom, arrangement_date)
        
        # 모든 학생 이메일 수집
        all_student_emails = []
        for arrangement in arrangements:
            if arrangement.get('student_emails'):
                all_student_emails.extend(arrangement['student_emails'])
        
        seat_data = {}
        student_map = {}
        
        if all_student_emails:
            # 학생 정보 조회 
            students_endpoint = f"users?email=in.({','.join(all_student_emails)})&role=eq.student&select=id,email,name,student_profiles(student_id,grade,class_number)"
            students = self._make_request('GET', students_endpoint, use_service_role=True)
            
            # 학생 정보를 이메일로 매핑
            for student in students:
                profile = student.get('student_profiles', [{}])[0] if student.get('student_profiles') else {}
                student_map[student['email']] = {
                    'id': student['id'],
                    'email': student['email'],
                    'name': student['name'],
                    'number': profile.get('student_id', ''),
                    'grade': profile.get('grade'),
                    'class_number': profile.get('class_number')
                }
        
        # 자리배치 데이터에 학생 정보 추가
        for arrangement in arrangements:
            position_key = arrangement['position_key']
            student_emails = arrangement.get('student_emails', [])
            
            seat_data[position_key] = []
            for email in student_emails:
                if email in student_map:
                    seat_data[position_key].append(student_map[email])
                else:
                    seat_data[position_key].append({'email': email, 'name': '알 수 없음'})
        
        return seat_data
    
    def save_seat_arrangements(self, classroom: str, arrangement_date: str, 
                             arrangements: Dict[str, List[str]], created_by_email: str) -> Dict:
        """자리배치 저장"""
        try:
            # 생성자 ID 조회
            user = self.get_user_by_email(created_by_email)
            if not user:
                return {'success': False, 'error': '사용자를 찾을 수 없습니다.'}
            
            created_by_id = user['id']
            
            # 기존 배치 비활성화
            endpoint = f"seat_arrangements?classroom=eq.{classroom}&arrangement_date=eq.{arrangement_date}"
            deactivate_data = {'is_active': False}
            self._make_request('PATCH', endpoint, deactivate_data, use_service_role=True)
            
            # 새 배치 저장
            insert_data = []
            for position_key, student_emails in arrangements.items():
                if student_emails:  # 빈 자리가 아닌 경우에만 저장
                    insert_data.append({
                        'classroom': classroom,
                        'position_key': position_key,
                        'student_emails': student_emails,
                        'arrangement_date': arrangement_date,
                        'created_by': created_by_id,
                        'is_active': True
                    })
            
            if insert_data:
                endpoint = "seat_arrangements"
                result = self._make_request('POST', endpoint, insert_data, use_service_role=True)
                return {'success': True, 'saved_positions': len(insert_data)}
            
            return {'success': True, 'saved_positions': 0}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_classroom_layout(self, classroom_key: str) -> Optional[Dict]:
        """교실 레이아웃 조회"""
        endpoint = f"classroom_layouts?classroom_key=eq.{classroom_key}&is_active=eq.true&select=*"
        result = self._make_request('GET', endpoint, use_service_role=True)
        return result[0] if result else None
    
    def get_classroom_layouts(self) -> List[Dict]:
        """모든 교실 레이아웃 조회"""
        endpoint = "classroom_layouts?is_active=eq.true&select=*&order=classroom_key"
        return self._make_request('GET', endpoint, use_service_role=True)
    
    def get_period_config(self, config_date: str) -> Optional[Dict]:
        """교시 설정 조회"""
        endpoint = f"period_configs?config_date=eq.{config_date}&select=*"
        result = self._make_request('GET', endpoint, use_service_role=True)
        return result[0] if result else None
    
    def get_attendance_records_by_period(self, attendance_date: str, period: int, classroom: str = None) -> List[Dict]:
        """교시별 출석 기록 조회"""
        endpoint = f"attendance_records?attendance_date=eq.{attendance_date}&period=eq.{period}&select=*,users(name,student_profiles(student_id,grade,class_number))&order=student_email"
        return self._make_request('GET', endpoint, use_service_role=True)
    
    def get_activity_records(self, activity_date: str, period: int) -> List[Dict]:
        """활동 기록 조회 (분임토의실 등)"""
        endpoint = f"attendance_records?attendance_date=eq.{activity_date}&period=eq.{period}&status=eq.activity&select=*,users(name,student_profiles(student_id))&order=student_email"
        return self._make_request('GET', endpoint, use_service_role=True)
    
    def mark_attendance_bulk(self, attendance_date: str, period: int, student_emails: List[str], 
                           status: str, marked_by_email: str, notes: str = '') -> Dict:
        """일괄 출석 처리"""
        try:
            # 처리자 정보 조회
            marker = self.get_user_by_email(marked_by_email)
            if not marker:
                return {'success': False, 'error': '처리자를 찾을 수 없습니다.'}
            
            marked_by_id = marker['id']
            current_time = datetime.utcnow().isoformat()
            processed_count = 0
            
            for email in student_emails:
                # 학생 정보 조회
                student = self.get_user_by_email(email)
                if not student or student['role'] != 'student':
                    continue
                
                student_id = student['id']
                
                # 기존 기록 확인
                existing_endpoint = f"attendance_records?attendance_date=eq.{attendance_date}&period=eq.{period}&student_id=eq.{student_id}&select=id,status"
                existing_records = self._make_request('GET', existing_endpoint, use_service_role=True)
                
                if existing_records:
                    # 기존 기록 업데이트
                    existing_id = existing_records[0]['id']
                    update_data = {
                        'status': status,
                        'notes': notes,
                        'updated_at': current_time
                    }
                    
                    if status == 'absent':
                        update_data.update({
                            'marked_by': marked_by_id,
                            'marked_at': current_time
                        })
                    elif status in ['returned', 'present']:
                        update_data.update({
                            'returned_by': marked_by_id,
                            'returned_at': current_time
                        })
                    
                    update_endpoint = f"attendance_records?id=eq.{existing_id}"
                    self._make_request('PATCH', update_endpoint, update_data, use_service_role=True)
                else:
                    # 새 기록 생성
                    insert_data = {
                        'attendance_date': attendance_date,
                        'period': period,
                        'student_id': student_id,
                        'student_email': email,
                        'status': status,
                        'notes': notes
                    }
                    
                    if status == 'absent':
                        insert_data.update({
                            'marked_by': marked_by_id,
                            'marked_at': current_time
                        })
                    elif status in ['returned', 'present']:
                        insert_data.update({
                            'returned_by': marked_by_id,
                            'returned_at': current_time
                        })
                    
                    endpoint = "attendance_records"
                    self._make_request('POST', endpoint, insert_data, use_service_role=True)
                
                processed_count += 1
            
            return {'success': True, 'processed_count': processed_count}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_supervisor_schedules(self, schedule_date: str) -> List[Dict]:
        """감독교사 스케줄 조회"""
        endpoint = f"supervisor_schedules?schedule_date=eq.{schedule_date}&select=*,users(name,teacher_profiles(position,subject))&order=grade,start_time"
        return self._make_request('GET', endpoint, use_service_role=True)
    
    def get_all_students(self) -> List[Dict]:
        """모든 학생 목록 조회"""
        endpoint = "users?role=eq.student&select=id,email,name,is_active,student_profiles(student_id,grade,class_number,department)&order=name"
        return self._make_request('GET', endpoint, use_service_role=True)
    
    def get_study_groups(self, creator_email: str = None) -> List[Dict]:
        """자율학습 그룹 조회"""
        endpoint = "study_groups?is_active=eq.true&is_deleted=eq.false&select=*&order=created_at.desc"
        if creator_email:
            endpoint += f"&creator_email=eq.{creator_email}"
        return self._make_request('GET', endpoint, use_service_role=True)
    
    def create_study_group(self, group_data: Dict) -> Optional[Dict]:
        """자율학습 그룹 생성"""
        endpoint = "study_groups"
        return self._make_request('POST', endpoint, group_data, use_service_role=True)
    
    def update_study_group(self, group_id: str, group_data: Dict) -> Optional[Dict]:
        """자율학습 그룹 업데이트"""
        endpoint = f"study_groups?id=eq.{group_id}"
        return self._make_request('PATCH', endpoint, group_data, use_service_role=True)
    
    def delete_study_group(self, group_id: str) -> bool:
        """자율학습 그룹 삭제 (소프트 삭제)"""
        endpoint = f"study_groups?id=eq.{group_id}"
        delete_data = {'is_deleted': True}
        result = self._make_request('PATCH', endpoint, delete_data, use_service_role=True)
        return result is not None

# 전역 서비스 인스턴스
supabase_service = SupabaseService()