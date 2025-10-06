#!/usr/bin/env python3
"""
Quick Localization Backend Test Runner

This script provides a quick way to test the localization backend components
that have been implemented based on the advanced-survey-features spec.
"""

import os
import sys
import requests
import json
from datetime import datetime

def test_backend_health():
    """Test if the backend is running"""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        return response.status_code == 200
    except:
        return False

def test_localization_endpoints():
    """Test localization API endpoints"""
    base_url = "http://localhost:8000"
    results = []
    
    # Test public endpoints (no auth required)
    public_endpoints = [
        "/api/localization/languages",
        "/api/localization/questions/en",
        "/api/localization/questions/ar",
        "/api/localization/ui/en",
        "/api/localization/ui/ar"
    ]
    
    for endpoint in public_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                results.append(f"✓ PASS {endpoint} - Status: {response.status_code}")
            elif response.status_code in [401, 403]:
                results.append(f"⚠ AUTH {endpoint} - Status: {response.status_code} (requires auth)")
            else:
                results.append(f"✗ FAIL {endpoint} - Status: {response.status_code}")
        except Exception as e:
            results.append(f"✗ FAIL {endpoint} - Error: {str(e)}")
    
    # Test admin endpoints (expect 401/403 without auth)
    admin_endpoints = [
        "/api/localization/content",
        "/api/admin/localization/content",
        "/api/admin/localization/translations"
    ]
    
    for endpoint in admin_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code in [401, 403]:
                results.append(f"✓ PASS {endpoint} - Status: {response.status_code} (auth required)")
            elif response.status_code == 200:
                results.append(f"⚠ WARN {endpoint} - Status: {response.status_code} (no auth required)")
            else:
                results.append(f"✗ FAIL {endpoint} - Status: {response.status_code}")
        except Exception as e:
            results.append(f"✗ FAIL {endpoint} - Error: {str(e)}")
    
    return results

def test_database_tables():
    """Test if localization database tables exist"""
    try:
        # Import after adding to path
        sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
        from app.database import engine
        from sqlalchemy import text
        
        results = []
        tables = ['localized_content', 'question_variations', 'demographic_rules']
        
        with engine.connect() as conn:
            for table in tables:
                try:
                    result = conn.execute(text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"))
                    if result.fetchone():
                        results.append(f"✓ PASS Table '{table}' exists")
                    else:
                        results.append(f"✗ FAIL Table '{table}' missing")
                except Exception as e:
                    results.append(f"✗ FAIL Table '{table}' - Error: {str(e)}")
        
        return results
    except Exception as e:
        return [f"✗ FAIL Database connection - Error: {str(e)}"]

def test_localization_service():
    """Test localization service functionality"""
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
        from app.localization.service import LocalizationService
        from app.database import SessionLocal
        
        results = []
        
        # Test service initialization with database session
        db = SessionLocal()
        try:
            service = LocalizationService(db)
            results.append("✓ PASS LocalizationService initialized")
            
            # Test supported languages
            try:
                import asyncio
                languages = asyncio.run(service.get_supported_languages())
                if languages and len(languages) >= 2:
                    results.append(f"✓ PASS Supported languages - {len(languages)} languages")
                else:
                    results.append("⚠ WARN Supported languages - Limited language support")
            except Exception as e:
                results.append(f"⚠ WARN Supported languages - {str(e)}")
            
            # Test content validation
            try:
                validation = asyncio.run(service.validate_content(
                    "test", "test_key", "ar", "مرحباً بك"
                ))
                if validation.get("is_valid"):
                    results.append("✓ PASS Content validation")
                else:
                    results.append("⚠ WARN Content validation - Validation issues found")
            except Exception as e:
                results.append(f"⚠ WARN Content validation - {str(e)}")
                
        finally:
            db.close()
        
        return results
    except Exception as e:
        return [f"✗ FAIL LocalizationService - Error: {str(e)}"]

def test_arabic_pdf_service():
    """Test Arabic PDF generation service"""
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
        from app.reports.arabic_pdf_service import ArabicPDFReportService, ArabicBrandingConfig
        
        results = []
        pdf_service = ArabicPDFReportService()
        results.append("✓ PASS ArabicPDFReportService initialized")
        
        # Test branding config
        branding = ArabicBrandingConfig()
        results.append("✓ PASS ArabicBrandingConfig initialized")
        
        # Test Arabic text processing
        try:
            arabic_text = "مرحباً بك في تقرير الصحة المالية"
            processed_text = pdf_service._process_arabic_text(arabic_text)
            if processed_text:
                results.append("✓ PASS Arabic text processing")
            else:
                results.append("✗ FAIL Arabic text processing - Empty result")
        except Exception as e:
            results.append(f"⚠ WARN Arabic text processing - {str(e)}")
        
        # Test font registration
        try:
            pdf_service._register_fonts()
            results.append(f"✓ PASS Font registration - Using: {pdf_service.arabic_font}")
        except Exception as e:
            results.append(f"⚠ WARN Font registration - {str(e)}")
        
        return results
    except Exception as e:
        return [f"✗ FAIL ArabicPDFReportService - Error: {str(e)}"]

def main():
    """Run quick localization tests"""
    print("🚀 Quick Localization Backend Tests")
    print("=" * 50)
    
    # Test backend health
    print("\n📡 Backend Health Check:")
    if test_backend_health():
        print("✓ PASS Backend is running on http://localhost:8000")
    else:
        print("✗ FAIL Backend is not running - Start with: uvicorn app.main:app --reload")
        print("⚠ Some tests will be skipped")
    
    # Test database tables
    print("\n🗄️  Database Tables:")
    for result in test_database_tables():
        print(f"  {result}")
    
    # Test localization service
    print("\n🌐 Localization Service:")
    for result in test_localization_service():
        print(f"  {result}")
    
    # Test Arabic PDF service
    print("\n📄 Arabic PDF Service:")
    for result in test_arabic_pdf_service():
        print(f"  {result}")
    
    # Test API endpoints (only if backend is running)
    if test_backend_health():
        print("\n🔗 API Endpoints:")
        for result in test_localization_endpoints():
            print(f"  {result}")
    
    print("\n" + "=" * 50)
    print("✅ Quick test completed!")
    print("💡 For comprehensive testing, run: python test_complete_localization_backend.py")

if __name__ == "__main__":
    main()