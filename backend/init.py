#!/usr/bin/env python3
"""
FermTrack - Fermentation Tracking System - Backend Initialization Script
Copyright (C) 2026 FermTrack Contributors

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

FermTrack Backend Initialization Script

This script helps set up the FermTrack backend environment.
"""

import os
import sys
import subprocess
import secrets

def generate_secret_key():
    """Generate a secure random secret key"""
    return secrets.token_urlsafe(32)

def create_env_file():
    """Create .env file from template with generated secrets"""
    env_example = '.env.example'
    env_file = '.env'
    
    if os.path.exists(env_file):
        print(f"✅ {env_file} already exists")
        return
    
    if not os.path.exists(env_example):
        print(f"❌ {env_example} template not found")
        return
    
    # Read template
    with open(env_example, 'r') as f:
        content = f.read()
    
    # Replace placeholder values with generated secrets
    content = content.replace('your-secret-key-change-in-production', generate_secret_key())
    content = content.replace('your-jwt-secret-key-change-in-production', generate_secret_key())
    
    # Write .env file
    with open(env_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Created {env_file} with secure random keys")

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def create_virtual_environment():
    """Create virtual environment if it doesn't exist"""
    venv_path = 'venv'
    
    if os.path.exists(venv_path):
        print(f"✅ Virtual environment already exists at {venv_path}")
        return True
    
    try:
        subprocess.run([sys.executable, '-m', 'venv', venv_path], check=True)
        print(f"✅ Created virtual environment at {venv_path}")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to create virtual environment")
        return False

def install_dependencies():
    """Install Python dependencies"""
    venv_python = os.path.join('venv', 'bin', 'python') if os.name != 'nt' else os.path.join('venv', 'Scripts', 'python.exe')
    
    if not os.path.exists(venv_python):
        print("❌ Virtual environment Python not found. Please activate venv manually.")
        return False
    
    try:
        subprocess.run([venv_python, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def initialize_database():
    """Initialize the database"""
    venv_python = os.path.join('venv', 'bin', 'python') if os.name != 'nt' else os.path.join('venv', 'Scripts', 'python.exe')
    
    if not os.path.exists(venv_python):
        print("❌ Virtual environment Python not found.")
        return False
    
    try:
        # Run the app briefly to create database tables
        env = os.environ.copy()
        env['FLASK_ENV'] = 'development'
        result = subprocess.run([venv_python, '-c', '''
import sys
sys.path.insert(0, ".")
from app import create_app
app = create_app()
with app.app_context():
    print("Database initialized successfully")
'''], check=True, capture_output=True, text=True, env=env)
        print("✅ Database initialized successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to initialize database: {e.stderr}")
        return False

def print_next_steps():
    """Print instructions for next steps"""
    activate_cmd = 'source venv/bin/activate' if os.name != 'nt' else 'venv\\Scripts\\activate'
    
    print("\n" + "="*60)
    print("🎉 FermTrack Backend Setup Complete!")
    print("="*60)
    print("\nNext steps:")
    print(f"1. Activate the virtual environment:")
    print(f"   {activate_cmd}")
    print("\n2. Start the development server:")
    print("   python app.py")
    print("\n3. The API will be available at:")
    print("   http://localhost:5000")
    print("\n4. Default admin credentials:")
    print("   Username: admin")
    print("   Password: admin123")
    print("   ⚠️  Change these in production!")
    print("\n5. API documentation:")
    print("   See README.md for detailed endpoint information")
    print("\n" + "="*60)

def main():
    """Main initialization function"""
    print("🚀 Initializing FermTrack Backend...")
    print()
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Create .env file
    create_env_file()
    
    # Create virtual environment
    if not create_virtual_environment():
        return 1
    
    # Install dependencies
    if not install_dependencies():
        return 1
    
    # Initialize database
    if not initialize_database():
        return 1
    
    # Print success message and next steps
    print_next_steps()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())