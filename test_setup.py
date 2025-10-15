"""
Test script for Code Review Assistant
Verifies that all components are working correctly
"""

import os
import sys
from datetime import datetime

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import requests
        print("✅ Requests imported successfully")
    except ImportError as e:
        print(f"❌ Requests import failed: {e}")
        return False
    
    try:
        import reportlab
        print("✅ ReportLab imported successfully")
    except ImportError as e:
        print(f"❌ ReportLab import failed: {e}")
        return False
    
    try:
        import markdown
        print("✅ Markdown imported successfully")
    except ImportError as e:
        print(f"❌ Markdown import failed: {e}")
        return False
    
    try:
        import sqlite3
        print("✅ SQLite3 imported successfully")
    except ImportError as e:
        print(f"❌ SQLite3 import failed: {e}")
        return False
    
    return True

def test_directories():
    """Test that required directories exist or can be created"""
    print("\n📁 Testing directories...")
    
    directories = ['services', 'db', 'reports']
    
    for directory in directories:
        if os.path.exists(directory):
            print(f"✅ Directory '{directory}' exists")
        else:
            try:
                os.makedirs(directory)
                print(f"✅ Directory '{directory}' created successfully")
            except Exception as e:
                print(f"❌ Failed to create directory '{directory}': {e}")
                return False
    
    return True

def test_services():
    """Test that service modules can be imported"""
    print("\n🔧 Testing services...")
    
    try:
        from services.llm_client import CodeReviewLLM
        print("✅ LLM Client service imported successfully")
    except ImportError as e:
        print(f"❌ LLM Client import failed: {e}")
        return False
    
    try:
        from services.pdf_generator import PDFGenerator
        print("✅ PDF Generator service imported successfully")
    except ImportError as e:
        print(f"❌ PDF Generator import failed: {e}")
        return False
    
    try:
        from db.database import DatabaseManager
        print("✅ Database Manager imported successfully")
    except ImportError as e:
        print(f"❌ Database Manager import failed: {e}")
        return False
    
    return True

def test_database():
    """Test database initialization"""
    print("\n💾 Testing database...")
    
    try:
        from db.database import DatabaseManager
        db_manager = DatabaseManager("db/test_reviews.db")
        print("✅ Database initialized successfully")
        
        # Test basic operations
        stats = db_manager.get_database_stats()
        print(f"✅ Database stats retrieved: {stats}")
        
        # Clean up test database
        if os.path.exists("db/test_reviews.db"):
            os.remove("db/test_reviews.db")
            print("✅ Test database cleaned up")
        
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_pdf_generator():
    """Test PDF generator initialization"""
    print("\n📄 Testing PDF generator...")
    
    try:
        from services.pdf_generator import PDFGenerator
        pdf_gen = PDFGenerator("reports/test")
        print("✅ PDF Generator initialized successfully")
        
        # Test report info method
        info = pdf_gen.get_report_info("nonexistent.pdf")
        print(f"✅ PDF Generator methods working: {info}")
        
        return True
    except Exception as e:
        print(f"❌ PDF Generator test failed: {e}")
        return False

def test_environment():
    """Test environment configuration"""
    print("\n🌍 Testing environment...")
    
    # Check if .env file exists
    if os.path.exists('.env'):
        print("✅ .env file exists")
    else:
        print("⚠️  .env file not found - please copy env.example to .env")
    
    # Check if env.example exists
    if os.path.exists('env.example'):
        print("✅ env.example file exists")
    else:
        print("❌ env.example file missing")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Code Review Assistant - Setup Test")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Directory Test", test_directories),
        ("Services Test", test_services),
        ("Database Test", test_database),
        ("PDF Generator Test", test_pdf_generator),
        ("Environment Test", test_environment),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        print("\n📝 Next steps:")
        print("1. Copy env.example to .env")
        print("2. Add your OpenRouter API key to .env")
        print("3. Run: streamlit run app.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("1. Install missing dependencies: pip install -r requirements.txt")
        print("2. Check file permissions")
        print("3. Ensure Python version is 3.8+")

if __name__ == "__main__":
    main()

