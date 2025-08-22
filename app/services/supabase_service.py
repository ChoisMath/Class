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
            print(f"Supabase API 오류: {str(e)}")
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

# 전역 서비스 인스턴스
supabase_service = SupabaseService()