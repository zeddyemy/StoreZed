import pytest
from unittest.mock import patch
from app.utils.payments.processor.flutterwave import FlutterwaveProcessor
from app.utils.payments.types import PaymentProcessorResponse

# Fixture to create a processor instance for each test
@pytest.fixture
def flutterwave_processor():
    return FlutterwaveProcessor(secret_key="test_secret")

# Test successful payment initialization
@patch("requests.post")  # Mock the API call
def test_initialize_payment_success(mock_post, flutterwave_processor, app_context):
    # Simulate a successful API response
    mock_response = {
        "status": "success",
        "message": "Payment initiated",
        "data": {"reference": "flw_12345", "link": "https://flutterwave.com/pay/12345"}
    }
    mock_post.return_value.json.return_value = mock_response
    mock_post.return_value.status_code = 200

    # Call the method
    response = flutterwave_processor.initialize_payment(
        amount=100.0,
        currency="NGN",
        customer_data={"email": "test@example.com", "name": "Test User"}
    )
    
    print(type(response))  # Should print <class 'dict'> if it’s a dictionary
    print(response)

    # Check the results
    assert response["status"] == "success"
    assert response["message"] == "Payment initiated"
    assert response["payment_id"] == "flw_12345"
    assert response["authorization_url"] == "https://flutterwave.com/pay/12345"

# Test failed payment initialization
@patch("requests.post")
def test_initialize_payment_failure(mock_post, flutterwave_processor, app_context):
    # Simulate an error response
    mock_post.return_value.json.return_value = {
        "status": "error",
        "message": "Invalid currency"
    }
    mock_post.return_value.status_code = 400

    # Call the method
    response = flutterwave_processor.initialize_payment(
        amount=100.0,
        currency="INVALID",
        customer_data={"email": "test@example.com", "name": "Test User"}
    )

    # Check the results
    assert response["status"] == "error"
    assert response["message"] == "Invalid currency"
    assert response["payment_id"] is None
    assert response["authorization_url"] is None


def test_flutterwave_supports_currency(flutterwave_processor):
    assert flutterwave_processor.supports_currency("NGN") is True
    assert flutterwave_processor.supports_currency("USD") is True
    assert flutterwave_processor.supports_currency("EUR") is True
    assert flutterwave_processor.supports_currency("CAD") is False

