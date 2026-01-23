#!/usr/bin/env python3
"""
Test the integrated system
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint"""
    print("\n1. Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health/live")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    return response.status_code == 200


def test_vault_connection():
    """Test Vault connection"""
    print("\n2. Testing Vault connection...")
    response = requests.get(f"{BASE_URL}/api/v1/debug/vault-test")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_login():
    """Test login endpoint"""
    print("\n3. Testing login...")
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        params={"username": "test_user", "password": "test_pass"},
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Got token: {data['access_token'][:20]}...")
        return data["access_token"]
    else:
        print(f"   Error: {response.text}")
        return None


def test_protected_endpoint(token):
    """Test protected endpoint"""
    print("\n4. Testing protected endpoint...")
    response = requests.get(
        f"{BASE_URL}/api/v1/profile", headers={"Authorization": f"Bearer {token}"}
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_credit_check(token):
    """Test credit check"""
    print("\n5. Testing credit check...")
    response = requests.post(
        f"{BASE_URL}/api/v1/credit/check",
        headers={"Authorization": f"Bearer {token}"},
        params={"applicant_id": "APP123", "amount": 50000.0, "term_months": 60},
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_unauthorized_access():
    """Test that unauthorized access is blocked"""
    print("\n6. Testing unauthorized access (should fail)...")
    response = requests.post(
        f"{BASE_URL}/api/v1/credit/check",
        params={"applicant_id": "APP123", "amount": 50000.0, "term_months": 60},
    )
    print(f"   Status: {response.status_code}")
    print(f"   Expected: 401 (Unauthorized)")
    return response.status_code == 401


def test_metrics():
    """Test metrics endpoint"""
    print("\n7. Testing metrics endpoint...")
    response = requests.get(f"{BASE_URL}/metrics")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        lines = response.text.split("\n")
        galani_metrics = [
            l for l in lines if "galani" in l.lower() and not l.startswith("#")
        ]
        print(f"   Found {len(galani_metrics)} Galani metrics")
        for metric in galani_metrics[:5]:
            print(f"   - {metric}")
    return response.status_code == 200


def main():
    """Run all tests"""
    print("=" * 80)
    print("🧪 GALANI INTEGRATION TESTS")
    print("=" * 80)

    results = []

    # Test health
    results.append(("Health Check", test_health()))

    # Test Vault
    results.append(("Vault Connection", test_vault_connection()))

    # Test login
    token = test_login()
    results.append(("Login", token is not None))

    if token:
        # Test protected endpoints
        results.append(("Protected Endpoint", test_protected_endpoint(token)))
        results.append(("Credit Check", test_credit_check(token)))

    # Test security
    results.append(("Unauthorized Access Blocked", test_unauthorized_access()))

    # Test metrics
    results.append(("Metrics Endpoint", test_metrics()))

    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 80)

    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
