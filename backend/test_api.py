"""Simple test script for the SafePay API."""
import requests
import json
from datetime import datetime

API_BASE = "http://localhost:8000/api/v1"

def test_health():
    """Test health endpoint."""
    print("Testing health endpoint...")
    response = requests.get(f"{API_BASE}/health/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

def test_prediction():
    """Test fraud prediction."""
    print("Testing fraud prediction...")
    
    transaction = {
        "user_id": "user_123",
        "card_id": "card_456",
        "amount": 150.50,
        "currency": "USD",
        "merchant_id": "merchant_789",
        "merchant_category": "electronics",
        "transaction_type": "purchase",
        "location_country": "US",
        "location_city": "New York",
        "ip_address": "192.168.1.1",
        "device_id": "device_abc",
        "threshold": 0.5,
        "include_explainability": True
    }
    
    response = requests.post(f"{API_BASE}/predictions/", json=transaction)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Transaction ID: {result['transaction_id']}")
        print(f"Fraud Probability: {result['fraud_probability']:.4f}")
        print(f"Is Fraud: {result['is_fraud']}")
        print(f"Inference Time: {result['inference_time_ms']:.2f} ms")
        if result.get('explainability'):
            print(f"Explainability: Available")
        return result['transaction_id']
    else:
        print(f"Error: {response.text}")
        return None

def test_transactions(transaction_id=None):
    """Test transactions endpoint."""
    print("\nTesting transactions endpoint...")
    
    # Get all transactions
    response = requests.get(f"{API_BASE}/transactions/?limit=10")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        transactions = response.json()
        print(f"Retrieved {len(transactions)} transactions")
    
    # Get specific transaction
    if transaction_id:
        response = requests.get(f"{API_BASE}/transactions/{transaction_id}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Transaction details retrieved")

def test_analytics():
    """Test analytics endpoints."""
    print("\nTesting analytics endpoints...")
    
    # Get stats
    response = requests.get(f"{API_BASE}/analytics/stats?hours=24")
    print(f"Stats Status: {response.status_code}")
    if response.status_code == 200:
        stats = response.json()
        print(f"Total Transactions: {stats['total_transactions']}")
        print(f"Fraud Rate: {stats['fraud_rate']*100:.2f}%")
    
    # Get model metrics
    response = requests.get(f"{API_BASE}/analytics/model-metrics")
    print(f"Metrics Status: {response.status_code}")
    if response.status_code == 200:
        metrics = response.json()
        print(f"Total Predictions: {metrics['total_predictions']}")
        print(f"Avg Inference Time: {metrics['avg_inference_time_ms']:.2f} ms")

if __name__ == "__main__":
    print("=" * 50)
    print("SafePay API Test Script")
    print("=" * 50)
    
    try:
        test_health()
        transaction_id = test_prediction()
        test_transactions(transaction_id)
        test_analytics()
        print("\n" + "=" * 50)
        print("All tests completed!")
        print("=" * 50)
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to API. Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"Error: {e}")

