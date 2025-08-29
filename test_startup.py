"""
Test script to verify ADE startup without running the full interactive loop
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test if all required modules can be imported"""
    try:
        from permission_manager import ADEPermissionManager
        print("✅ Permission Manager import successful")
        
        from agent import build_agent
        print("✅ Agent module import successful")
        
        from main import AutonomousADE
        print("✅ Main ADE class import successful")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_permission_manager():
    """Test permission manager functionality"""
    try:
        from permission_manager import ADEPermissionManager
        pm = ADEPermissionManager()
        
        # Quick permission check
        results = pm.check_all_permissions(show_progress=False)
        granted = sum(results.values())
        total = len(results)
        
        print(f"🔐 Permissions: {granted}/{total} granted")
        
        # Check critical permissions
        critical_missing = sum(1 for perm in pm.permissions.values() 
                              if perm["critical"] and not perm["status"])
        
        if critical_missing == 0:
            print("✅ All critical permissions are available")
            return True
        else:
            print(f"⚠️ {critical_missing} critical permissions missing")
            return False
            
    except Exception as e:
        print(f"❌ Permission manager error: {e}")
        return False

def test_agent_setup():
    """Test agent setup without full initialization"""
    try:
        from agent import build_agent
        
        # Check if we have required environment variables
        if not os.getenv("GOOGLE_API_KEY"):
            print("⚠️ GOOGLE_API_KEY not found in environment")
            return False
            
        print("✅ Environment variables are set")
        print("✅ Agent module ready (not testing full initialization to avoid API calls)")
        return True
        
    except Exception as e:
        print(f"❌ Agent setup error: {e}")
        return False

def main():
    """Run all startup tests"""
    print("🚀 Testing ADE Startup Components\n")
    
    tests = [
        ("Module Imports", test_imports),
        ("Permission Manager", test_permission_manager),
        ("Agent Setup", test_agent_setup)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}...")
        result = test_func()
        results.append(result)
        print(f"{'✅' if result else '❌'} {test_name}: {'PASSED' if result else 'FAILED'}")
    
    # Final summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n🎯 TEST SUMMARY: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ADE is ready to run! All startup components are working correctly.")
        print("\n💡 To start ADE, run: python -m src.main")
    else:
        print(f"\n⚠️ {total - passed} tests failed. Please check the issues above before running ADE.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
