"""
자리배치표 관리 서비스
Seating Management Service
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, date
import json

from .supabase_service import SupabaseService

logger = logging.getLogger(__name__)

class SeatingService:
    """자리배치표 관리 서비스 클래스"""
    
    def __init__(self):
        self.supabase = SupabaseService()
    
    def get_seat_arrangements(self, classroom: str, arrangement_date: str) -> Dict[str, Any]:
        """특정 교실과 날짜의 자리배치 정보 조회"""
        try:
            response = self.supabase.client.table('seat_arrangements') \
                .select('*') \
                .eq('classroom', classroom) \
                .eq('arrangement_date', arrangement_date) \
                .eq('is_active', True) \
                .execute()
            
            arrangements = {}
            for row in response.data:
                arrangements[row['position_key']] = row['student_emails']
            
            return {
                'success': True,
                'arrangements': arrangements
            }
            
        except Exception as e:
            logger.error(f"자리배치 조회 에러: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_seat_data_with_students(self, classroom: str, arrangement_date: str) -> Dict[str, Any]:
        """학생 정보와 함께 자리배치 데이터 조회"""
        try:
            # 자리배치 정보 조회
            arrangement_result = self.get_seat_arrangements(classroom, arrangement_date)
            if not arrangement_result['success']:
                return arrangement_result
            
            arrangements = arrangement_result['arrangements']
            
            # 해당 교실의 모든 학생 이메일 수집
            all_student_emails = []
            for emails in arrangements.values():
                all_student_emails.extend(emails)
            
            # 학생 정보 조회
            if all_student_emails:
                student_response = self.supabase.client.table('users') \
                    .select('id, email, name, role, student_profiles(student_id, grade, class_number)') \
                    .in_('email', all_student_emails) \
                    .eq('role', 'student') \
                    .execute()
                
                # 학생 정보를 이메일로 매핑
                student_map = {}
                for student in student_response.data:
                    student_map[student['email']] = {
                        'id': student['id'],
                        'email': student['email'],
                        'name': student['name'],
                        'number': student['student_profiles'][0]['student_id'] if student['student_profiles'] else '',
                        'grade': student['student_profiles'][0]['grade'] if student['student_profiles'] else None,
                        'class_number': student['student_profiles'][0]['class_number'] if student['student_profiles'] else None
                    }
            else:
                student_map = {}
            
            # 자리배치 데이터에 학생 정보 추가
            seat_data = {}
            for position_key, student_emails in arrangements.items():
                seat_data[position_key] = []
                for email in student_emails:
                    if email in student_map:
                        seat_data[position_key].append(student_map[email])
                    else:
                        # 학생 정보가 없는 경우 이메일만 저장
                        seat_data[position_key].append({'email': email, 'name': '알 수 없음'})
            
            return {
                'success': True,
                'seat_data': seat_data,
                'student_count': len(all_student_emails)
            }
            
        except Exception as e:
            logger.error(f"학생 정보 포함 자리배치 조회 에러: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def save_seat_arrangements(self, classroom: str, arrangement_date: str, 
                             arrangements: Dict[str, List[str]], created_by_email: str) -> Dict[str, Any]:
        """자리배치 정보 저장"""
        try:
            # 생성자 ID 조회
            user_response = self.supabase.client.table('users') \
                .select('id') \
                .eq('email', created_by_email) \
                .single() \
                .execute()
            
            created_by_id = user_response.data['id']
            
            # 기존 배치 비활성화
            self.supabase.client.table('seat_arrangements') \
                .update({'is_active': False}) \
                .eq('classroom', classroom) \
                .eq('arrangement_date', arrangement_date) \
                .execute()
            
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
                self.supabase.client.table('seat_arrangements') \
                    .insert(insert_data) \
                    .execute()
            
            return {
                'success': True,
                'saved_positions': len(insert_data)
            }
            
        except Exception as e:
            logger.error(f"자리배치 저장 에러: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_classroom_layout(self, classroom_key: str) -> Dict[str, Any]:
        """교실 레이아웃 조회"""
        try:
            response = self.supabase.client.table('classroom_layouts') \
                .select('*') \
                .eq('classroom_key', classroom_key) \
                .eq('is_active', True) \
                .single() \
                .execute()
            
            return {
                'success': True,
                'layout': response.data
            }
            
        except Exception as e:
            logger.error(f"교실 레이아웃 조회 에러: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_classroom_layouts(self) -> Dict[str, Any]:
        """모든 교실 레이아웃 조회"""
        try:
            response = self.supabase.client.table('classroom_layouts') \
                .select('*') \
                .eq('is_active', True) \
                .order('classroom_key') \
                .execute()
            
            return {
                'success': True,
                'layouts': response.data
            }
            
        except Exception as e:
            logger.error(f"교실 레이아웃 목록 조회 에러: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }