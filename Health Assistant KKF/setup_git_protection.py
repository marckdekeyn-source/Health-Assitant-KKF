#!/usr/bin/env python3
"""
Git Protection Setup Script
Automatically setup .gitignore dan protect sensitive files
"""
import os
import sys
import json
import shutil
from pathlib import Path


class GitProtectionSetup:
    """Setup Git protection untuk Health Assistant"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.config_dir = self.project_root / "config"
        self.config_file = self.config_dir / "config.json"
        self.config_example = self.config_dir / "config.example.json"
        self.gitignore_file = self.project_root / ".gitignore"
        
    def print_header(self):
        """Print header"""
        print("\n" + "="*60)
        print("🔒 GIT PROTECTION SETUP - Health Assistant")
        print("="*60 + "\n")
    
    def check_git_initialized(self):
        """Check if Git is initialized"""
        git_dir = self.project_root / ".git"
        if git_dir.exists():
            print("✓ Git repository detected")
            return True
        else:
            print("⚠️  Git not initialized yet")
            print("   Run: git init")
            return False
    
    def create_gitignore(self):
        """Create .gitignore file"""
        print("\n📝 Creating .gitignore...")
        
        gitignore_content = """# ========================================
# HEALTH ASSISTANT - .gitignore
# ========================================

# CRITICAL: Sensitive config
config/config.json

# Personal data
logs/
logs/*.csv
logs/*.txt
logs/*.log

# Python cache
__pycache__/
*.py[cod]
*.pyc
*.pyo

# Virtual environment
venv/
env/
.venv

# IDE files
.vscode/
.idea/
*.swp
*.swo

# OS files
.DS_Store
Thumbs.db
desktop.ini

# Audio files (optional - large)
sounds/*.wav
sounds/*.mp3

# Backup files
*.bak
*.old
*.backup

# Environment variables
.env
.env.local
"""
        
        try:
            with open(self.gitignore_file, 'w', encoding='utf-8') as f:
                f.write(gitignore_content)
            print(f"✓ Created: {self.gitignore_file}")
            return True
        except Exception as e:
            print(f"✗ Failed to create .gitignore: {e}")
            return False
    
    def create_config_example(self):
        """Create config.example.json from config.json"""
        print("\n📝 Creating config.example.json...")
        
        if not self.config_file.exists():
            print(f"⚠️  config.json not found at {self.config_file}")
            return False
        
        try:
            # Read existing config
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Replace sensitive data with placeholders
            if 'telegram' in config:
                config['telegram']['bot_token'] = "PASTE_YOUR_BOT_TOKEN_HERE"
                config['telegram']['chat_id'] = "PASTE_YOUR_CHAT_ID_HERE"
            
            # Write example config
            with open(self.config_example, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            print(f"✓ Created: {self.config_example}")
            return True
        except Exception as e:
            print(f"✗ Failed to create config.example.json: {e}")
            return False
    
    def create_gitkeep_files(self):
        """Create .gitkeep files in empty directories"""
        print("\n📝 Creating .gitkeep files...")
        
        dirs_to_keep = ['logs', 'sounds']
        created = 0
        
        for dirname in dirs_to_keep:
            dir_path = self.project_root / dirname
            gitkeep_file = dir_path / ".gitkeep"
            
            if dir_path.exists():
                try:
                    gitkeep_file.touch()
                    print(f"✓ Created: {gitkeep_file}")
                    created += 1
                except Exception as e:
                    print(f"✗ Failed to create {gitkeep_file}: {e}")
            else:
                print(f"⚠️  Directory not found: {dir_path}")
        
        return created > 0
    
    def verify_protection(self):
        """Verify that sensitive files are protected"""
        print("\n🔍 Verifying protection...")
        
        issues = []
        
        # Check .gitignore exists
        if not self.gitignore_file.exists():
            issues.append("✗ .gitignore not found!")
        else:
            print("✓ .gitignore exists")
        
        # Check config.example.json exists
        if not self.config_example.exists():
            issues.append("✗ config.example.json not found!")
        else:
            print("✓ config.example.json exists")
        
        # Check if config.json has real tokens
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    token = config.get('telegram', {}).get('bot_token', '')
                    
                    if token and token != "PASTE_YOUR_BOT_TOKEN_HERE":
                        print("✓ config.json has real token (good for local)")
                    else:
                        print("⚠️  config.json has placeholder token")
            except:
                print("⚠️  Could not read config.json")
        
        # Check if config.example.json has placeholders
        if self.config_example.exists():
            try:
                with open(self.config_example, 'r') as f:
                    config = json.load(f)
                    token = config.get('telegram', {}).get('bot_token', '')
                    
                    if token == "PASTE_YOUR_BOT_TOKEN_HERE":
                        print("✓ config.example.json has placeholders (safe for Git)")
                    else:
                        issues.append("✗ config.example.json has real token!")
            except:
                print("⚠️  Could not read config.example.json")
        
        return issues
    
    def test_git_ignore(self):
        """Test if Git will ignore sensitive files"""
        print("\n🧪 Testing Git ignore rules...")
        
        if not shutil.which('git'):
            print("⚠️  Git command not found. Install Git first.")
            return False
        
        try:
            import subprocess
            
            # Check if config.json is ignored
            result = subprocess.run(
                ['git', 'check-ignore', 'config/config.json'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✓ config/config.json will be ignored by Git")
                return True
            else:
                print("✗ WARNING: config/config.json will NOT be ignored!")
                print("  Check your .gitignore file!")
                return False
        except Exception as e:
            print(f"⚠️  Could not test Git ignore: {e}")
            return False
    
    def show_next_steps(self):
        """Show next steps to user"""
        print("\n" + "="*60)
        print("✅ SETUP COMPLETE!")
        print("="*60)
        
        print("\n📋 Files created:")
        print("  ✓ .gitignore")
        print("  ✓ config/config.example.json")
        print("  ✓ logs/.gitkeep")
        print("  ✓ sounds/.gitkeep")
        
        print("\n🔒 Protected files (will NOT be pushed):")
        print("  • config/config.json (has your bot token)")
        print("  • logs/*.csv (your personal data)")
        print("  • __pycache__/ (Python cache)")
        
        print("\n📤 Next steps to push to GitHub:")
        print("  1. git add .")
        print("  2. git status  # Verify config.json NOT listed!")
        print("  3. git commit -m \"Initial commit\"")
        print("  4. git push -u origin main")
        
        print("\n⚠️  IMPORTANT:")
        print("  • NEVER edit config.example.json with real tokens")
        print("  • ALWAYS check 'git status' before pushing")
        print("  • config/config.json should NEVER appear in git status")
        
        print("\n" + "="*60 + "\n")
    
    def run(self):
        """Run complete setup"""
        self.print_header()
        
        # Check Git
        git_exists = self.check_git_initialized()
        
        # Create protection files
        success = True
        success &= self.create_gitignore()
        success &= self.create_config_example()
        success &= self.create_gitkeep_files()
        
        # Verify
        issues = self.verify_protection()
        
        if issues:
            print("\n⚠️  Issues found:")
            for issue in issues:
                print(f"  {issue}")
        
        # Test Git ignore
        if git_exists:
            self.test_git_ignore()
        
        # Show next steps
        if success:
            self.show_next_steps()
        else:
            print("\n⚠️  Some steps failed. Please check errors above.")
        
        return success


def main():
    """Main function"""
    print("Starting Git Protection Setup...")
    
    setup = GitProtectionSetup()
    success = setup.run()
    
    if success:
        print("✅ Git protection setup completed successfully!")
        return 0
    else:
        print("❌ Git protection setup failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())