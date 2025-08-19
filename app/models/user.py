from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    """사용자 모델"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='student')
    
    # 프로필 정보
    profile_image = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    department = db.Column(db.String(100))
    student_id = db.Column(db.String(50))  # 학번 (학생용)
    employee_id = db.Column(db.String(50))  # 직원번호 (교직원용)
    
    # 시스템 정보
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)
    
    # 권한 확인 메서드
    def has_permission(self, permission):
        """사용자가 특정 권한을 가지고 있는지 확인"""
        from config import Config
        role_permissions = Config.ROLES.get(self.role, {}).get('permissions', [])
        return permission in role_permissions or 'full_access' in role_permissions
    
    def has_role(self, role):
        """사용자가 특정 역할을 가지고 있는지 확인"""
        return self.role == role
    
    def get_role_name(self):
        """역할 이름 반환"""
        from config import Config
        return Config.ROLES.get(self.role, {}).get('name', self.role)
    
    def is_student(self):
        return self.role == 'student'
    
    def is_teacher(self):
        return self.role == 'teacher'
    
    def is_admin(self):
        return self.role in ['admin', 'super_admin']
    
    def update_last_login(self):
        """마지막 로그인 시간 업데이트"""
        self.last_login = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    @staticmethod
    def create_or_update_from_google(google_user_info, role='student'):
        """Google OAuth 정보로부터 사용자 생성 또는 업데이트 (기존 메서드 유지)"""
        user = User.query.filter_by(google_id=google_user_info['sub']).first()
        
        if user:
            # 기존 사용자 정보 업데이트
            user.email = google_user_info.get('email')
            user.name = google_user_info.get('name')
            user.profile_image = google_user_info.get('picture')
            user.updated_at = datetime.utcnow()
        else:
            # 새 사용자 생성
            user = User(
                google_id=google_user_info['sub'],
                email=google_user_info.get('email'),
                name=google_user_info.get('name'),
                profile_image=google_user_info.get('picture'),
                role=role
            )
            db.session.add(user)
        
        db.session.commit()
        return user
    
    @staticmethod
    def create_or_update_from_supabase(supabase_user):
        """Supabase 사용자 정보로부터 Flask-Login용 사용자 생성/업데이트"""
        user = User.query.filter_by(google_id=supabase_user['google_id']).first()
        
        if user:
            # 기존 사용자 정보 업데이트
            user.email = supabase_user.get('email')
            user.name = supabase_user.get('name')
            user.profile_image = supabase_user.get('profile_image')
            user.role = supabase_user.get('role')
            user.is_active = supabase_user.get('is_active', True)
            user.updated_at = datetime.utcnow()
        else:
            # 새 사용자 생성
            user = User(
                google_id=supabase_user['google_id'],
                email=supabase_user.get('email'),
                name=supabase_user.get('name'),
                profile_image=supabase_user.get('profile_image'),
                role=supabase_user.get('role'),
                is_active=supabase_user.get('is_active', True)
            )
            db.session.add(user)
        
        # 프로필 정보 추가
        if supabase_user.get('profile'):
            user.profile_data = supabase_user['profile']
        
        db.session.commit()
        return user