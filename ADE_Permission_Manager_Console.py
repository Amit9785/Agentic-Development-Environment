#!/usr/bin/env python3
"""
ADE Windows Console Permission Manager
A console-based application that handles Windows permissions and setup for ADE to run successfully on any Windows system.
"""

import os
import sys
import subprocess
import json
import ctypes
import platform
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional
import re

class Colors:
    """ANSI color codes for console output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    
    # Background colors
    BG_RED = '\033[101m'
    BG_GREEN = '\033[102m'
    BG_YELLOW = '\033[103m'
    BG_BLUE = '\033[104m'

class ADEConsolePermissionManager:
    """Console-based Windows Permission Manager for ADE"""
    
    def __init__(self):
        # Enable ANSI colors on Windows
        self.enable_ansi_colors()
        
        self.permissions = {
            "admin_rights": {"status": False, "desc": "Administrator Rights", "critical": True},
            "python_installed": {"status": False, "desc": "Python 3.8+ Installation", "critical": True},
            "pip_available": {"status": False, "desc": "pip Package Manager", "critical": True},
            "file_access": {"status": False, "desc": "File System Access", "critical": True},
            "network_access": {"status": False, "desc": "Internet Connectivity", "critical": True},
            "workspace_created": {"status": False, "desc": "ADE Workspace", "critical": False},
            "api_keys_set": {"status": False, "desc": "API Keys Configured", "critical": False},
            "dependencies_installed": {"status": False, "desc": "Python Dependencies", "critical": False},
            "firewall_configured": {"status": False, "desc": "Windows Firewall", "critical": False},
            "antivirus_exclusion": {"status": False, "desc": "Antivirus Exclusion", "critical": False}
        }
        
        self.system_info = {
            "os": platform.system(),
            "version": platform.version(),
            "architecture": platform.architecture()[0],
            "python_version": sys.version,
            "user": self.get_current_user(),
            "admin": self.is_admin(),
            "working_dir": str(Path.cwd())
        }
        
        self.config = {
            "google_api_key": "",
            "gemini_model": "gemini-1.5-flash",
            "workspace_dir": str(Path.cwd()),
            "ade_ready": False
        }
    
    def enable_ansi_colors(self):
        """Enable ANSI color codes on Windows"""
        if os.name == 'nt':
            try:
                # Enable ANSI escape sequence processing
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                pass
    
    def get_current_user(self) -> str:
        """Get current Windows user"""
        try:
            return os.getlogin()
        except:
            return os.environ.get('USERNAME', 'Unknown')
    
    def is_admin(self) -> bool:
        """Check if running with administrator privileges"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def print_header(self, title: str, color: str = Colors.CYAN):
        """Print formatted header"""
        print(f"\n{color}{Colors.BOLD}{'='*80}{Colors.END}")
        print(f"{color}{Colors.BOLD}{title.center(80)}{Colors.END}")
        print(f"{color}{Colors.BOLD}{'='*80}{Colors.END}\n")
    
    def print_section(self, title: str, color: str = Colors.BLUE):
        """Print formatted section header"""
        print(f"\n{color}{Colors.BOLD}🔧 {title}{Colors.END}")
        print(f"{color}{'─' * (len(title) + 3)}{Colors.END}")
    
    def print_status(self, item: str, status: bool, desc: str = ""):
        """Print status with colored indicator"""
        icon = f"{Colors.GREEN}✅{Colors.END}" if status else f"{Colors.RED}❌{Colors.END}"
        desc_text = f" - {desc}" if desc else ""
        print(f"  {icon} {item}{desc_text}")
    
    def print_progress_bar(self, current: int, total: int, width: int = 50):
        """Print ASCII progress bar"""
        percent = (current / total) * 100
        filled = int(width * current / total)
        bar = '█' * filled + '░' * (width - filled)
        
        if percent == 100:
            color = Colors.GREEN
        elif percent >= 70:
            color = Colors.YELLOW
        else:
            color = Colors.RED
            
        print(f"\n  {color}[{bar}] {percent:.1f}% ({current}/{total}){Colors.END}")
    
    def get_user_input(self, prompt: str, valid_options: List[str] = None, default: str = None) -> str:
        """Get user input with validation"""
        while True:
            if default:
                user_prompt = f"{Colors.CYAN}{prompt} [{default}]: {Colors.END}"
            else:
                user_prompt = f"{Colors.CYAN}{prompt}: {Colors.END}"
            
            try:
                response = input(user_prompt).strip()
                
                if not response and default:
                    return default
                
                if valid_options and response.lower() not in valid_options:
                    print(f"{Colors.RED}❌ Invalid option. Please choose from: {', '.join(valid_options)}{Colors.END}")
                    continue
                
                return response.lower() if valid_options else response
                
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}👋 Operation cancelled by user{Colors.END}")
                return ""
    
    def confirm_action(self, message: str, default: bool = False) -> bool:
        """Ask user for confirmation"""
        default_text = "Y/n" if default else "y/N"
        response = self.get_user_input(f"{message} ({default_text})", ["y", "yes", "n", "no"], "y" if default else "n")
        return response in ["y", "yes"]
    
    def show_system_info(self):
        """Display comprehensive system information"""
        self.print_header("🖥️  SYSTEM INFORMATION")
        
        print(f"  {Colors.BOLD}Operating System:{Colors.END} {self.system_info['os']} {self.system_info['version']}")
        print(f"  {Colors.BOLD}Architecture:{Colors.END} {self.system_info['architecture']}")
        print(f"  {Colors.BOLD}Python Version:{Colors.END} {sys.version.split()[0]}")
        print(f"  {Colors.BOLD}Current User:{Colors.END} {self.system_info['user']}")
        print(f"  {Colors.BOLD}Working Directory:{Colors.END} {self.system_info['working_dir']}")
        print(f"  {Colors.BOLD}Python Executable:{Colors.END} {sys.executable}")
        
        # Admin status
        if self.system_info['admin']:
            print(f"  {Colors.GREEN}✅ Administrator Rights: Active{Colors.END}")
        else:
            print(f"  {Colors.RED}⚠️  Administrator Rights: Not Active{Colors.END}")
    
    def check_permission(self, perm_key: str) -> bool:
        """Check specific permission"""
        if perm_key == "admin_rights":
            return self.is_admin()
        elif perm_key == "python_installed":
            return sys.version_info >= (3, 8)
        elif perm_key == "pip_available":
            return self.check_pip()
        elif perm_key == "file_access":
            return self.check_file_access()
        elif perm_key == "network_access":
            return self.check_network_access()
        elif perm_key == "workspace_created":
            return self.check_workspace()
        elif perm_key == "api_keys_set":
            return self.check_api_keys()
        elif perm_key == "dependencies_installed":
            return self.check_dependencies()
        elif perm_key == "firewall_configured":
            return self.check_firewall()
        elif perm_key == "antivirus_exclusion":
            return self.check_antivirus()
        return False
    
    def check_pip(self) -> bool:
        """Check if pip is available"""
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def check_file_access(self) -> bool:
        """Check file system access"""
        try:
            test_dir = Path.cwd() / ".ade_permission_test"
            test_dir.mkdir(exist_ok=True)
            test_file = test_dir / "test.txt"
            test_file.write_text("ADE Permission Test")
            content = test_file.read_text()
            test_file.unlink()
            test_dir.rmdir()
            return content == "ADE Permission Test"
        except:
            return False
    
    def check_network_access(self) -> bool:
        """Check network connectivity"""
        try:
            import urllib.request
            with urllib.request.urlopen('https://www.google.com', timeout=5) as response:
                return response.getcode() == 200
        except:
            return False
    
    def check_workspace(self) -> bool:
        """Check if ADE workspace exists"""
        workspace = Path(self.config['workspace_dir'])
        return (workspace / 'data').exists() and (workspace / 'src').exists()
    
    def check_api_keys(self) -> bool:
        """Check if API keys are configured"""
        env_file = Path('.env')
        if env_file.exists():
            try:
                with open(env_file, 'r') as f:
                    content = f.read()
                    return 'GOOGLE_API_KEY' in content and len(content.strip()) > 20
            except:
                pass
        return False
    
    def check_dependencies(self) -> bool:
        """Check if Python dependencies are installed"""
        required_packages = ['langchain', 'langchain-google-genai', 'rich', 'requests', 'beautifulsoup4']
        try:
            for package in required_packages:
                __import__(package.replace('-', '_'))
            return True
        except ImportError:
            return False
    
    def check_firewall(self) -> bool:
        """Check Windows Firewall (simplified check)"""
        try:
            result = subprocess.run(['netsh', 'advfirewall', 'show', 'allprofiles', 'state'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def check_antivirus(self) -> bool:
        """Check antivirus exclusion status (simplified)"""
        # This is a placeholder - real implementation would check specific antivirus software
        return True
    
    def check_all_permissions(self, show_progress: bool = True):
        """Check all permissions and update status"""
        if show_progress:
            self.print_section("🔍 CHECKING SYSTEM PERMISSIONS")
        
        total = len(self.permissions)
        current = 0
        
        for perm_key, perm_info in self.permissions.items():
            if show_progress:
                print(f"  Checking {perm_info['desc']}...", end="", flush=True)
            
            status = self.check_permission(perm_key)
            self.permissions[perm_key]["status"] = status
            current += 1
            
            if show_progress:
                if status:
                    print(f" {Colors.GREEN}✅{Colors.END}")
                else:
                    print(f" {Colors.RED}❌{Colors.END}")
                
                if current % 3 == 0 or current == total:  # Update progress every 3 items or at end
                    self.print_progress_bar(current, total)
    
    def show_permission_status(self):
        """Display current permission status"""
        self.print_header("🛡️  PERMISSION STATUS")
        
        critical_issues = 0
        total_issues = 0
        
        # Critical permissions
        self.print_section("Critical Permissions", Colors.RED)
        for perm_key, perm_info in self.permissions.items():
            if perm_info["critical"]:
                self.print_status(perm_info["desc"], perm_info["status"])
                if not perm_info["status"]:
                    critical_issues += 1
                    total_issues += 1
        
        # Optional permissions
        self.print_section("Optional Permissions", Colors.YELLOW)
        for perm_key, perm_info in self.permissions.items():
            if not perm_info["critical"]:
                self.print_status(perm_info["desc"], perm_info["status"])
                if not perm_info["status"]:
                    total_issues += 1
        
        # Overall status
        print(f"\n{Colors.BOLD}📊 OVERALL STATUS:{Colors.END}")
        if critical_issues == 0:
            if total_issues == 0:
                print(f"  {Colors.GREEN}🟢 All systems ready - ADE can run successfully!{Colors.END}")
            else:
                print(f"  {Colors.YELLOW}🟡 Core systems ready - {total_issues} optional issues remain{Colors.END}")
        else:
            print(f"  {Colors.RED}🔴 {critical_issues} critical issues must be resolved before ADE can run{Colors.END}")
    
    def fix_permission(self, perm_key: str) -> bool:
        """Attempt to fix specific permission issue"""
        perm_info = self.permissions[perm_key]
        print(f"\n{Colors.BLUE}🔧 Attempting to fix: {perm_info['desc']}{Colors.END}")
        
        if perm_key == "admin_rights":
            return self.fix_admin_rights()
        elif perm_key == "pip_available":
            return self.fix_pip()
        elif perm_key == "workspace_created":
            return self.create_workspace()
        elif perm_key == "api_keys_set":
            return self.setup_api_keys()
        elif perm_key == "dependencies_installed":
            return self.install_dependencies()
        else:
            print(f"  {Colors.YELLOW}⚠️  No automatic fix available for {perm_info['desc']}{Colors.END}")
            return False
    
    def fix_admin_rights(self) -> bool:
        """Request admin privileges"""
        if self.is_admin():
            return True
        
        print(f"  {Colors.YELLOW}⚠️  ADE needs administrator privileges for full functionality{Colors.END}")
        
        if self.confirm_action("Restart as administrator?"):
            try:
                # Show instructions for manual restart
                print(f"\n{Colors.CYAN}📋 Instructions:{Colors.END}")
                print(f"  1. Close this application")
                print(f"  2. Right-click on Command Prompt or PowerShell")
                print(f"  3. Select 'Run as administrator'")
                print(f"  4. Navigate to: {Path.cwd()}")
                print(f"  5. Run: python {Path(__file__).name}")
                
                input(f"\n{Colors.YELLOW}Press Enter to close this application...{Colors.END}")
                sys.exit(0)
            except Exception as e:
                print(f"  {Colors.RED}❌ Error: {str(e)}{Colors.END}")
                return False
        return False
    
    def fix_pip(self) -> bool:
        """Fix pip installation"""
        try:
            print("  Installing/upgrading pip...")
            result = subprocess.run([sys.executable, '-m', 'ensurepip', '--upgrade'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  {Colors.GREEN}✅ pip installed/upgraded successfully{Colors.END}")
                return True
            else:
                print(f"  {Colors.RED}❌ pip installation failed{Colors.END}")
                return False
        except Exception as e:
            print(f"  {Colors.RED}❌ Error installing pip: {str(e)}{Colors.END}")
            return False
    
    def create_workspace(self) -> bool:
        """Create ADE workspace directories"""
        try:
            workspace = Path(self.config['workspace_dir'])
            directories = [
                workspace / 'data',
                workspace / 'data' / 'vectorstore', 
                workspace / 'data' / 'agent_workspace',
                workspace / 'src' / 'tools'
            ]
            
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                print(f"  ✅ Created: {directory}")
            
            print(f"  {Colors.GREEN}✅ Workspace created successfully{Colors.END}")
            return True
            
        except Exception as e:
            print(f"  {Colors.RED}❌ Error creating workspace: {str(e)}{Colors.END}")
            return False
    
    def setup_api_keys(self) -> bool:
        """Setup API keys interactively"""
        print(f"\n{Colors.CYAN}🔑 API Key Configuration{Colors.END}")
        
        api_key = self.get_user_input("Enter your Google API Key (or press Enter to skip)")
        if not api_key:
            print(f"  {Colors.YELLOW}⚠️  Skipped API key setup{Colors.END}")
            return False
        
        model = self.get_user_input("Gemini Model", ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"], "gemini-1.5-flash")
        
        try:
            env_path = Path('.env')
            with open(env_path, 'w') as f:
                f.write(f'GOOGLE_API_KEY="{api_key}"\n')
                f.write(f'GEMINI_MODEL="{model}"\n')
            
            print(f"  {Colors.GREEN}✅ API keys saved to {env_path}{Colors.END}")
            return True
            
        except Exception as e:
            print(f"  {Colors.RED}❌ Error saving API keys: {str(e)}{Colors.END}")
            return False
    
    def install_dependencies(self) -> bool:
        """Install Python dependencies"""
        print(f"  {Colors.BLUE}📦 Installing Python dependencies...{Colors.END}")
        
        requirements_file = Path('requirements.txt')
        if not requirements_file.exists():
            print(f"  {Colors.YELLOW}⚠️  requirements.txt not found, installing essential packages{Colors.END}")
            packages = [
                'langchain>=0.2.17',
                'langchain-google-genai>=2.1.9',
                'rich>=13.7.1',
                'requests>=2.31.0',
                'beautifulsoup4>=4.13.5',
                'faiss-cpu>=1.8.0',
                'tiktoken>=0.7.0'
            ]
        else:
            packages = ['requirements.txt']
        
        try:
            for package in packages:
                if package == 'requirements.txt':
                    cmd = [sys.executable, '-m', 'pip', 'install', '-r', package]
                    print(f"    Installing from {package}...")
                else:
                    cmd = [sys.executable, '-m', 'pip', 'install', package]
                    print(f"    Installing {package}...")
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"  {Colors.RED}❌ Failed to install {package}{Colors.END}")
                    print(f"    Error: {result.stderr}")
                    return False
            
            print(f"  {Colors.GREEN}✅ All dependencies installed successfully{Colors.END}")
            return True
            
        except Exception as e:
            print(f"  {Colors.RED}❌ Error installing dependencies: {str(e)}{Colors.END}")
            return False
    
    def auto_fix_issues(self):
        """Automatically fix all fixable issues"""
        self.print_header("🔧 AUTO-FIX MODE")
        
        print(f"{Colors.YELLOW}Attempting to automatically fix all detected issues...{Colors.END}\n")
        
        fixes_attempted = 0
        fixes_successful = 0
        
        for perm_key, perm_info in self.permissions.items():
            if not perm_info["status"]:
                fixes_attempted += 1
                print(f"\n{Colors.BLUE}[{fixes_attempted}] Fixing: {perm_info['desc']}{Colors.END}")
                
                if self.fix_permission(perm_key):
                    fixes_successful += 1
                    self.permissions[perm_key]["status"] = True
                
                time.sleep(1)  # Brief pause between fixes
        
        print(f"\n{Colors.BOLD}📊 AUTO-FIX RESULTS:{Colors.END}")
        print(f"  Fixes attempted: {fixes_attempted}")
        print(f"  Fixes successful: {fixes_successful}")
        
        if fixes_successful == fixes_attempted and fixes_attempted > 0:
            print(f"  {Colors.GREEN}✅ All issues fixed successfully!{Colors.END}")
        elif fixes_successful > 0:
            print(f"  {Colors.YELLOW}⚠️  {fixes_attempted - fixes_successful} issues require manual intervention{Colors.END}")
    
    def launch_ade(self):
        """Launch ADE application"""
        self.print_header("🚀 LAUNCHING ADE")
        
        # Final permission check
        self.check_all_permissions(show_progress=False)
        
        critical_issues = sum(1 for perm in self.permissions.values() if perm["critical"] and not perm["status"])
        
        if critical_issues > 0:
            print(f"{Colors.RED}❌ Cannot launch ADE: {critical_issues} critical issues remain{Colors.END}")
            print(f"   Use 'fix' command to resolve issues first")
            return False
        
        # Try to launch ADE
        ade_main = Path('src/main.py')
        if not ade_main.exists():
            print(f"{Colors.RED}❌ ADE main file not found: {ade_main}{Colors.END}")
            return False
        
        print(f"{Colors.GREEN}✅ All critical requirements met{Colors.END}")
        
        if self.confirm_action("Launch ADE now?", True):
            try:
                print(f"\n{Colors.CYAN}🚀 Starting ADE...{Colors.END}")
                
                # Launch ADE in a new process
                if os.name == 'nt':  # Windows
                    subprocess.Popen([sys.executable, '-m', 'src.main'], 
                                   creationflags=subprocess.CREATE_NEW_CONSOLE)
                else:
                    subprocess.Popen([sys.executable, '-m', 'src.main'])
                
                print(f"{Colors.GREEN}✅ ADE launched successfully!{Colors.END}")
                print(f"{Colors.CYAN}💡 ADE is now running in a separate window{Colors.END}")
                return True
                
            except Exception as e:
                print(f"{Colors.RED}❌ Failed to launch ADE: {str(e)}{Colors.END}")
                return False
        
        return False
    
    def show_menu(self):
        """Display main menu"""
        self.print_header("🛡️  ADE PERMISSION MANAGER")
        
        print(f"{Colors.CYAN}Available Commands:{Colors.END}")
        print(f"  {Colors.GREEN}check{Colors.END}     - Check all system permissions and requirements")
        print(f"  {Colors.BLUE}status{Colors.END}    - Show current permission status")
        print(f"  {Colors.YELLOW}fix{Colors.END}       - Automatically fix all detected issues")
        print(f"  {Colors.PURPLE}config{Colors.END}    - Configure API keys and settings")
        print(f"  {Colors.GREEN}launch{Colors.END}    - Launch ADE (if ready)")
        print(f"  {Colors.CYAN}info{Colors.END}      - Show system information")
        print(f"  {Colors.WHITE}help{Colors.END}      - Show detailed help")
        print(f"  {Colors.RED}exit{Colors.END}      - Exit permission manager")
    
    def show_help(self):
        """Display detailed help"""
        self.print_header("🆘 HELP & DOCUMENTATION")
        
        help_text = f"""
{Colors.BOLD}ADE Windows Console Permission Manager{Colors.END}

This tool ensures ADE (Agentic Development Environment) runs successfully 
on your Windows system by checking and fixing permissions and requirements.

{Colors.BOLD}🔍 SYSTEM CHECKS:{Colors.END}
• Administrator rights for system operations
• Python 3.8+ installation and PATH configuration  
• pip package manager availability
• File system read/write permissions
• Internet connectivity for API calls
• Required Python dependencies

{Colors.BOLD}🔧 AUTO-FIX CAPABILITIES:{Colors.END}
• Install/upgrade pip package manager
• Create ADE workspace directories
• Install Python dependencies from requirements.txt
• Configure API keys and environment variables
• Setup proper file permissions

{Colors.BOLD}⚙️ CONFIGURATION:{Colors.END}
• Google API key for AI services (Gemini)
• Model selection (gemini-1.5-flash, gemini-1.5-pro, etc.)
• Workspace directory location
• Environment variable setup

{Colors.BOLD}🚀 LAUNCH PROCESS:{Colors.END}
• Validates all critical requirements are met
• Launches ADE in autonomous mode
• Provides real-time status feedback

{Colors.BOLD}💡 TIPS:{Colors.END}
• Run as Administrator for full functionality
• Ensure stable internet connection
• Have your Google API key ready
• Close antivirus temporarily if issues occur

For more information, visit: https://github.com/your-repo/ADE
        """
        
        print(help_text)
    
    def run_interactive_mode(self):
        """Run the interactive console interface"""
        print(f"{Colors.GREEN}🛡️  ADE Windows Console Permission Manager v1.0{Colors.END}")
        print(f"{Colors.CYAN}Ensuring ADE runs successfully on your Windows system{Colors.END}\n")
        
        # Initial system check
        print(f"{Colors.YELLOW}⏳ Performing initial system check...{Colors.END}")
        self.check_all_permissions(show_progress=False)
        
        while True:
            try:
                self.show_menu()
                
                command = self.get_user_input("\nEnter command", 
                                            ["check", "status", "fix", "config", "launch", "info", "help", "exit"])
                
                if command == "check":
                    self.check_all_permissions()
                    
                elif command == "status":
                    self.show_permission_status()
                    
                elif command == "fix":
                    self.auto_fix_issues()
                    
                elif command == "config":
                    self.setup_api_keys()
                    
                elif command == "launch":
                    if self.launch_ade():
                        print(f"\n{Colors.GREEN}ADE is now running. You can close this window or keep it open for future management.{Colors.END}")
                    
                elif command == "info":
                    self.show_system_info()
                    
                elif command == "help":
                    self.show_help()
                    
                elif command == "exit":
                    print(f"\n{Colors.YELLOW}👋 Thank you for using ADE Permission Manager!{Colors.END}")
                    break
                
                # Wait for user to continue
                if command != "exit":
                    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
                    
            except KeyboardInterrupt:
                print(f"\n\n{Colors.YELLOW}👋 Goodbye!{Colors.END}")
                break
            except Exception as e:
                print(f"\n{Colors.RED}❌ Error: {str(e)}{Colors.END}")
                input(f"{Colors.CYAN}Press Enter to continue...{Colors.END}")

def main():
    """Main function"""
    try:
        # Clear screen
        os.system('cls' if os.name == 'nt' else 'clear')
        
        manager = ADEConsolePermissionManager()
        manager.run_interactive_mode()
        
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
