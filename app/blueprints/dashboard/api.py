from flask import request, jsonify
from flask_login import login_required, current_user
from app.utils.decorators import admin_required, permission_required
from app.services.supabase_service import supabase_service
from . import dashboard_bp

# Super Admin - 사용자 관리 API
@dashboard_bp.route('/api/users', methods=['GET'])
@login_required
@permission_required('full_access')
def get_users():
    """전체 사용자 목록 조회 (super_admin 전용)"""
    try:
        users = supabase_service.get_all_users()
        return jsonify({'success': True, 'users': users})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@dashboard_bp.route('/api/users', methods=['POST'])
@login_required
@permission_required('full_access')
def create_user():
    """새 사용자 생성 (super_admin 전용)"""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['email', 'name', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'{field}는 필수 항목입니다.'}), 400
        
        # 이메일 중복 체크
        existing_user = supabase_service.get_user_by_email(data['email'])
        if existing_user:
            return jsonify({'success': False, 'message': '이미 존재하는 이메일입니다.'}), 400
        
        # 사용자 생성
        user_data = {
            'email': data['email'],
            'name': data['name'],
            'role': data['role'],
            'is_active': data.get('is_active', True)
        }
        
        result = supabase_service.create_user(user_data)
        if result:
            return jsonify({'success': True, 'message': '사용자가 성공적으로 생성되었습니다.'})
        else:
            return jsonify({'success': False, 'message': '사용자 생성에 실패했습니다.'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@dashboard_bp.route('/api/users/<user_id>', methods=['PUT'])
@login_required
@permission_required('full_access')
def update_user(user_id):
    """사용자 정보 수정 (super_admin 전용)"""
    try:
        data = request.get_json()
        
        # 수정 가능한 필드만 추출
        update_data = {}
        allowed_fields = ['name', 'role', 'is_active']
        
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        if not update_data:
            return jsonify({'success': False, 'message': '수정할 데이터가 없습니다.'}), 400
        
        result = supabase_service.update_user(user_id, update_data)
        if result:
            return jsonify({'success': True, 'message': '사용자 정보가 성공적으로 수정되었습니다.'})
        else:
            return jsonify({'success': False, 'message': '사용자 정보 수정에 실패했습니다.'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@dashboard_bp.route('/api/users/<user_id>', methods=['DELETE'])
@login_required
@permission_required('full_access')
def delete_user(user_id):
    """사용자 삭제 (super_admin 전용)"""
    try:
        # 자기 자신은 삭제할 수 없음
        user_to_delete = supabase_service.get_user_by_id(user_id)
        if user_to_delete and user_to_delete.get('email') == current_user.email:
            return jsonify({'success': False, 'message': '자기 자신은 삭제할 수 없습니다.'}), 400
        
        result = supabase_service.delete_user(user_id)
        if result:
            return jsonify({'success': True, 'message': '사용자가 성공적으로 삭제되었습니다.'})
        else:
            return jsonify({'success': False, 'message': '사용자 삭제에 실패했습니다.'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Admin - 학교 관리 API
@dashboard_bp.route('/api/schools', methods=['GET'])
@login_required
def get_schools():
    """학교 목록 조회"""
    try:
        # admin과 super_admin만 접근 가능
        if current_user.role not in ['admin', 'super_admin']:
            return jsonify({'success': False, 'message': '접근 권한이 없습니다.'}), 403
            
        schools = supabase_service.get_schools()
        return jsonify({'success': True, 'schools': schools})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@dashboard_bp.route('/api/schools', methods=['POST'])
@login_required
def create_school():
    """학교 생성"""
    try:
        if current_user.role not in ['admin', 'super_admin']:
            return jsonify({'success': False, 'message': '접근 권한이 없습니다.'}), 403
            
        data = request.get_json()
        
        required_fields = ['name', 'grade_count']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'{field}는 필수 항목입니다.'}), 400
        
        result = supabase_service.create_school(data)
        if result:
            return jsonify({'success': True, 'message': '학교가 성공적으로 생성되었습니다.'})
        else:
            return jsonify({'success': False, 'message': '학교 생성에 실패했습니다.'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@dashboard_bp.route('/api/schools/<school_id>', methods=['PUT'])
@login_required
def update_school(school_id):
    """학교 정보 수정"""
    try:
        if current_user.role not in ['admin', 'super_admin']:
            return jsonify({'success': False, 'message': '접근 권한이 없습니다.'}), 403
            
        data = request.get_json()
        
        # 수정 가능한 필드만 추출
        update_data = {}
        allowed_fields = ['name', 'grade_count', 'address', 'phone', 'email', 'principal_name', 'website']
        
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        if not update_data:
            return jsonify({'success': False, 'message': '수정할 데이터가 없습니다.'}), 400
        
        result = supabase_service.update_school(school_id, update_data)
        if result:
            return jsonify({'success': True, 'message': '학교 정보가 성공적으로 수정되었습니다.'})
        else:
            return jsonify({'success': False, 'message': '학교 정보 수정에 실패했습니다.'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@dashboard_bp.route('/api/schools/<school_id>', methods=['DELETE'])
@login_required
def delete_school(school_id):
    """학교 삭제"""
    try:
        if current_user.role not in ['admin', 'super_admin']:
            return jsonify({'success': False, 'message': '접근 권한이 없습니다.'}), 403
            
        result = supabase_service.delete_school(school_id)
        if result:
            return jsonify({'success': True, 'message': '학교가 성공적으로 삭제되었습니다.'})
        else:
            return jsonify({'success': False, 'message': '학교 삭제에 실패했습니다.'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Teacher - 학급 관리 API
@dashboard_bp.route('/api/classes', methods=['GET'])
@login_required
def get_classes():
    """학급 목록 조회"""
    try:
        if current_user.role == 'student':
            return jsonify({'success': False, 'message': '접근 권한이 없습니다.'}), 403
            
        school_id = request.args.get('school_id')
        
        if current_user.role == 'teacher':
            # 담임 교사로 지정된 학급만 조회
            classes = supabase_service.get_classes_by_teacher(current_user.email)
        else:
            # admin, super_admin은 모든 학급 조회
            if school_id:
                classes = supabase_service.get_classes_by_school(school_id)
            else:
                classes = supabase_service.get_all_classes()
            
        return jsonify({'success': True, 'classes': classes})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@dashboard_bp.route('/api/classes', methods=['POST'])
@login_required
def create_class():
    """학급 생성"""
    try:
        if current_user.role not in ['admin', 'super_admin']:
            return jsonify({'success': False, 'message': '접근 권한이 없습니다.'}), 403
            
        data = request.get_json()
        
        required_fields = ['school_id', 'grade', 'class_number']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'{field}는 필수 항목입니다.'}), 400
        
        result = supabase_service.create_class(data)
        if result:
            return jsonify({'success': True, 'message': '학급이 성공적으로 생성되었습니다.'})
        else:
            return jsonify({'success': False, 'message': '학급 생성에 실패했습니다.'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@dashboard_bp.route('/api/classes/<class_id>', methods=['PUT'])
@login_required
def update_class(class_id):
    """학급 정보 수정"""
    try:
        if current_user.role not in ['admin', 'super_admin']:
            return jsonify({'success': False, 'message': '접근 권한이 없습니다.'}), 403
            
        data = request.get_json()
        
        # 수정 가능한 필드만 추출
        update_data = {}
        allowed_fields = ['class_name', 'teacher_email', 'room_number', 'max_students']
        
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        if not update_data:
            return jsonify({'success': False, 'message': '수정할 데이터가 없습니다.'}), 400
        
        result = supabase_service.update_class(class_id, update_data)
        if result:
            return jsonify({'success': True, 'message': '학급 정보가 성공적으로 수정되었습니다.'})
        else:
            return jsonify({'success': False, 'message': '학급 정보 수정에 실패했습니다.'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@dashboard_bp.route('/api/classes/<class_id>', methods=['DELETE'])
@login_required
def delete_class(class_id):
    """학급 삭제"""
    try:
        if current_user.role not in ['admin', 'super_admin']:
            return jsonify({'success': False, 'message': '접근 권한이 없습니다.'}), 403
            
        result = supabase_service.delete_class(class_id)
        if result:
            return jsonify({'success': True, 'message': '학급이 성공적으로 삭제되었습니다.'})
        else:
            return jsonify({'success': False, 'message': '학급 삭제에 실패했습니다.'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 현재 사용자 정보 API
@dashboard_bp.route('/api/current-user', methods=['GET'])
@login_required
def get_current_user():
    """현재 로그인한 사용자 정보 반환"""
    try:
        user_data = {
            'id': current_user.id,
            'email': current_user.email,
            'name': current_user.name,
            'role': current_user.role
        }
        return jsonify({'success': True, 'user': user_data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 학급 학생 관리 API
@dashboard_bp.route('/api/class-students/<class_id>', methods=['GET'])
@login_required
def get_class_students(class_id):
    """특정 학급의 학생 목록 조회"""
    try:
        if current_user.role == 'student':
            return jsonify({'success': False, 'message': '접근 권한이 없습니다.'}), 403
        
        # 교사는 자신의 담임 학급만 조회 가능
        if current_user.role == 'teacher':
            teacher_classes = supabase_service.get_classes_by_teacher(current_user.email)
            if not any(cls['id'] == class_id for cls in teacher_classes):
                return jsonify({'success': False, 'message': '해당 학급에 대한 권한이 없습니다.'}), 403
        
        students = supabase_service.get_class_students(class_id)
        return jsonify({'success': True, 'students': students})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@dashboard_bp.route('/api/enroll-student', methods=['POST'])
@login_required
def enroll_student():
    """학생을 학급에 등록"""
    try:
        if current_user.role == 'student':
            return jsonify({'success': False, 'message': '접근 권한이 없습니다.'}), 403
        
        data = request.get_json()
        student_email = data.get('student_email')
        class_id = data.get('class_id')
        
        if not student_email or not class_id:
            return jsonify({'success': False, 'message': '학생 이메일과 학급 ID는 필수입니다.'}), 400
        
        # 교사는 자신의 담임 학급에만 학생 추가 가능
        if current_user.role == 'teacher':
            teacher_classes = supabase_service.get_classes_by_teacher(current_user.email)
            if not any(cls['id'] == class_id for cls in teacher_classes):
                return jsonify({'success': False, 'message': '해당 학급에 대한 권한이 없습니다.'}), 403
        
        # 학생이 존재하는지 확인
        student_user = supabase_service.get_user_by_email(student_email)
        if not student_user:
            return jsonify({'success': False, 'message': '해당 이메일의 학생을 찾을 수 없습니다.'}), 404
        
        if student_user.get('role') != 'student':
            return jsonify({'success': False, 'message': '해당 사용자는 학생이 아닙니다.'}), 400
        
        result = supabase_service.enroll_student_to_class(student_email, class_id)
        if result:
            return jsonify({'success': True, 'message': '학생이 성공적으로 학급에 등록되었습니다.'})
        else:
            return jsonify({'success': False, 'message': '학생 등록에 실패했습니다.'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@dashboard_bp.route('/api/remove-student', methods=['POST'])
@login_required
def remove_student():
    """학생을 학급에서 제거"""
    try:
        if current_user.role == 'student':
            return jsonify({'success': False, 'message': '접근 권한이 없습니다.'}), 403
        
        data = request.get_json()
        student_email = data.get('student_email')
        class_id = data.get('class_id')
        
        if not student_email or not class_id:
            return jsonify({'success': False, 'message': '학생 이메일과 학급 ID는 필수입니다.'}), 400
        
        # 교사는 자신의 담임 학급에서만 학생 제거 가능
        if current_user.role == 'teacher':
            teacher_classes = supabase_service.get_classes_by_teacher(current_user.email)
            if not any(cls['id'] == class_id for cls in teacher_classes):
                return jsonify({'success': False, 'message': '해당 학급에 대한 권한이 없습니다.'}), 403
        
        result = supabase_service.remove_student_from_class(student_email, class_id)
        if result:
            return jsonify({'success': True, 'message': '학생이 성공적으로 학급에서 제거되었습니다.'})
        else:
            return jsonify({'success': False, 'message': '학생 제거에 실패했습니다.'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Student - 출석 체크 API
@dashboard_bp.route('/api/attendance', methods=['GET'])
@login_required
def get_attendance():
    """출석 기록 조회"""
    try:
        class_id = request.args.get('class_id')
        date = request.args.get('date')
        period = request.args.get('period')
        
        if current_user.role == 'student':
            # 학생은 자신의 출석 기록만 조회
            start_date = date
            end_date = date if date else None
            attendance = supabase_service.get_student_attendance(current_user.email, start_date, end_date)
        else:
            # 교사, 관리자는 담당 학급 또는 전체 출석 기록 조회
            # 교사는 자신의 담임 학급만 조회 가능 (권한 체크는 서비스 레이어에서)
            if current_user.role == 'teacher' and class_id:
                teacher_classes = supabase_service.get_classes_by_teacher(current_user.email)
                if not any(cls['id'] == class_id for cls in teacher_classes):
                    return jsonify({'success': False, 'message': '해당 학급에 대한 권한이 없습니다.'}), 403
            
            # 출석 기록 조회 파라미터 구성
            attendance = []
            if class_id and date:
                if period:
                    # 특정 교시의 출석 기록 조회
                    endpoint = f"attendance?class_id=eq.{class_id}&attendance_date=eq.{date}&period=eq.{period}&select=*"
                    attendance = supabase_service._make_request('GET', endpoint, use_service_role=True)
                else:
                    # 특정 날짜의 모든 교시 출석 기록 조회
                    endpoint = f"attendance?class_id=eq.{class_id}&attendance_date=eq.{date}&select=*&order=period"
                    attendance = supabase_service._make_request('GET', endpoint, use_service_role=True)
            elif class_id:
                # 특정 학급의 모든 출석 기록 조회
                attendance = supabase_service.get_attendance_records(class_id)
            
        return jsonify({'success': True, 'attendance': attendance or []})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@dashboard_bp.route('/api/attendance', methods=['POST'])
@login_required
def mark_attendance():
    """출석 체크"""
    try:
        data = request.get_json()
        
        required_fields = ['class_id', 'attendance_date', 'period', 'status']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'{field}는 필수 항목입니다.'}), 400
        
        if current_user.role == 'student':
            # 학생은 자신의 출석만 체크 가능
            data['student_email'] = current_user.email
        else:
            # 교사, 관리자는 학생 이메일이 필요
            if not data.get('student_email'):
                return jsonify({'success': False, 'message': '학생 이메일은 필수 항목입니다.'}), 400
            
            # 교사는 자신의 담임 학급 학생만 출석 체크 가능
            if current_user.role == 'teacher':
                teacher_classes = supabase_service.get_classes_by_teacher(current_user.email)
                if not any(cls['id'] == data['class_id'] for cls in teacher_classes):
                    return jsonify({'success': False, 'message': '해당 학급에 대한 권한이 없습니다.'}), 403
        
        # 중복 출석 체크 (UPSERT 방식으로 처리)
        existing_attendance = None
        try:
            endpoint = f"attendance?student_email=eq.{data['student_email']}&class_id=eq.{data['class_id']}&attendance_date=eq.{data['attendance_date']}&period=eq.{data['period']}&select=*"
            existing_records = supabase_service._make_request('GET', endpoint, use_service_role=True)
            if existing_records and len(existing_records) > 0:
                existing_attendance = existing_records[0]
        except Exception:
            pass
        
        if existing_attendance:
            # 기존 출석 기록 업데이트
            update_data = {
                'status': data['status'],
                'note': data.get('note', '')
            }
            result = supabase_service.update_attendance(existing_attendance['id'], update_data)
        else:
            # 새 출석 기록 생성
            result = supabase_service.mark_attendance(data)
        
        if result:
            return jsonify({'success': True, 'message': '출석이 성공적으로 기록되었습니다.'})
        else:
            return jsonify({'success': False, 'message': '출석 기록에 실패했습니다.'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@dashboard_bp.route('/api/student-classes', methods=['GET'])
@login_required
def get_student_classes():
    """학생이 속한 학급 목록 조회"""
    try:
        if current_user.role != 'student':
            return jsonify({'success': False, 'message': '학생만 접근 가능합니다.'}), 403
        
        classes = supabase_service.get_student_classes(current_user.email)
        return jsonify({'success': True, 'classes': classes})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500