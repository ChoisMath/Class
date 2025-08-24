"""
출석 관리 서비스 (DSHS-Life 스타일)
DSHS-Life Style Attendance Management Service
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, date

from .supabase_service import SupabaseService

logger = logging.getLogger(__name__)

class AttendanceService:
    """DSHS-Life 스타일 출석 관리 서비스 클래스"""
    
    def __init__(self):
        self.supabase = SupabaseService()
    
    def get_missing_students(self, target_date: date) -> Dict[str, Any]:
        """
        날짜별 부재 학생 목록 조회 (DSHS-Life 방식)
        
        Args:
            target_date: 조회 날짜
            
        Returns:
            교시별 부재 학생 목록 (DSHS-Life /selfstudy/missing과 동일)
        """
        try:
            response = self.supabase.client.table('attendance_records') \
                .select('period, student_email') \
                .eq('attendance_date', target_date) \
                .eq('status', 'absent') \
                .execute()
            
            # 교시별로 부재 학생 그룹화
            missings = {}
            for record in response.data:
                period = record['period']
                if period not in missings:
                    missings[period] = []
                missings[period].append(record['student_email'])
            
            return {
                'success': True,
                'items': missings
            }
            
        except Exception as e:
            logger.error(f"Error fetching missing students: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def mark_attendance_dshs(self, action: str, target_date: date, period: int, 
                           student_emails: List[str], teacher_email: str) -> Dict[str, Any]:
        """
        부재/복귀 처리 (DSHS-Life 방식)
        
        Args:
            action: 'miss' 또는 'return'
            target_date: 날짜
            period: 교시
            student_emails: 학생 이메일 목록
            teacher_email: 처리하는 교사 이메일
            
        Returns:
            처리 결과 (DSHS-Life /selfstudy/missing POST와 동일)
        """
        try:
            # 교시 유효성 검증
            period_result = self.validate_period(target_date, period)
            if not period_result['valid']:
                return {
                    'success': False,
                    'error': '해당 일자에 처리할 수 없는 교시입니다.'
                }
            
            # 교사 정보 조회
            teacher_response = self.supabase.client.table('users') \
                .select('id, name') \
                .eq('email', teacher_email) \
                .eq('role', 'teacher') \
                .single() \
                .execute()
            
            if not teacher_response.data:
                return {
                    'success': False,
                    'error': '교사 정보를 찾을 수 없습니다.'
                }
            
            teacher_id = teacher_response.data['id']
            processed_students = []
            
            for student_email in student_emails:
                # 학생 정보 조회
                student_response = self.supabase.client.table('users') \
                    .select('id, name, student_profiles(parent_phone)') \
                    .eq('email', student_email) \
                    .eq('role', 'student') \
                    .single() \
                    .execute()
                
                if not student_response.data:
                    continue
                    
                student = student_response.data
                student_id = student['id']
                
                # 기존 출석 기록 확인
                existing_response = self.supabase.client.table('attendance_records') \
                    .select('id, status') \
                    .eq('attendance_date', target_date) \
                    .eq('period', period) \
                    .eq('student_id', student_id) \
                    .execute()
                
                if action == 'miss':
                    # 부재 처리
                    if existing_response.data and existing_response.data[0]['status'] == 'absent':
                        # 이미 부재 처리된 경우 건너뛰기 (DSHS-Life 로직)
                        continue
                    
                    record_data = {
                        'attendance_date': target_date,
                        'period': period,
                        'student_id': student_id,
                        'student_email': student_email,
                        'status': 'absent',
                        'marked_by': teacher_id,
                        'marked_at': datetime.now().isoformat(),
                        'notes': f'{self.format_period(period)} 부재 처리'
                    }
                    
                    if existing_response.data:
                        # 기존 기록 업데이트
                        self.supabase.client.table('attendance_records') \
                            .update(record_data) \
                            .eq('id', existing_response.data[0]['id']) \
                            .execute()
                    else:
                        # 새 기록 삽입
                        self.supabase.client.table('attendance_records') \
                            .insert(record_data) \
                            .execute()
                    
                    processed_students.append(student['name'])
                
                elif action == 'return':
                    # 복귀 처리
                    if not existing_response.data or existing_response.data[0]['status'] != 'absent':
                        # 부재 상태가 아닌 경우 건너뛰기 (DSHS-Life 로직)
                        continue
                    
                    # 복귀 처리
                    self.supabase.client.table('attendance_records') \
                        .update({
                            'status': 'returned',
                            'returned_by': teacher_id,
                            'returned_at': datetime.now().isoformat(),
                            'notes': f'{self.format_period(period)} 복귀 처리'
                        }) \
                        .eq('id', existing_response.data[0]['id']) \
                        .execute()
                    
                    processed_students.append(student['name'])
            
            # TODO: SMS 알림 발송 (현재는 이메일로 대체 가능)
            # DSHS-Life에서는 부재 처리 시 SMS 발송
            
            return {
                'success': True,
                'error': None,  # DSHS-Life 응답 형식
                'processed_count': len(processed_students),
                'processed_students': processed_students
            }
            
        except Exception as e:
            logger.error(f"Error in DSHS attendance marking ({action}): {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def format_period(self, period: int) -> str:
        """
        교시 번호를 형식화된 문자열로 변환 (DSHS-Life period_format 함수)
        
        Args:
            period: 교시 번호
            
        Returns:
            형식화된 교시 문자열
        """
        if period == 0:
            return '-'
        if period < 10:
            return f'{period}교시'
        if period < 20:
            return f'{period % 10}차자습'
        if period == 21:
            return '조식'
        if period == 22:
            return '중식'
        if period == 23:
            return '석식'
        if period == 25:
            return '외박'
        
        return '-'
    
    def validate_period(self, target_date: date, period: int) -> Dict[str, Any]:
        """
        교시 유효성 검증 (DSHS-Life 방식)
        
        Args:
            target_date: 날짜
            period: 교시
            
        Returns:
            유효성 검증 결과
        """
        try:
            # 교시 설정 조회
            response = self.supabase.client.table('period_configs') \
                .select('is_holiday, regular_periods, study_periods, meal_periods, special_periods') \
                .eq('config_date', target_date) \
                .execute()
            
            if response.data:
                config = response.data[0]
                is_holiday = config['is_holiday']
                
                if is_holiday:
                    valid_periods = [11, 22, 12, 13, 23, 14, 15, 25]
                else:
                    valid_periods = [1, 2, 3, 4, 22, 5, 6, 7, 11, 23, 12, 13, 25]
                
                return {
                    'valid': period in valid_periods,
                    'is_holiday': is_holiday
                }
            else:
                # 기본 평일 교시
                valid_periods = [1, 2, 3, 4, 22, 5, 6, 7, 11, 23, 12, 13, 25]
                return {
                    'valid': period in valid_periods,
                    'is_holiday': False
                }
                
        except Exception as e:
            logger.error(f"Error validating period: {e}")
            # 기본값으로 평일 교시 허용
            valid_periods = [1, 2, 3, 4, 22, 5, 6, 7, 11, 23, 12, 13, 25]
            return {
                'valid': period in valid_periods,
                'is_holiday': False
            }
    
    def get_attendance_records(self, attendance_date: str, period: int, 
                             classroom: Optional[str] = None) -> Dict[str, Any]:
        """출석 기록 조회"""
        try:
            query = self.supabase.client.table('attendance_records') \
                .select('*, users(id, email, name, student_profiles(student_id, grade, class_number))') \
                .eq('attendance_date', attendance_date) \
                .eq('period', period)
            
            # 교실별 필터링이 필요한 경우 (향후 구현)
            if classroom:
                # 해당 교실의 학생들만 필터링하는 로직 추가 필요
                pass
            
            response = query.execute()
            
            # 상태별로 그룹화
            attendance_status = {
                'present': [],
                'absent': [],
                'returned': [],
                'activity': []
            }
            
            for record in response.data:
                student_info = {
                    'id': record['student_id'],
                    'email': record['student_email'],
                    'name': record['users']['name'] if record['users'] else '알 수 없음',
                    'number': record['users']['student_profiles'][0]['student_id'] if record['users'] and record['users']['student_profiles'] else '',
                    'status': record['status'],
                    'marked_at': record['marked_at'],
                    'returned_at': record['returned_at'],
                    'notes': record['notes'],
                    'activity_type': record['activity_type'],
                    'activity_location': record['activity_location']
                }
                
                if record['status'] in attendance_status:
                    attendance_status[record['status']].append(student_info)
            
            return {
                'success': True,
                'attendance_status': attendance_status,
                'total_records': len(response.data)
            }
            
        except Exception as e:
            logger.error(f"출석 기록 조회 에러: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def mark_attendance_bulk(self, attendance_date: str, period: int, 
                           student_emails: List[str], status: str,
                           marked_by_email: str, notes: str = '') -> Dict[str, Any]:
        """일괄 출석 처리"""
        try:
            # 처리자 ID 조회
            marker_response = self.supabase.client.table('users') \
                .select('id') \
                .eq('email', marked_by_email) \
                .single() \
                .execute()
            
            marked_by_id = marker_response.data['id']
            
            # 학생 ID 조회
            students_response = self.supabase.client.table('users') \
                .select('id, email') \
                .in_('email', student_emails) \
                .eq('role', 'student') \
                .execute()
            
            student_id_map = {student['email']: student['id'] for student in students_response.data}
            
            processed_count = 0
            
            for email in student_emails:
                if email not in student_id_map:
                    logger.warning(f"학생을 찾을 수 없음: {email}")
                    continue
                
                student_id = student_id_map[email]
                current_time = datetime.now().isoformat()
                
                # 기존 기록 확인
                existing_response = self.supabase.client.table('attendance_records') \
                    .select('id, status') \
                    .eq('attendance_date', attendance_date) \
                    .eq('period', period) \
                    .eq('student_id', student_id) \
                    .execute()
                
                if existing_response.data:
                    # 기존 기록 업데이트
                    existing_record = existing_response.data[0]
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
                    
                    self.supabase.client.table('attendance_records') \
                        .update(update_data) \
                        .eq('id', existing_record['id']) \
                        .execute()
                        
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
                    
                    self.supabase.client.table('attendance_records') \
                        .insert(insert_data) \
                        .execute()
                
                processed_count += 1
            
            return {
                'success': True,
                'processed_count': processed_count
            }
            
        except Exception as e:
            logger.error(f"일괄 출석 처리 에러: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_activity_records(self, activity_date: str, period: int) -> Dict[str, Any]:
        """활동 기록 조회 (분임토의실 등)"""
        try:
            response = self.supabase.client.table('attendance_records') \
                .select('*, users(name, student_profiles(student_id))') \
                .eq('attendance_date', activity_date) \
                .eq('period', period) \
                .eq('status', 'activity') \
                .execute()
            
            activities = []
            for record in response.data:
                activities.append({
                    'student_email': record['student_email'],
                    'student_name': record['users']['name'] if record['users'] else '알 수 없음',
                    'student_number': record['users']['student_profiles'][0]['student_id'] if record['users'] and record['users']['student_profiles'] else '',
                    'activity_type': record['activity_type'],
                    'activity_location': record['activity_location'],
                    'notes': record['notes']
                })
            
            return {
                'success': True,
                'activities': activities,
                'total_count': len(activities)
            }
            
        except Exception as e:
            logger.error(f"활동 기록 조회 에러: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_attendance_statistics(self, date_from: str, date_to: str) -> Dict[str, Any]:
        """출석 통계 조회"""
        try:
            response = self.supabase.client.table('attendance_records') \
                .select('attendance_date, period, status, student_email') \
                .gte('attendance_date', date_from) \
                .lte('attendance_date', date_to) \
                .execute()
            
            # 통계 계산
            stats = {
                'total_records': len(response.data),
                'by_status': {},
                'by_date': {},
                'by_period': {}
            }
            
            for record in response.data:
                status = record['status']
                date = record['attendance_date']
                period = record['period']
                
                # 상태별 통계
                if status not in stats['by_status']:
                    stats['by_status'][status] = 0
                stats['by_status'][status] += 1
                
                # 날짜별 통계
                if date not in stats['by_date']:
                    stats['by_date'][date] = {'total': 0, 'absent': 0, 'present': 0}
                stats['by_date'][date]['total'] += 1
                if status in stats['by_date'][date]:
                    stats['by_date'][date][status] += 1
                
                # 교시별 통계
                if period not in stats['by_period']:
                    stats['by_period'][period] = {'total': 0, 'absent': 0, 'present': 0}
                stats['by_period'][period]['total'] += 1
                if status in stats['by_period'][period]:
                    stats['by_period'][period][status] += 1
            
            return {
                'success': True,
                'date_range': {'from': date_from, 'to': date_to},
                'statistics': stats
            }
            
        except Exception as e:
            logger.error(f"출석 통계 조회 에러: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }