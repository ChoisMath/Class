"""
Test configuration and fixtures
"""
import os
import pytest
import tempfile
from app import create_app, db
from app.models.user import User


@pytest.fixture(scope='session')
def app():
    """Create application for the tests."""
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp()
    
    # Override environment variables for testing
    os.environ['TESTING'] = 'True'
    os.environ['SECRET_KEY'] = 'test-secret-key'
    os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'
    os.environ['SUPABASE_URL'] = 'https://test.supabase.co'
    os.environ['SUPABASE_KEY'] = 'test-key'
    os.environ['GOOGLE_CLIENT_ID'] = 'test-client-id'
    os.environ['GOOGLE_CLIENT_SECRET'] = 'test-client-secret'
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['MAIL_SUPPRESS_SEND'] = True
    
    with app.app_context():
        try:
            db.create_all()
            yield app
        finally:
            db.session.remove()
            db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test runner for the app's CLI commands."""
    return app.test_cli_runner()


@pytest.fixture
def auth_headers():
    """Create headers for authenticated requests."""
    return {
        'Authorization': 'Bearer test-token',
        'Content-Type': 'application/json'
    }


@pytest.fixture
def sample_user(app):
    """Create a sample user for testing."""
    with app.app_context():
        user = User(
            email='test@example.com',
            name='Test User',
            role='student',
            is_active=True
        )
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def sample_admin(app):
    """Create a sample admin user for testing."""
    with app.app_context():
        admin = User(
            email='admin@example.com',
            name='Admin User',
            role='admin',
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        return admin


@pytest.fixture
def sample_teacher(app):
    """Create a sample teacher user for testing."""
    with app.app_context():
        teacher = User(
            email='teacher@example.com',
            name='Teacher User',
            role='teacher',
            is_active=True
        )
        db.session.add(teacher)
        db.session.commit()
        return teacher


@pytest.fixture
def authenticated_client(client, sample_user):
    """Create an authenticated client."""
    with client.session_transaction() as sess:
        sess['_user_id'] = sample_user.id
        sess['_fresh'] = True
    return client


@pytest.fixture
def admin_client(client, sample_admin):
    """Create an authenticated admin client."""
    with client.session_transaction() as sess:
        sess['_user_id'] = sample_admin.id
        sess['_fresh'] = True
    return client


@pytest.fixture
def teacher_client(client, sample_teacher):
    """Create an authenticated teacher client."""
    with client.session_transaction() as sess:
        sess['_user_id'] = sample_teacher.id
        sess['_fresh'] = True
    return client


@pytest.fixture
def mock_supabase_service(mocker):
    """Mock the Supabase service for testing."""
    mock_service = mocker.Mock()
    mock_service.get_all_users.return_value = []
    mock_service.get_schools.return_value = []
    mock_service.get_all_classes.return_value = []
    mock_service.get_seat_arrangements.return_value = []
    mock_service.get_attendance_records_by_period.return_value = []
    return mock_service