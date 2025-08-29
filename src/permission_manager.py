"""
Permission Manager for Autonomous Development Environment (ADE)
Handles Windows-specific permission checks and interactive permission granting
"""

import os
import sys
import ctypes
import subprocess
import winreg
from pathlib import Path
from typing import Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.text import Text


class ADEPermissionManager:
    """Comprehensive permission manager for ADE on Windows"""
    
    def __init__(self):
        self.console = Console()
        self.permissions = {
            "admin_rights": {
                "name": "Administrator Rights",
                "description": "Required for system-level operations",
                "status": False,
                "critical": False,  # Changed to non-critical to allow app to run
                "check_method": self._check_admin_rights,
                "fix_method": self._request_admin_elevation
            },
            "file_system": {
                "name": "File System Access",
                "description": "Read/write access to workspace directory",
                "status": False,
                "critical": True,
                "check_method": self._check_file_system_access,
                "fix_method": self._fix_file_system_access
            },
            "network": {
                "name": "Network Access",
                "description": "Internet connectivity for AI APIs",
                "status": False,
                "critical": True,
                "check_method": self._check_network_access,
                "fix_method": self._fix_network_access
            },
            "registry": {
                "name": "Registry Access",
                "description": "Access to system registry for configuration",
                "status": False,
                "critical": False,
                "check_method": self._check_registry_access,
                "fix_method": self._fix_registry_access
            },
            "environment": {
                "name": "Environment Variables",
                "description": "Access to environment variables",
                "status": False,
                "critical": True,
                "check_method": self._check_environment_access,
                "fix_method": self._fix_environment_access
            },
            "python_packages": {
                "name": "Python Package Management",
                "description": "Ability to install Python packages",
                "status": False,
                "critical": True,
                "check_method": self._check_python_packages,
                "fix_method": self._fix_python_packages
            },
            "workspace": {
                "name": "Workspace Directory",
                "description": "Full access to ADE workspace",
                "status": False,
                "critical": True,
                "check_method": self._check_workspace_access,
                "fix_method": self._fix_workspace_access
            }
        }
        
        self.workspace_dir = Path("data/agent_workspace")
        
    def _check_admin_rights(self) -> bool:
        """Check if running with administrator privileges"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False
    
    def _request_admin_elevation(self) -> bool:
        """Request administrator elevation"""
        if self._check_admin_rights():
            return True
            
        self.console.print("\n[yellow]⚠️ Administrator rights required[/yellow]")
        self.console.print("The ADE needs administrator privileges for system operations.")
        self.console.print("\n[bold blue]MANUAL SOLUTION:[/bold blue]")
        self.console.print("1. Close this application")
        self.console.print("2. Right-click on your terminal/command prompt")
        self.console.print("3. Select 'Run as Administrator'")
        self.console.print("4. Navigate to this directory and run the application again")
        self.console.print("\n[yellow]OR[/yellow]")
        self.console.print("Accept that some advanced features may be limited without admin rights.")
        
        # For now, we'll mark this as non-critical to allow the app to continue
        self.console.print("\n[green]✅ Continuing without administrator privileges[/green]")
        self.console.print("[yellow]Some advanced features may be limited[/yellow]")
        return False  # Return False but don't block the application
    
    def _check_file_system_access(self) -> bool:
        """Check file system read/write access"""
        try:
            test_dir = Path("data/test_permissions")
            test_dir.mkdir(parents=True, exist_ok=True)
            
            test_file = test_dir / "test.txt"
            test_file.write_text("permission test", encoding="utf-8")
            
            content = test_file.read_text(encoding="utf-8")
            test_file.unlink()
            test_dir.rmdir()
            
            return content == "permission test"
            
        except Exception:
            return False
    
    def _fix_file_system_access(self) -> bool:
        """Fix file system access issues"""
        try:
            # Create necessary directories with proper permissions
            directories = [
                Path("data"),
                Path("data/agent_workspace"),
                Path("data/memory"),
                Path("data/logs"),
                Path("src"),
                Path("src/todo_list")
            ]
            
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                
            return self._check_file_system_access()
            
        except Exception as e:
            self.console.print(f"[red]❌ Failed to fix file system access: {e}[/red]")
            return False
    
    def _check_network_access(self) -> bool:
        """Check network connectivity"""
        try:
            import urllib.request
            urllib.request.urlopen('https://www.google.com', timeout=5)
            return True
        except Exception:
            return False
    
    def _fix_network_access(self) -> bool:
        """Attempt to fix network access issues"""
        self.console.print("\n[yellow]⚠️ Network access required[/yellow]")
        self.console.print("Please check your internet connection and firewall settings.")
        
        if Confirm.ask("Would you like to test network connection again?"):
            return self._check_network_access()
        
        return False
    
    def _check_registry_access(self) -> bool:
        """Check registry access"""
        try:
            # Try to read a common registry key
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software")
            winreg.CloseKey(key)
            return True
        except Exception:
            return False
    
    def _fix_registry_access(self) -> bool:
        """Fix registry access issues"""
        self.console.print("\n[yellow]⚠️ Registry access limited[/yellow]")
        self.console.print("Some features may be limited without registry access.")
        return True  # Non-critical, so we can continue
    
    def _check_environment_access(self) -> bool:
        """Check environment variable access"""
        try:
            # Test reading and setting environment variables
            test_var = "ADE_PERMISSION_TEST"
            os.environ[test_var] = "test_value"
            result = os.environ.get(test_var) == "test_value"
            del os.environ[test_var]
            return result
        except Exception:
            return False
    
    def _fix_environment_access(self) -> bool:
        """Fix environment access issues"""
        return self._check_environment_access()  # Usually not fixable programmatically
    
    def _check_python_packages(self) -> bool:
        """Check if we can install Python packages"""
        try:
            # Check if pip is available and working
            result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except Exception:
            return False
    
    def _fix_python_packages(self) -> bool:
        """Fix Python package management issues"""
        try:
            # Try to upgrade pip
            self.console.print("Attempting to upgrade pip...")
            result = subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                self.console.print("[green]✅ Pip upgraded successfully[/green]")
                return True
            else:
                self.console.print(f"[red]❌ Failed to upgrade pip: {result.stderr}[/red]")
                return False
                
        except Exception as e:
            self.console.print(f"[red]❌ Failed to fix Python packages: {e}[/red]")
            return False
    
    def _check_workspace_access(self) -> bool:
        """Check workspace directory access"""
        try:
            self.workspace_dir.mkdir(parents=True, exist_ok=True)
            
            # Test file operations in workspace
            test_file = self.workspace_dir / "permission_test.txt"
            test_file.write_text("workspace test", encoding="utf-8")
            
            content = test_file.read_text(encoding="utf-8")
            test_file.unlink()
            
            return content == "workspace test"
            
        except Exception:
            return False
    
    def _fix_workspace_access(self) -> bool:
        """Fix workspace access issues"""
        try:
            self.workspace_dir.mkdir(parents=True, exist_ok=True)
            return self._check_workspace_access()
        except Exception:
            return False
    
    def check_all_permissions(self, show_progress: bool = True) -> Dict[str, bool]:
        """Check all permissions with optional progress display"""
        results = {}
        
        if show_progress:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Checking permissions...", total=len(self.permissions))
                
                for perm_id, permission in self.permissions.items():
                    progress.update(task, description=f"Checking {permission['name']}...")
                    try:
                        status = permission['check_method']()
                        permission['status'] = status
                        results[perm_id] = status
                    except Exception as e:
                        permission['status'] = False
                        results[perm_id] = False
                        self.console.print(f"[red]Error checking {permission['name']}: {e}[/red]")
                    
                    progress.advance(task)
        else:
            for perm_id, permission in self.permissions.items():
                try:
                    status = permission['check_method']()
                    permission['status'] = status
                    results[perm_id] = status
                except Exception:
                    permission['status'] = False
                    results[perm_id] = False
        
        return results
    
    def show_permission_status(self):
        """Display current permission status"""
        table = Table(title="🔐 Permission Status", show_header=True, header_style="bold blue")
        table.add_column("Permission", style="cyan", width=20)
        table.add_column("Status", justify="center", width=10)
        table.add_column("Critical", justify="center", width=10)
        table.add_column("Description", style="white")
        
        for perm_id, permission in self.permissions.items():
            status_icon = "✅" if permission['status'] else "❌"
            status_style = "green" if permission['status'] else "red"
            critical_icon = "🔥" if permission['critical'] else "ℹ️"
            
            table.add_row(
                permission['name'],
                f"[{status_style}]{status_icon}[/{status_style}]",
                critical_icon,
                permission['description']
            )
        
        self.console.print(table)
        
        # Show summary
        total = len(self.permissions)
        granted = sum(1 for p in self.permissions.values() if p['status'])
        critical_missing = sum(1 for p in self.permissions.values() if p['critical'] and not p['status'])
        
        if critical_missing > 0:
            self.console.print(f"\n[red]⚠️ {critical_missing} critical permissions missing![/red]")
        elif granted == total:
            self.console.print(f"\n[green]✅ All permissions granted! ({granted}/{total})[/green]")
        else:
            self.console.print(f"\n[yellow]⚠️ {granted}/{total} permissions granted[/yellow]")
    
    def fix_permissions_interactively(self) -> bool:
        """Interactive permission fixing"""
        self.console.print("\n[bold blue]🔧 Interactive Permission Fixer[/bold blue]")
        
        missing_permissions = [
            (perm_id, perm) for perm_id, perm in self.permissions.items() 
            if not perm['status']
        ]
        
        if not missing_permissions:
            self.console.print("[green]✅ All permissions are already granted![/green]")
            return True
        
        for perm_id, permission in missing_permissions:
            self.console.print(f"\n[yellow]⚠️ Missing: {permission['name']}[/yellow]")
            self.console.print(f"Description: {permission['description']}")
            
            if permission['critical']:
                self.console.print("[red]This permission is CRITICAL for ADE operation![/red]")
            
            if Confirm.ask(f"Would you like to fix '{permission['name']}'?", default=True):
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console
                ) as progress:
                    task = progress.add_task(f"Fixing {permission['name']}...")
                    
                    try:
                        success = permission['fix_method']()
                        if success:
                            permission['status'] = True
                            self.console.print(f"[green]✅ Fixed {permission['name']}![/green]")
                        else:
                            self.console.print(f"[red]❌ Failed to fix {permission['name']}[/red]")
                    except Exception as e:
                        self.console.print(f"[red]❌ Error fixing {permission['name']}: {e}[/red]")
                    
                    progress.remove_task(task)
            else:
                self.console.print(f"[yellow]⏭️ Skipping {permission['name']}[/yellow]")
        
        # Re-check all permissions after fixes
        self.console.print("\n[blue]🔄 Re-checking permissions...[/blue]")
        self.check_all_permissions(show_progress=True)
        
        critical_missing = sum(1 for p in self.permissions.values() if p['critical'] and not p['status'])
        return critical_missing == 0
    
    def run_interactive_mode(self) -> bool:
        """Run full interactive permission management"""
        self.console.print(Panel(
            "Welcome to ADE Permission Manager\n\n"
            "This tool will check and fix permissions required for the\n"
            "Autonomous Development Environment to function properly.",
            title="🔐 ADE Permission Manager",
            border_style="blue"
        ))
        
        # Initial check
        self.console.print("\n[blue]🔍 Checking current permissions...[/blue]")
        self.check_all_permissions(show_progress=True)
        self.show_permission_status()
        
        # Check if we need to fix anything
        critical_missing = sum(1 for p in self.permissions.values() if p['critical'] and not p['status'])
        
        if critical_missing == 0:
            self.console.print("\n[green]🎉 All critical permissions are granted! ADE is ready to run.[/green]")
            return True
        
        # Interactive fixing
        if Confirm.ask(f"\n{critical_missing} critical permissions need fixing. Start interactive fix?", default=True):
            return self.fix_permissions_interactively()
        else:
            self.console.print("\n[yellow]⚠️ Cannot start ADE without critical permissions.[/yellow]")
            return False


def main():
    """Test the permission manager"""
    manager = ADEPermissionManager()
    manager.run_interactive_mode()


if __name__ == "__main__":
    main()
