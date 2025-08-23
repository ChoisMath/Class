from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
import os

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # Configuration
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')
    
    from config import config
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '로그인이 필요합니다.'
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))
    
    # Register Blueprints
    from app.blueprints.auth import auth_bp
    from app.blueprints.student import student_bp
    from app.blueprints.teacher import teacher_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.dashboard import dashboard_bp
    from app.blueprints.seating import seating_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(teacher_bp, url_prefix='/teacher')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(seating_bp, url_prefix='/seating')
    
    # Main routes
    from app.blueprints.main import main_bp
    app.register_blueprint(main_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        from flask import render_template
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(403)
    def forbidden(error):
        from flask import render_template
        return render_template('errors/403.html'), 403
    
    # Performance optimizations
    @app.after_request
    def after_request(response):
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Cache static files
        if request.endpoint and request.endpoint.startswith('static'):
            response.cache_control.max_age = 31536000  # 1 year
        
        return response
    
    return app