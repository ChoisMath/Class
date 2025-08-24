from flask import render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime, date
import logging

from app.utils.decorators import role_required
from app.services.seating_service import SeatingService
from app.services.attendance_service import AttendanceService
from . import seating_bp

logger = logging.getLogger(__name__)

@seating_bp.route('/')
@login_required
@role_required(['teacher', 'admin', 'super_admin'])
def seating_main():
    """자리배치 시각화 메인 페이지"""
    try:
        today = date.today().isoformat()
        
        return render_template('seating/seating.html', 
                             today=today,
                             current_user=current_user)
                             
    except Exception as e:
        logger.error(f"자리배치 페이지 로드 에러: {str(e)}")
        return render_template('error.html', 
                             error_message="자리배치 페이지를 로드할 수 없습니다."), 500

@seating_bp.route('/api/seat-arrangement', methods=['POST'])
@login_required
@role_required(['teacher', 'admin', 'super_admin'])
def get_seat_arrangement():
    """자리배치 정보 조회 API (Week 2 시각화용)"""
    try:
        data = request.get_json()
        
        grade = data.get('grade', 1)
        arrangement_date = data.get('date', date.today().isoformat())
        period = data.get('period', 1)
        
        # Week 2 시각화 테스트용 샘플 데이터
        sample_data = {
            'success': True,
            'grade': grade,
            'date': arrangement_date,
            'period': period,
            'sections': [
                {
                    'name': f'{grade}-A섹션',
                    'rows': [
                        {
                            'seats': [
                                {
                                    'position': f'{grade}-A-L1',
                                    'student': {
                                        'id': '1',
                                        'name': '김철수',
                                        'student_number': f'{grade}1001'
                                    },
                                    'attendance_status': 'present',
                                    'activity': None
                                },
                                {
                                    'position': f'{grade}-A-R1',
                                    'student': {
                                        'id': '2',
                                        'name': '이영희',
                                        'student_number': f'{grade}1002'
                                    },
                                    'attendance_status': 'absent',
                                    'activity': None
                                },
                                {
                                    'position': f'{grade}-A-L3',
                                    'student': {
                                        'id': '6',
                                        'name': '홍길동',
                                        'student_number': f'{grade}1006'
                                    },
                                    'attendance_status': 'present',
                                    'activity': None
                                }
                            ]
                        },
                        {
                            'seats': [
                                {
                                    'position': f'{grade}-A-L2',
                                    'student': {
                                        'id': '3',
                                        'name': '박민수',
                                        'student_number': f'{grade}1003'
                                    },
                                    'attendance_status': 'activity',
                                    'activity': '분임토의실'
                                },
                                {
                                    'position': f'{grade}-A-R2',
                                    'student': {
                                        'id': '7',
                                        'name': '강감찬',
                                        'student_number': f'{grade}1007'
                                    },
                                    'attendance_status': 'activity',
                                    'activity': '도서관'
                                },
                                {
                                    'position': f'{grade}-A-L4',
                                    'student': None,
                                    'attendance_status': 'empty',
                                    'activity': None
                                }
                            ]
                        }
                    ]
                },
                {
                    'name': f'{grade}-B섹션',
                    'rows': [
                        {
                            'seats': [
                                {
                                    'position': f'{grade}-B-L1',
                                    'student': {
                                        'id': '4',
                                        'name': '최지현',
                                        'student_number': f'{grade}1004'
                                    },
                                    'attendance_status': 'present',
                                    'activity': None
                                },
                                {
                                    'position': f'{grade}-B-R1',
                                    'student': {
                                        'id': '5',
                                        'name': '정하늘',
                                        'student_number': f'{grade}1005'
                                    },
                                    'attendance_status': 'absent',
                                    'activity': None
                                },
                                {
                                    'position': f'{grade}-B-L3',
                                    'student': {
                                        'id': '8',
                                        'name': '윤보선',
                                        'student_number': f'{grade}1008'
                                    },
                                    'attendance_status': 'present',
                                    'activity': None
                                }
                            ]
                        },
                        {
                            'seats': [
                                {
                                    'position': f'{grade}-B-L2',
                                    'student': {
                                        'id': '9',
                                        'name': '서장훈',
                                        'student_number': f'{grade}1009'
                                    },
                                    'attendance_status': 'present',
                                    'activity': None
                                },
                                {
                                    'position': f'{grade}-B-R2',
                                    'student': {
                                        'id': '10',
                                        'name': '김유신',
                                        'student_number': f'{grade}1010'
                                    },
                                    'attendance_status': 'activity',
                                    'activity': '상담실'
                                },
                                {
                                    'position': f'{grade}-B-L4',
                                    'student': None,
                                    'attendance_status': 'empty',
                                    'activity': None
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        return jsonify(sample_data)
        
    except Exception as e:
        logger.error(f"자리배치 조회 에러: {str(e)}")
        return jsonify({
            'success': False,
            'error': '자리배치 정보를 조회할 수 없습니다.'
        }), 500

@seating_bp.route('/api/attendance-status', methods=['GET'])
@login_required
@role_required(['teacher', 'admin', 'super_admin'])
def get_attendance_status():
    """출석 상태 조회 API"""
    try:
        attendance_date = request.args.get('date', date.today().isoformat())
        period = request.args.get('period', type=int)
        classroom = request.args.get('classroom', 'grade_1')
        
        if not period:
            return jsonify({
                'success': False,
                'error': '교시 정보가 필요합니다.'
            }), 400
            
        supabase = SupabaseService()
        
        # 출석 상태 조회
        attendance_records = supabase.get_attendance_records(attendance_date, period, classroom)
        
        # 활동 정보 조회 (분임토의실 등)
        activity_records = supabase.get_activity_records(attendance_date, period)
        
        return jsonify({
            'success': True,
            'date': attendance_date,
            'period': period,
            'classroom': classroom,
            'attendance': attendance_records,
            'activities': activity_records
        })
        
    except Exception as e:
        logger.error(f"출석 상태 조회 에러: {str(e)}")
        return jsonify({
            'success': False,
            'error': '출석 상태를 조회할 수 없습니다.'
        }), 500

@seating_bp.route('/api/mark-attendance', methods=['POST'])
@login_required
@role_required(['teacher', 'admin', 'super_admin'])
def mark_attendance():
    """출석/부재 처리 API (Week 2 시각화용)"""
    try:
        data = request.get_json()
        
        attendance_date = data.get('date')
        period = data.get('period')
        student_ids = data.get('student_ids', [])
        status = data.get('status')  # 'absent', 'present'
        teacher_id = data.get('teacher_id')
        
        # 입력값 검증
        if not all([attendance_date, period, student_ids, status]):
            return jsonify({
                'success': False,
                'error': '필수 정보가 누락되었습니다.'
            }), 400
            
        if status not in ['absent', 'present']:
            return jsonify({
                'success': False,
                'error': '올바르지 않은 상태값입니다.'
            }), 400
            
        if len(student_ids) == 0:
            return jsonify({
                'success': False,
                'error': '선택된 학생이 없습니다.'
            }), 400
        
        # Week 2 테스트용 샘플 응답
        changes = []
        for student_id in student_ids:
            student_name = f"학생{student_id}"
            changes.append({
                'student_id': student_id,
                'student_name': student_name,
                'status': status,
                'timestamp': datetime.now().isoformat()
            })
        
        logger.info(f"출석 처리: {len(student_ids)}명을 {status} 처리")
        
        return jsonify({
            'success': True,
            'message': f'{len(student_ids)}명의 학생을 {status} 처리했습니다.',
            'processed_count': len(student_ids),
            'changes': changes
        })
            
    except Exception as e:
        logger.error(f"출석 처리 에러: {str(e)}")
        return jsonify({
            'success': False,
            'error': '출석 처리 중 오류가 발생했습니다.'
        }), 500

@seating_bp.route('/api/period-config', methods=['GET'])
@login_required 
@role_required(['teacher', 'admin', 'super_admin'])
def get_period_config():
    """교시 설정 조회 API"""
    try:
        config_date = request.args.get('date', date.today().isoformat())
        
        supabase = SupabaseService()
        period_config = supabase.get_period_config(config_date)
        
        return jsonify({
            'success': True,
            'date': config_date,
            'config': period_config
        })
        
    except Exception as e:
        logger.error(f"교시 설정 조회 에러: {str(e)}")
        return jsonify({
            'success': False,
            'error': '교시 설정을 조회할 수 없습니다.'
        }), 500

@seating_bp.route('/api/classroom-layout', methods=['GET'])
@login_required
@role_required(['teacher', 'admin', 'super_admin'])
def get_classroom_layout():
    """교실 레이아웃 조회 API"""
    try:
        classroom_key = request.args.get('classroom', 'grade_1')
        
        supabase = SupabaseService()
        layout = supabase.get_classroom_layout(classroom_key)
        
        return jsonify({
            'success': True,
            'classroom': classroom_key,
            'layout': layout
        })
        
    except Exception as e:
        logger.error(f"교실 레이아웃 조회 에러: {str(e)}")
        return jsonify({
            'success': False,
            'error': '교실 레이아웃을 조회할 수 없습니다.'
        }), 500

@seating_bp.route('/api/supervisor-schedule', methods=['GET'])
@login_required
@role_required(['teacher', 'admin', 'super_admin'])
def get_supervisor_schedule():
    """감독교사 스케줄 조회 API"""
    try:
        schedule_date = request.args.get('date', date.today().isoformat())
        
        supabase = SupabaseService()
        schedules = supabase.get_supervisor_schedules(schedule_date)
        
        return jsonify({
            'success': True,
            'date': schedule_date,
            'schedules': schedules
        })
        
    except Exception as e:
        logger.error(f"감독교사 스케줄 조회 에러: {str(e)}")
        return jsonify({
            'success': False,
            'error': '감독교사 스케줄을 조회할 수 없습니다.'
        }), 500

# Admin-only routes for seat arrangement management
@seating_bp.route('/admin')
@login_required
@role_required(['admin', 'super_admin'])
def seat_admin():
    """자리배치 관리자 페이지"""
    try:
        supabase = SupabaseService()
        
        # 모든 학생 목록 조회
        students = supabase.get_all_students()
        
        # 교실 레이아웃 조회
        layouts = supabase.get_classroom_layouts()
        
        return render_template('seating/admin/seat_editor.html',
                             students=students,
                             layouts=layouts,
                             current_user=current_user)
                             
    except Exception as e:
        logger.error(f"자리배치 관리자 페이지 로드 에러: {str(e)}")
        return render_template('error.html',
                             error_message="자리배치 관리자 페이지를 로드할 수 없습니다."), 500

@seating_bp.route('/api/admin/save-arrangement', methods=['POST'])
@login_required
@role_required(['admin', 'super_admin'])
def save_seat_arrangement():
    """자리배치 저장 API (관리자만)"""
    try:
        data = request.get_json()
        
        classroom = data.get('classroom')
        arrangement_date = data.get('date')
        arrangements = data.get('arrangements', {})
        
        if not all([classroom, arrangement_date]):
            return jsonify({
                'success': False,
                'error': '필수 정보가 누락되었습니다.'
            }), 400
            
        supabase = SupabaseService()
        
        result = supabase.save_seat_arrangements(
            classroom=classroom,
            arrangement_date=arrangement_date,
            arrangements=arrangements,
            created_by_email=current_user.email
        )
        
        return jsonify({
            'success': result['success'],
            'message': '자리배치가 성공적으로 저장되었습니다.' if result['success'] else result['error']
        })
        
    except Exception as e:
        logger.error(f"자리배치 저장 에러: {str(e)}")
        return jsonify({
            'success': False,
            'error': '자리배치 저장 중 오류가 발생했습니다.'
        }), 500

# =============================================================================
# DSHS-Life 스타일 API 엔드포인트
# =============================================================================

@seating_bp.route('/api/seats')
@login_required
@role_required(['teacher', 'admin', 'super_admin'])
def get_seats():
    """자리배치표 불러오기 (DSHS-Life /selfstudy/seats와 동일)"""
    try:
        seating_service = SeatingService()
        
        # 모든 교실 레이아웃 조회
        layouts_result = seating_service.get_classroom_layouts()
        if not layouts_result['success']:
            return jsonify({
                'error': 'Classroom layouts not found'
            }), 404
        
        # 자리배치 데이터를 DSHS-Life 형식으로 변환
        seats = []
        for layout in layouts_result['layouts']:
            classroom_key = layout['classroom_key']
            
            # 오늘 날짜의 자리배치 조회
            today = date.today()
            arrangement_result = seating_service.get_seat_arrangements(classroom_key, str(today))
            
            if arrangement_result['success']:
                arrangements = arrangement_result['arrangements']
                for position_key, student_emails in arrangements.items():
                    # DSHS-Life 형식: prefix, snums
                    seats.append({
                        'prefix': position_key,
                        'snums': student_emails  # 학생 이메일 배열
                    })
        
        return jsonify({
            'seats': seats
        })
        
    except Exception as e:
        logger.error(f"Error in get_seats: {e}")
        return jsonify({
            'error': 'Internal server error'
        }), 500

@seating_bp.route('/api/missing')
@login_required
@role_required(['teacher', 'admin', 'super_admin'])
def get_missing():
    """부재 처리된 학생 목록 (DSHS-Life /selfstudy/missing과 동일)"""
    try:
        target_date = request.args.get('date', date.today().isoformat())
        target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        
        attendance_service = AttendanceService()
        result = attendance_service.get_missing_students(target_date)
        
        if result['success']:
            return jsonify({
                'items': result['items']  # 교시별 부재 학생 목록
            })
        else:
            return jsonify({
                'error': result.get('error', 'Failed to fetch missing students')
            }), 500
            
    except Exception as e:
        logger.error(f"Error in get_missing: {e}")
        return jsonify({
            'error': 'Internal server error'
        }), 500

@seating_bp.route('/api/missing', methods=['POST'])
@login_required
@role_required(['teacher', 'admin', 'super_admin'])
def mark_missing():
    """부재/복귀 처리 (DSHS-Life /selfstudy/missing POST와 동일)"""
    try:
        data = request.get_json()
        
        action = data.get('action')  # 'miss' or 'return'
        target_date = data.get('date')
        period = data.get('period')
        student_emails = data.get('uids', [])  # DSHS-Life에서는 uids
        
        # 입력값 검증
        if action not in ('miss', 'return'):
            return jsonify({
                'error': 'Bad Request'
            }), 400
            
        if not target_date or not period or len(student_emails) == 0:
            return jsonify({
                'error': '필수 정보가 누락되었습니다.'
            }), 400
        
        # 날짜 변환
        target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        
        # 출석 처리
        attendance_service = AttendanceService()
        result = attendance_service.mark_attendance_dshs(
            action=action,
            target_date=target_date,
            period=period,
            student_emails=student_emails,
            teacher_email=current_user.email
        )
        
        if result['success']:
            return jsonify({
                'error': None  # DSHS-Life 응답 형식
            })
        else:
            return jsonify({
                'error': result.get('error', 'Processing failed')
            }), 400
            
    except Exception as e:
        logger.error(f"Error in mark_missing: {e}")
        return jsonify({
            'error': 'Internal server error'
        }), 500

@seating_bp.route('/api/config')
@login_required
@role_required(['teacher', 'admin', 'super_admin'])
def get_date_config():
    """날짜별 교시 설정 조회 (DSHS-Life /config와 동일)"""
    try:
        target_date = request.args.get('date', date.today().isoformat())
        target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        
        seating_service = SeatingService()
        result = seating_service.get_period_info(target_date)
        
        if result['success']:
            return jsonify({
                'date': result['date'],
                'config': result['config'],
                'periods': result['periods']
            })
        else:
            return jsonify({
                'error': result.get('error', 'Failed to fetch date config')
            }), 500
            
    except Exception as e:
        logger.error(f"Error in get_date_config: {e}")
        return jsonify({
            'error': 'Internal server error'
        }), 500

@seating_bp.route('/api/supervisor')
@login_required
@role_required(['teacher', 'admin', 'super_admin'])
def get_supervisor():
    """감독교사 정보 조회 (DSHS-Life /selfstudy/supervisor와 동일)"""
    try:
        target_date = request.args.get('date', date.today().isoformat())
        
        # 샘플 감독교사 데이터 (실제 구현에서는 DB에서 조회)
        supervisor_data = [
            {
                'grade': 1,
                'teacher_name': current_user.name,
                'period': '1차자습',
                'time': '19:00-20:50'
            },
            {
                'grade': 2,
                'teacher_name': '박철수',
                'period': '2차자습',
                'time': '21:00-22:50'
            }
        ]
        
        return jsonify({
            'items': supervisor_data
        })
        
    except Exception as e:
        logger.error(f"Error in get_supervisor: {e}")
        return jsonify({
            'error': 'Internal server error'
        }), 500