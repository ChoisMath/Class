"""
알림 서비스
Notification Service for absence alerts and other notifications
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import os

from flask import current_app
from flask_mail import Message
from app import mail

logger = logging.getLogger(__name__)

class NotificationService:
    """알림 서비스 클래스"""
    
    @staticmethod
    def send_absence_notification(student_email: str, date: str, period: int) -> Dict[str, Any]:
        """부재 알림 이메일 발송"""
        try:
            from app.services.supabase_service import SupabaseService
            from app.services.period_service import PeriodService
            
            supabase = SupabaseService()
            period_service = PeriodService()
            
            # 학생 정보 조회
            student = supabase.get_user_by_email(student_email)
            if not student:
                return {'success': False, 'error': '학생을 찾을 수 없습니다.'}
            
            # 학생 프로필 조회
            student_profile = supabase.get_student_profile(student['id'])
            
            # 교시 포맷팅
            period_name = period_service.format_period(period)
            
            # 이메일 내용 구성
            subject = f'[학습관리시스템] 자율학습 부재 알림'
            
            html_body = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #d32f2f;">자율학습 부재 알림</h2>
                
                <div style="background-color: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3>부재 정보</h3>
                    <p><strong>학생명:</strong> {student['name']}</p>
                    <p><strong>이메일:</strong> {student['email']}</p>
                    {f"<p><strong>학번:</strong> {student_profile['student_id']}</p>" if student_profile and student_profile.get('student_id') else ""}
                    {f"<p><strong>학년/반:</strong> {student_profile['grade']}학년 {student_profile['class_number']}반</p>" if student_profile and student_profile.get('grade') else ""}
                    <p><strong>날짜:</strong> {date}</p>
                    <p><strong>교시:</strong> {period_name}</p>
                    <p><strong>시간:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                </div>
                
                <div style="background-color: #fff3e0; padding: 15px; border-radius: 8px; border-left: 4px solid #ff9800;">
                    <p><strong>안내사항:</strong></p>
                    <p>자율학습 자리검사에서 부재가 확인되었습니다.</p>
                    <p>감독교사에게 즉시 보고하시기 바랍니다.</p>
                </div>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px;">
                    <p>이 메시지는 자동으로 발송되었습니다.</p>
                    <p>문의사항은 학교 관리자에게 연락하시기 바랍니다.</p>
                </div>
            </div>
            """
            
            # 이메일 수신자 목록 (학생과 학부모)
            recipients = [student['email']]
            
            # 학부모 연락처가 있는 경우 추가
            if student_profile and student_profile.get('parent_phone'):
                # 실제 구현에서는 SMS 서비스를 사용할 수 있음
                logger.info(f"SMS 알림 대상: {student_profile['parent_phone']}")
            
            # 이메일 발송
            msg = Message(
                subject=subject,
                recipients=recipients,
                html=html_body,
                sender=current_app.config.get('MAIL_DEFAULT_SENDER')
            )
            
            mail.send(msg)
            
            return {
                'success': True,
                'message': '부재 알림이 발송되었습니다.',
                'recipients': recipients
            }
            
        except Exception as e:
            logger.error(f"부재 알림 발송 에러: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def send_return_notification(student_email: str, date: str, period: int) -> Dict[str, Any]:
        """복귀 알림 이메일 발송"""
        try:
            from app.services.supabase_service import SupabaseService
            from app.services.period_service import PeriodService
            
            supabase = SupabaseService()
            period_service = PeriodService()
            
            # 학생 정보 조회
            student = supabase.get_user_by_email(student_email)
            if not student:
                return {'success': False, 'error': '학생을 찾을 수 없습니다.'}
            
            # 학생 프로필 조회
            student_profile = supabase.get_student_profile(student['id'])
            
            # 교시 포맷팅
            period_name = period_service.format_period(period)
            
            # 이메일 내용 구성
            subject = f'[학습관리시스템] 자율학습 복귀 확인'
            
            html_body = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #4caf50;">자율학습 복귀 확인</h2>
                
                <div style="background-color: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3>복귀 정보</h3>
                    <p><strong>학생명:</strong> {student['name']}</p>
                    <p><strong>이메일:</strong> {student['email']}</p>
                    {f"<p><strong>학번:</strong> {student_profile['student_id']}</p>" if student_profile and student_profile.get('student_id') else ""}
                    {f"<p><strong>학년/반:</strong> {student_profile['grade']}학년 {student_profile['class_number']}반</p>" if student_profile and student_profile.get('grade') else ""}
                    <p><strong>날짜:</strong> {date}</p>
                    <p><strong>교시:</strong> {period_name}</p>
                    <p><strong>복귀 시간:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                </div>
                
                <div style="background-color: #e8f5e8; padding: 15px; border-radius: 8px; border-left: 4px solid #4caf50;">
                    <p><strong>알림:</strong></p>
                    <p>자율학습 복귀가 확인되었습니다.</p>
                    <p>정상적으로 출석 처리되었습니다.</p>
                </div>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px;">
                    <p>이 메시지는 자동으로 발송되었습니다.</p>
                    <p>문의사항은 학교 관리자에게 연락하시기 바랍니다.</p>
                </div>
            </div>
            """
            
            # 이메일 발송
            msg = Message(
                subject=subject,
                recipients=[student['email']],
                html=html_body,
                sender=current_app.config.get('MAIL_DEFAULT_SENDER')
            )
            
            mail.send(msg)
            
            return {
                'success': True,
                'message': '복귀 알림이 발송되었습니다.',
                'recipient': student['email']
            }
            
        except Exception as e:
            logger.error(f"복귀 알림 발송 에러: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def send_bulk_attendance_summary(teacher_email: str, attendance_summary: Dict[str, Any]) -> Dict[str, Any]:
        """교사에게 일괄 출석 처리 결과 요약 발송"""
        try:
            from app.services.supabase_service import SupabaseService
            
            supabase = SupabaseService()
            
            # 교사 정보 조회
            teacher = supabase.get_user_by_email(teacher_email)
            if not teacher:
                return {'success': False, 'error': '교사를 찾을 수 없습니다.'}
            
            date = attendance_summary.get('date')
            period = attendance_summary.get('period')
            processed_students = attendance_summary.get('processed_students', [])
            status = attendance_summary.get('status')
            
            # 이메일 내용 구성
            subject = f'[학습관리시스템] 출석 처리 완료 - {date} {period}교시'
            
            student_list_html = ""
            for i, student in enumerate(processed_students, 1):
                student_list_html += f"<tr><td>{i}</td><td>{student.get('name', '알 수 없음')}</td><td>{student.get('email')}</td></tr>"
            
            html_body = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #1976d2;">출석 처리 완료</h2>
                
                <div style="background-color: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3>처리 정보</h3>
                    <p><strong>처리자:</strong> {teacher['name']} ({teacher['email']})</p>
                    <p><strong>날짜:</strong> {date}</p>
                    <p><strong>교시:</strong> {period}교시</p>
                    <p><strong>처리 상태:</strong> {status}</p>
                    <p><strong>처리된 학생 수:</strong> {len(processed_students)}명</p>
                    <p><strong>처리 시간:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                </div>
                
                <div style="margin: 20px 0;">
                    <h3>처리된 학생 목록</h3>
                    <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                        <thead>
                            <tr style="background-color: #e3f2fd;">
                                <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">번호</th>
                                <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">학생명</th>
                                <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">이메일</th>
                            </tr>
                        </thead>
                        <tbody>
                            {student_list_html}
                        </tbody>
                    </table>
                </div>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px;">
                    <p>출석 처리가 정상적으로 완료되었습니다.</p>
                    <p>이 메시지는 자동으로 발송되었습니다.</p>
                </div>
            </div>
            """
            
            # 이메일 발송
            msg = Message(
                subject=subject,
                recipients=[teacher['email']],
                html=html_body,
                sender=current_app.config.get('MAIL_DEFAULT_SENDER')
            )
            
            mail.send(msg)
            
            return {
                'success': True,
                'message': '출석 처리 요약이 발송되었습니다.',
                'recipient': teacher['email']
            }
            
        except Exception as e:
            logger.error(f"출석 처리 요약 발송 에러: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }