"""
Startup script for Code Review Assistant
This script helps users get started quickly
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    env_file = Path('.env')
    env_example = Path('env.example')
    
    if not env_file.exists() and env_example.exists():
        print("📝 Creating .env file from template...")
        with open(env_example, 'r') as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ .env file created successfully!")
        print("⚠️  Please edit .env file and add your OpenRouter API key")
        return True
    elif env_file.exists():
        print("✅ .env file already exists")
        return True
    else:
        print("❌ env.example file not found")
        return False

def check_api_key():
    """Check if API key is configured"""
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
            if 'your_openrouter_api_key_here' in content:
                print("⚠️  Please update your OpenRouter API key in .env file")
                return False
            else:
                print("✅ API key appears to be configured")
                return True
    return False

def main():
    """Main startup function"""
    print("🚀 Code Review Assistant - Startup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Create .env file
    if not create_env_file():
        return False
    
    # Check API key
    api_configured = check_api_key()
    
    print("\n📋 Next Steps:")
    if not api_configured:
        print("1. Edit .env file and add your OpenRouter API key")
        print("2. Get your API key from: https://openrouter.ai/")
        print("3. Run: streamlit run app.py")
    else:
        print("1. Run: streamlit run app.py")
        print("2. Open your browser to: http://localhost:8501")
    
    print("\n🎉 Setup complete! Happy code reviewing!")
    return True

if __name__ == "__main__":
    main()

