import pytest
from app import create_app  # Replace with your app factory or app import
from app.extensions import db
from app.models import AppUser

@pytest.fixture
def app():
    # Create the Flask app instance
    app = create_app()  # If you use a factory function
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def app_context(app):
    # Set up the application context and yield control to the test
    with app.app_context():
        yield

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def test_user(app):
    with app.app_context():
        user = AppUser(username="testuser", email="test@example.com")
        db.session.add(user)
        db.session.commit()
        return user