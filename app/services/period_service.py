"""
교시 관리 서비스
Period Management Service
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, date

from .supabase_service import SupabaseService

logger = logging.getLogger(__name__)

class PeriodService:
    """교시 관리 서비스 클래스"""
    
    def __init__(self):
        self.supabase = SupabaseService()
    
    def get_period_config(self, config_date: str) -> Dict[str, Any]:
        """특정 날짜의 교시 설정 조회"""
        try:
            response = self.supabase.client.table('period_configs') \
                .select('*') \
                .eq('config_date', config_date) \
                .single() \
                .execute()
            
            if response.data:
                return {
                    'success': True,
                    'config': response.data
                }
            else:
                # 해당 날짜의 설정이 없으면 기본 설정 반환
                return self.get_default_period_config(config_date)
                
        except Exception as e:
            # 데이터가 없는 경우 기본 설정 반환
            logger.info(f"교시 설정 조회 실패, 기본 설정 사용: {str(e)}")
            return self.get_default_period_config(config_date)
    
    def get_default_period_config(self, config_date: str) -> Dict[str, Any]:
        """기본 교시 설정 반환"""
        try:
            # 요일 확인 (주말 여부)
            target_date = datetime.strptime(config_date, '%Y-%m-%d')
            is_holiday = target_date.weekday() >= 5  # 토요일(5), 일요일(6)
            
            if is_holiday:
                # 휴일 교시 설정
                periods = [11, 22, 12, 13, 23, 14, 15, 25]
            else:
                # 평일 교시 설정
                periods = [1, 2, 3, 4, 22, 5, 6, 7, 11, 23, 12, 13, 25]
            
            period_info = {
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
            }
            
            default_config = {
                'config_date': config_date,
                'is_holiday': is_holiday,
                'regular_periods': [1, 2, 3, 4, 5, 6, 7] if not is_holiday else [],
                'study_periods': [11, 12, 13, 14, 15],
                'meal_periods': [22, 23],
                'special_periods': [21, 25],
                'period_info': period_info,
                'all_periods': periods
            }
            
            return {
                'success': True,
                'config': default_config
            }
            
        except Exception as e:
            logger.error(f"기본 교시 설정 생성 에러: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def save_period_config(self, config_date: str, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """교시 설정 저장"""
        try:
            # 기존 설정 확인
            existing_response = self.supabase.client.table('period_configs') \
                .select('id') \
                .eq('config_date', config_date) \
                .execute()
            
            if existing_response.data:
                # 업데이트
                self.supabase.client.table('period_configs') \
                    .update(config_data) \
                    .eq('config_date', config_date) \
                    .execute()
            else:
                # 새로 생성
                config_data['config_date'] = config_date
                self.supabase.client.table('period_configs') \
                    .insert(config_data) \
                    .execute()
            
            return {
                'success': True,
                'message': '교시 설정이 저장되었습니다.'
            }
            
        except Exception as e:
            logger.error(f"교시 설정 저장 에러: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def format_period(self, period: int) -> str:
        """교시 번호를 포맷된 문자열로 변환"""
        period_formats = {
            1: '1교시', 2: '2교시', 3: '3교시', 4: '4교시',
            5: '5교시', 6: '6교시', 7: '7교시',
            11: '1차자습', 12: '2차자습', 13: '3차자습', 14: '4차자습', 15: '5차자습',
            21: '조식', 22: '중식', 23: '석식', 25: '외박'
        }
        
        return period_formats.get(period, f'{period}교시')
    
    def parse_period(self, period_str: str) -> int:
        """포맷된 교시 문자열을 번호로 변환"""
        period_mapping = {
            '조식': 21, '중식': 22, '석식': 23, '외박': 25,
            '1차자습': 11, '2차자습': 12, '3차자습': 13, '4차자습': 14, '5차자습': 15
        }
        
        if period_str in period_mapping:
            return period_mapping[period_str]
        
        # 교시 패턴 체크 (예: "1교시" -> 1)
        if period_str.endswith('교시') and len(period_str) == 3:
            try:
                period = int(period_str[0])
                if 1 <= period <= 7:
                    return period
            except ValueError:
                pass
        
        return 0
    
    def get_current_period(self, current_time: str = None, is_holiday: bool = False) -> int:
        """현재 시간에 해당하는 교시 반환"""
        if current_time is None:
            current_time = datetime.now().strftime('%H:%M')
        
        try:
            current_hour, current_minute = map(int, current_time.split(':'))
            current_minutes = current_hour * 60 + current_minute
            
            # 교시별 시간 설정 (분 단위)
            time_ranges = {
                1: (8*60+30, 9*60+20),    # 08:30-09:20
                2: (9*60+30, 10*60+20),   # 09:30-10:20
                3: (10*60+30, 11*60+20),  # 10:30-11:20
                4: (11*60+30, 12*60+20),  # 11:30-12:20
                5: (13*60+10, 14*60),     # 13:10-14:00
                6: (14*60+10, 15*60),     # 14:10-15:00
                7: (15*60+10, 16*60),     # 15:10-16:00
                11: (19*60, 20*60+50),    # 19:00-20:50
                12: (21*60, 22*60+50),    # 21:00-22:50
                13: (7*60, 8*60+20),      # 07:00-08:20
                14: (16*60+10, 17*60),    # 16:10-17:00
                15: (17*60+10, 18*60),    # 17:10-18:00
                21: (6*60+30, 7*60+30),   # 06:30-07:30 (조식)
                22: (12*60+20, 13*60+10), # 12:20-13:10 (중식)
                23: (18*60, 19*60),       # 18:00-19:00 (석식)
            }
            
            # 현재 시간이 속한 교시 찾기
            for period, (start, end) in time_ranges.items():
                if start <= current_minutes <= end:
                    return period
            
            # 기본값: 평일이면 1교시, 휴일이면 1차자습
            return 11 if is_holiday else 1
            
        except Exception as e:
            logger.error(f"현재 교시 계산 에러: {str(e)}")
            return 11 if is_holiday else 1
    
    def get_supervisor_schedules(self, schedule_date: str) -> Dict[str, Any]:
        """감독교사 스케줄 조회"""
        try:
            response = self.supabase.client.table('supervisor_schedules') \
                .select('*, users(name, teacher_profiles(position, subject))') \
                .eq('schedule_date', schedule_date) \
                .order('grade, start_time') \
                .execute()
            
            # 학년별로 그룹화
            schedules_by_grade = {1: [], 2: [], 3: []}
            
            for schedule in response.data:
                grade = schedule['grade']
                teacher_info = {
                    'teacher_email': schedule['teacher_email'],
                    'teacher_name': schedule['users']['name'] if schedule['users'] else '알 수 없음',
                    'position': schedule['users']['teacher_profiles'][0]['position'] if schedule['users'] and schedule['users']['teacher_profiles'] else '',
                    'subject': schedule['users']['teacher_profiles'][0]['subject'] if schedule['users'] and schedule['users']['teacher_profiles'] else '',
                    'start_time': schedule['start_time'],
                    'end_time': schedule['end_time'],
                    'notes': schedule['notes']
                }
                
                if grade in schedules_by_grade:
                    schedules_by_grade[grade].append(teacher_info)
            
            return {
                'success': True,
                'schedules': schedules_by_grade,
                'total_count': len(response.data)
            }
            
        except Exception as e:
            logger.error(f"감독교사 스케줄 조회 에러: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }