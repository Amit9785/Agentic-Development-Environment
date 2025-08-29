"""
Console UI Components
Enhanced user interface utilities
"""

def show_banner(app_name: str):
    """Display application banner"""
    banner = f"""
╔══════════════════════════════════════╗
║          {app_name.upper().center(30)}           ║  
╚══════════════════════════════════════╝
    """
    print(banner)

def get_user_confirmation(message: str, default: bool = True) -> bool:
    """Get user confirmation with default"""
    suffix = " [Y/n]: " if default else " [y/N]: "
    
    while True:
        response = input(message + suffix).strip().lower()
        
        if not response:
            return default
        elif response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Please enter 'y' or 'n'")

def show_progress(current: int, total: int, message: str = ""):
    """Show simple progress indicator"""
    percentage = (current / total) * 100 if total > 0 else 0
    bar_length = 30
    filled_length = int(bar_length * current // total) if total > 0 else 0
    
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    print(f'\r{message} [{bar}] {percentage:.1f}%', end='', flush=True)
    
    if current >= total:
        print()  # New line when complete
