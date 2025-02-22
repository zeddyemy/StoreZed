import pytest
from app import create_app  # Replace with your app factory or app import

@pytest.fixture
def app():
    # Create the Flask app instance
    app = create_app()  # If you use a factory function
    # Alternatively, if your app is a module-level variable:
    # from app import app
    return app

@pytest.fixture
def app_context(app):
    # Set up the application context and yield control to the test
    with app.app_context():
        yield