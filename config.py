import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    
    # Google OAuth 설정
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    
    # 성능 최적화 설정
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1년 캐시
    TEMPLATES_AUTO_RELOAD = False
    
    # 역할 기반 접근 제어 설정
    ROLES = {
        'student': {
            'name': '학생',
            'permissions': ['view_student_dashboard', 'submit_assignments', 'view_grades']
        },
        'teacher': {
            'name': '교사',
            'permissions': ['view_teacher_dashboard', 'manage_assignments', 'grade_assignments', 'view_student_list']
        },
        'admin': {
            'name': '관리자',
            'permissions': ['view_admin_dashboard', 'manage_users', 'manage_system', 'view_all_data']
        },
        'super_admin': {
            'name': '최고관리자',
            'permissions': ['full_access']
        }
    }

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}