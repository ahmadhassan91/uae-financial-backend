#!/usr/bin/env python3
"""
Test script for guest survey functionality
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_guest_survey():
    """Test the guest survey submission endpoint"""
    
    # Sample survey responses
    survey_data = {
        "responses": {
            "Q1": 3,
            "Q2": 4,
            "Q3": 2,
            "Q4": 5,
            "Q5": 3
        },
        "completion_time": 120
    }
    
    print("Testing guest survey submission...")
    try:
        response = requests.post(f"{BASE_URL}/surveys/submit-guest", json=survey_data)
        if response.status_code == 201:
            print("✓ Guest survey submission successful")
            result = response.json()
            print(f"  Overall Score: {result['score_breakdown']['overall_score']}")
            print(f"  Risk Tolerance: {result['score_breakdown']['risk_tolerance']}")
            print(f"  Recommendations: {len(result['recommendations'])} items")
            return result
        else:
            print(f"✗ Guest survey submission failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"✗ Guest survey error: {e}")
        return None

if __name__ == "__main__":
    print("Testing Guest Survey System")
    print("=" * 30)
    
    result = test_guest_survey()
    
    print("\n" + "=" * 30)
    print("Guest survey tests completed!")