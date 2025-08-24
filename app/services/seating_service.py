"""
자리배치표 관리 서비스 (DSHS-Life 스타일)
DSHS-Life Style Seating Management Service
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, date, time
import json

from .supabase_service import SupabaseService

logger = logging.getLogger(__name__)

class SeatingService:
    """DSHS-Life 스타일 자리배치표 관리 서비스 클래스"""
    
    def __init__(self):
        self.supabase = SupabaseService()
    
    def get_seat_arrangement_with_status(self, target_date: date, period: int, classroom: str) -> Dict[str, Any]:
        """
        날짜/교시별 좌석 배치 및 출석 상태 조회 (DSHS-Life 방식)
        
        Args:
            target_date: 조회 날짜
            period: 교시 (1-7: 일반교시, 11-15: 자습시간)
            classroom: 교실 키 (grade_1, grade_2, grade_3)
            
        Returns:
            좌석 배치 및 출석 상태 정보
        """
        try:
            # 1. 교실 레이아웃 조회
            layout_result = self.get_classroom_layout(classroom)
            if not layout_result['success']:
                return {'error': 'Classroom layout not found'}
                
            layout = layout_result['layout']

            # 2. 좌석 배치 조회
            seat_response = self.supabase.client.table('seat_arrangements').select('*').eq('classroom', classroom).eq('arrangement_date', target_date).execute()
            
            # 3. 출석 상태 조회
            attendance_response = self.supabase.client.table('attendance_records').select('student_email, status, notes, activity_type, activity_location').eq('attendance_date', target_date).eq('period', period).execute()
            
            # 4. 사용자 정보 조회 (학생 정보)
            users_response = self.supabase.client.table('users').select('id, email, name, student_profiles(student_id, grade, class_number)').eq('role', 'student').execute()
            users_dict = {}
            for user in users_response.data:
                profile = user['student_profiles'][0] if user['student_profiles'] else {}
                users_dict[user['email']] = {
                    'uid': user['id'],
                    'email': user['email'],
                    'name': user['name'],
                    'no': profile.get('student_id', ''),
                    'grade': profile.get('grade', 0),
                    'class_number': profile.get('class_number', 0)
                }
            
            # 5. 출석 상태를 딕셔너리로 변환
            attendance_dict = {}
            for record in attendance_response.data:
                attendance_dict[record['student_email']] = {
                    'status': record['status'],
                    'notes': record.get('notes', ''),
                    'activity_type': record.get('activity_type', ''),
                    'activity_location': record.get('activity_location', '')
                }

            # 6. 좌석 배치를 딕셔너리로 변환
            seats_dict = {}
            for seat in seat_response.data:
                seats_dict[seat['position_key']] = seat['student_emails'] or []

            # 7. DSHS-Life 방식으로 섹션 데이터 구성
            sections = []
            for section in layout['layout_config']['sections']:
                section_data = {
                    'name': section['name'],
                    'type': section.get('type', 'single'),
                    'cols': section['cols'],
                    'stick': section.get('stick', False)
                }

                sections.append(section_data)

            # 8. 좌석 라인 데이터 구성 (DSHS-Life seatLine 함수와 동일)
            def get_seat_line(prefix: str, lr: str):
                position_key = f"{prefix}-{lr}"
                student_emails = seats_dict.get(position_key, [])
                
                # 7행의 좌석 데이터 생성 (역순으로 - DSHS-Life와 동일)
                seat_items = []
                for row in range(7):
                    if row < len(student_emails) and student_emails[-(row+1)]:  # 역순
                        student_email = student_emails[-(row+1)]
                        student = users_dict.get(student_email)
                        if student:
                            attendance = attendance_dict.get(student_email, {'status': 'present'})
                            
                            # 활동 정보 구성
                            items = []
                            if attendance['status'] == 'activity':
                                activity_type = attendance.get('activity_type', '')
                                activity_location = attendance.get('activity_location', '')
                                
                                if activity_type == '분임토의실':
                                    items.append({
                                        'type': '분임토의실',
                                        'place': activity_location
                                    })
                                else:
                                    items.append({
                                        'type': activity_type,
                                        'place': activity_location
                                    })
                            
                            seat_items.append({
                                'user': student,
                                'items': items
                            })
                        else:
                            seat_items.append({'user': None, 'items': []})
                    else:
                        # 빈 자리 또는 존재하지 않는 자리
                        seat_items.append({'user': None, 'items': []})
                
                return seat_items

            return {
                'success': True,
                'classroom': layout,
                'sections': sections,
                'seat_line_func': get_seat_line,
                'seats': seats_dict,
                'date': str(target_date),
                'period': period,
                'grade_seats': [{
                    'name': layout['classroom_name'],
                    'bottom_left': layout['bottom_left_info'],
                    'seats': sections
                }]
            }

        except Exception as e:
            logger.error(f"Error fetching seat arrangement with status: {e}")
            return {'success': False, 'error': str(e)}

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
    
    def get_current_period(self, is_holiday: bool = False) -> int:
        """
        현재 시간에 해당하는 교시 계산 (DSHS-Life 방식)
        
        Args:
            is_holiday: 휴일 여부
            
        Returns:
            현재 교시 번호
        """
        now = datetime.now().time()
        
        # 자습시간 (휴일/평일 공통)
        if time(19, 0) <= now <= time(20, 50):
            return 11  # 1차자습
        elif time(21, 0) <= now <= time(22, 50):
            return 12  # 2차자습
        elif time(7, 0) <= now <= time(8, 20):
            return 13  # 3차자습
        elif time(16, 10) <= now <= time(17, 0):
            return 14  # 4차자습
        elif time(17, 10) <= now <= time(18, 0):
            return 15  # 5차자습
        
        # 평일 일반교시
        if not is_holiday:
            if time(8, 30) <= now <= time(9, 20):
                return 1
            elif time(9, 30) <= now <= time(10, 20):
                return 2
            elif time(10, 30) <= now <= time(11, 20):
                return 3
            elif time(11, 30) <= now <= time(12, 20):
                return 4
            elif time(13, 10) <= now <= time(14, 0):
                return 5
            elif time(14, 10) <= now <= time(15, 0):
                return 6
            elif time(15, 10) <= now <= time(16, 0):
                return 7
        
        # 기본값: 1차자습
        return 11
    
    def get_period_info(self, target_date: date) -> Dict[str, Any]:
        """
        날짜별 교시 정보 조회 (DSHS-Life periods_for 함수와 동일)
        
        Args:
            target_date: 조회 날짜
            
        Returns:
            교시 정보 딕셔너리
        """
        try:
            response = self.supabase.client.table('period_configs').select('*').eq('config_date', target_date).execute()
            
            if response.data:
                config = response.data[0]
                is_holiday = config['is_holiday']
                
                if is_holiday:
                    periods = [11, 22, 12, 13, 23, 14, 15, 25]  # 휴일 교시
                else:
                    periods = [1, 2, 3, 4, 22, 5, 6, 7, 11, 23, 12, 13, 25]  # 평일 교시
                
                return {
                    'success': True,
                    'date': str(target_date),
                    'config': {
                        'is_holiday': is_holiday
                    },
                    'periods': periods,
                    'period_info': config.get('period_info', {})
                }
            else:
                # 기본 평일 교시 정보 반환
                return {
                    'success': True,
                    'date': str(target_date),
                    'config': {
                        'is_holiday': False
                    },
                    'periods': [1, 2, 3, 4, 22, 5, 6, 7, 11, 23, 12, 13, 25],
                    'period_info': {}
                }
                
        except Exception as e:
            logger.error(f"Error fetching period info: {e}")
            return {
                'success': False,
                'error': str(e)
            }