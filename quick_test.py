"""
Quick test to verify main application startup
"""
import sys
from pathlib import Path
import os

# Set up the path correctly
sys.path.insert(0, str(Path(__file__).parent))

# Test if we can import and initialize the main components
try:
    print("🧪 Testing ADE Components...")
    
    # Test 1: Import permission manager
    from src.permission_manager import ADEPermissionManager
    pm = ADEPermissionManager()
    print("✅ Permission Manager: OK")
    
    # Test 2: Quick permission check
    results = pm.check_all_permissions(show_progress=False)
    granted = sum(results.values())
    total = len(results)
    critical_missing = sum(1 for perm in pm.permissions.values() 
                          if perm["critical"] and not perm["status"])
    print(f"🔐 Permissions: {granted}/{total} granted, {critical_missing} critical missing")
    
    # Test 3: Try to import agent
    from src.agent import build_agent
    print("✅ Agent Module: OK")
    
    # Test 4: Check environment variables
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key and len(api_key) > 20:
        print("✅ Google API Key: OK")
    else:
        print("⚠️ Google API Key: Missing or invalid")
    
    # Test 5: Try to import main class
    from src.main import AutonomousADE
    print("✅ Main ADE Class: OK")
    
    print(f"\n🎯 RESULT: ADE is {'READY' if critical_missing == 0 else 'NEEDS ADMIN RIGHTS'}")
    
    if critical_missing == 0:
        print("\n💡 You can start ADE with: python -m src.main")
    else:
        print("\n💡 Run as Administrator to grant critical permissions, then use: python -m src.main")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
