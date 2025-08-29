"""
Advanced Project Creator Tool
Creates complete projects with permission system, console UI, and intelligent structure generation.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage


class AdvancedProjectCreator:
    """Advanced project creator with AI-powered project generation and permission system"""
    
    def __init__(self):
        self.llm = None
        self.created_projects = []
        
    def _get_llm(self):
        """Lazy initialization of LLM"""
        if self.llm is None:
            try:
                self.llm = ChatGoogleGenerativeAI(
                    model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
                    temperature=0.3,
                    google_api_key=os.getenv("GOOGLE_API_KEY")
                )
            except Exception as e:
                self.llm = "error"
                return None
        return self.llm if self.llm != "error" else None
    
    def analyze_project_requirements(self, project_description: str) -> Dict:
        """Use AI to analyze project requirements and generate structure"""
        
        analysis_prompt = f"""
Analyze this project description and create a detailed project structure:

Project: "{project_description}"

Generate a JSON response with the following structure:
{{
    "project_name": "suggested_project_name",
    "project_type": "web_app|desktop_app|library|cli_tool|data_project|game",
    "technology_stack": ["python", "javascript", "react", etc.],
    "main_features": ["feature1", "feature2", "feature3"],
    "folder_structure": [
        "src/",
        "tests/",
        "docs/",
        "config/",
        "assets/",
        "data/"
    ],
    "essential_files": {{
        "README.md": "Project documentation with setup and usage instructions",
        "requirements.txt": "Python dependencies based on project needs",
        "main.py": "Main application entry point",
        "config.json": "Configuration file",
        "src/__init__.py": "Package initialization",
        "tests/test_main.py": "Basic test structure"
    }},
    "permissions_needed": [
        "file_creation",
        "directory_creation", 
        "console_ui",
        "user_input"
    ],
    "estimated_files": 8,
    "console_ui_needed": true,
    "user_permission_required": true
}}

Focus on creating a professional, scalable project structure with best practices.
        """
        
        llm = self._get_llm()
        if not llm:
            return self._fallback_analysis(project_description)
        
        try:
            response = llm.invoke([HumanMessage(content=analysis_prompt)])
            analysis_text = response.content
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
                return analysis
            else:
                return self._fallback_analysis(project_description)
                
        except Exception as e:
            return self._fallback_analysis(project_description, str(e))
    
    def _fallback_analysis(self, project_description: str, error: str = None) -> Dict:
        """Fallback analysis when LLM is not available"""
        
        # Simple keyword-based analysis
        desc_lower = project_description.lower()
        
        if "todo" in desc_lower or "task" in desc_lower:
            project_type = "cli_tool"
            tech_stack = ["python", "rich"]
            features = ["add_tasks", "list_tasks", "mark_complete", "console_ui"]
        elif "web" in desc_lower or "website" in desc_lower:
            project_type = "web_app"
            tech_stack = ["python", "flask", "html", "css"]
            features = ["web_interface", "routing", "templates"]
        elif "game" in desc_lower:
            project_type = "game"
            tech_stack = ["python", "pygame"]
            features = ["game_loop", "graphics", "input_handling"]
        else:
            project_type = "cli_tool"
            tech_stack = ["python"]
            features = ["main_functionality", "user_interface"]
        
        return {
            "project_name": "ai_generated_project",
            "project_type": project_type,
            "technology_stack": tech_stack,
            "main_features": features,
            "folder_structure": ["src/", "tests/", "docs/", "config/"],
            "essential_files": {
                "README.md": "Project documentation",
                "requirements.txt": "Dependencies",
                "main.py": "Main application",
                "src/__init__.py": "Package init"
            },
            "permissions_needed": ["file_creation", "console_ui"],
            "estimated_files": 6,
            "console_ui_needed": True,
            "user_permission_required": True,
            "fallback_used": True,
            "error": error
        }
    
    def request_user_permission(self, analysis: Dict) -> bool:
        """Request user permission before creating project"""
        
        print("\n" + "="*70)
        print("🚀 ADVANCED PROJECT CREATOR - PERMISSION REQUEST")
        print("="*70)
        
        print(f"\n📋 Project Analysis:")
        print(f"   Name: {analysis['project_name']}")
        print(f"   Type: {analysis['project_type']}")
        print(f"   Tech Stack: {', '.join(analysis['technology_stack'])}")
        print(f"   Estimated Files: {analysis['estimated_files']}")
        
        print(f"\n📁 Folders to Create: {len(analysis['folder_structure'])}")
        for folder in analysis['folder_structure']:
            print(f"   • {folder}")
        
        print(f"\n📄 Essential Files: {len(analysis['essential_files'])}")
        for file_path in analysis['essential_files'].keys():
            print(f"   • {file_path}")
        
        print(f"\n⚡ Features to Implement:")
        for feature in analysis['main_features']:
            print(f"   • {feature}")
        
        print(f"\n🔐 Permissions Needed:")
        for permission in analysis['permissions_needed']:
            print(f"   • {permission}")
        
        print("\n" + "-"*70)
        
        while True:
            try:
                response = input("\n🤖 Do you want me to create this project? (y/n/details): ").strip().lower()
                
                if response in ['y', 'yes']:
                    print("\n✅ Permission granted! Creating project...")
                    return True
                elif response in ['n', 'no']:
                    print("\n❌ Permission denied. Project creation cancelled.")
                    return False
                elif response in ['d', 'details']:
                    self._show_detailed_preview(analysis)
                else:
                    print("Please enter 'y' for yes, 'n' for no, or 'details' for more information.")
                    
            except KeyboardInterrupt:
                print("\n❌ Cancelled by user.")
                return False
    
    def _show_detailed_preview(self, analysis: Dict):
        """Show detailed preview of what will be created"""
        print("\n" + "="*50)
        print("📋 DETAILED PROJECT PREVIEW")
        print("="*50)
        
        for file_path, description in analysis['essential_files'].items():
            print(f"\n📄 {file_path}:")
            print(f"   Purpose: {description}")
            
            # Generate preview content
            preview = self._generate_file_preview(file_path, analysis)
            if preview:
                lines = preview.split('\n')[:5]  # First 5 lines
                for line in lines:
                    print(f"   {line}")
                if len(preview.split('\n')) > 5:
                    print("   ...")
        
        print("\n" + "="*50)
    
    def _generate_file_preview(self, file_path: str, analysis: Dict) -> str:
        """Generate preview content for files"""
        
        if file_path == "README.md":
            return f"""# {analysis['project_name'].replace('_', ' ').title()}

## Description
{analysis.get('main_features', [])}

## Features
{chr(10).join(f'- {feature}' for feature in analysis['main_features'])}

## Installation
```bash
pip install -r requirements.txt
```"""
        
        elif file_path == "main.py":
            if analysis['project_type'] == 'cli_tool':
                return """#!/usr/bin/env python3
\"\"\"
Main application entry point
\"\"\"

def main():
    print("Welcome to the application!")
    # Main logic here
    
if __name__ == "__main__":
    main()"""
        
        elif file_path == "requirements.txt":
            tech_deps = {
                "rich": "rich>=13.0.0",
                "flask": "flask>=2.0.0", 
                "pygame": "pygame>=2.0.0",
                "requests": "requests>=2.25.0"
            }
            deps = [tech_deps.get(tech, f"{tech}>=1.0.0") for tech in analysis['technology_stack'] if tech in tech_deps]
            return '\n'.join(deps)
        
        return ""
    
    def create_project_structure(self, analysis: Dict, base_path: str = ".") -> bool:
        """Create the complete project structure"""
        
        try:
            project_name = analysis['project_name']
            project_path = Path(base_path) / project_name
            
            print(f"\n🏗️  Creating project: {project_name}")
            print(f"📍 Location: {project_path.absolute()}")
            
            # Create main project directory
            project_path.mkdir(parents=True, exist_ok=True)
            
            # Create folder structure
            print(f"\n📁 Creating folders...")
            for folder in analysis['folder_structure']:
                folder_path = project_path / folder
                folder_path.mkdir(parents=True, exist_ok=True)
                print(f"   ✅ {folder}")
            
            # Create essential files
            print(f"\n📄 Creating files...")
            for file_path, description in analysis['essential_files'].items():
                full_file_path = project_path / file_path
                
                # Generate content based on file type and analysis
                content = self._generate_file_content(file_path, analysis)
                
                # Create parent directories if needed
                full_file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write file
                with open(full_file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"   ✅ {file_path} ({len(content)} chars)")
            
            # Add console UI if needed
            if analysis.get('console_ui_needed', False):
                self._create_console_ui(project_path, analysis)
            
            # Log project creation
            self.created_projects.append({
                "name": project_name,
                "path": str(project_path),
                "created_at": datetime.now().isoformat(),
                "analysis": analysis
            })
            
            print(f"\n🎉 Project '{project_name}' created successfully!")
            print(f"📍 Path: {project_path.absolute()}")
            print(f"📊 Files created: {len(analysis['essential_files'])}")
            print(f"📁 Folders created: {len(analysis['folder_structure'])}")
            
            # Show next steps
            self._show_next_steps(project_name, analysis)
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating project: {str(e)}")
            return False
    
    def _generate_file_content(self, file_path: str, analysis: Dict) -> str:
        """Generate actual file content based on analysis"""
        
        project_name = analysis['project_name']
        project_type = analysis['project_type']
        features = analysis['main_features']
        tech_stack = analysis['technology_stack']
        
        if file_path == "README.md":
            return self._generate_readme(analysis)
        
        elif file_path == "main.py":
            return self._generate_main_py(analysis)
        
        elif file_path == "requirements.txt":
            return self._generate_requirements(analysis)
        
        elif file_path == "config.json":
            return self._generate_config(analysis)
        
        elif file_path.endswith("__init__.py"):
            return f'"""\\n{project_name.replace("_", " ").title()} Package\\n"""\\n\\n__version__ = "1.0.0"\\n'
        
        elif file_path.startswith("tests/"):
            return self._generate_test_file(file_path, analysis)
        
        else:
            return f'# {file_path}\\n# Auto-generated file for {project_name}\\n'
    
    def _generate_readme(self, analysis: Dict) -> str:
        """Generate comprehensive README.md"""
        
        project_name = analysis['project_name'].replace('_', ' ').title()
        
        return f"""# {project_name}

## 🚀 Overview

{project_name} is a {analysis['project_type'].replace('_', ' ')} built with {', '.join(analysis['technology_stack'])}.

## ✨ Features

{chr(10).join(f'- **{feature.replace("_", " ").title()}**: Description of {feature}' for feature in analysis['main_features'])}

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd {analysis['project_name']}

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\\Scripts\\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 🎯 Usage

### Basic Usage
```bash
python main.py
```

### Advanced Usage
```bash
# Add more usage examples here
python main.py --help
```

## 📁 Project Structure

```
{analysis['project_name']}/
{chr(10).join(f'├── {folder}' for folder in analysis['folder_structure'])}
{chr(10).join(f'├── {file}' for file in analysis['essential_files'].keys())}
```

## 🧪 Testing

```bash
# Run tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src/
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Created with ADE (Autonomous Agentic Development Environment)
- Built on {datetime.now().strftime('%Y-%m-%d')}

---

*Generated by Advanced Project Creator v1.0*
"""

    def _generate_main_py(self, analysis: Dict) -> str:
        """Generate main.py based on project type"""
        
        project_name = analysis['project_name']
        project_type = analysis['project_type']
        features = analysis['main_features']
        
        if project_type == 'cli_tool' and 'todo' in project_name.lower():
            return self._generate_todo_app(analysis)
        
        elif project_type == 'web_app':
            return self._generate_web_app(analysis)
        
        else:
            return f'''#!/usr/bin/env python3
"""
{project_name.replace('_', ' ').title()} - Main Application
Auto-generated by Advanced Project Creator
"""

import sys
import os
from pathlib import Path

def main():
    """Main application entry point"""
    print(f"🚀 Welcome to {project_name.replace('_', ' ').title()}!")
    
    # Main application logic
    try:
        # Initialize application
        print("⚙️  Initializing application...")
        
        # Add your main logic here
        {chr(10).join(f'        # TODO: Implement {feature}' for feature in features)}
        
        print("✅ Application completed successfully!")
        
    except KeyboardInterrupt:
        print("\\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {{e}}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
    
    def _generate_todo_app(self, analysis: Dict) -> str:
        """Generate a complete TODO application"""
        
        return '''#!/usr/bin/env python3
"""
Advanced Todo List Application
Created by ADE Advanced Project Creator
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

class TodoApp:
    """Advanced Todo List with console UI and persistence"""
    
    def __init__(self, data_file: str = "todos.json"):
        self.data_file = Path(data_file)
        self.todos: List[Dict] = []
        self.load_todos()
    
    def load_todos(self):
        """Load todos from JSON file"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.todos = json.load(f)
        except Exception as e:
            print(f"⚠️  Could not load todos: {e}")
            self.todos = []
    
    def save_todos(self):
        """Save todos to JSON file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.todos, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Could not save todos: {e}")
    
    def add_todo(self, task: str, priority: str = "medium"):
        """Add a new todo item"""
        todo = {
            "id": len(self.todos) + 1,
            "task": task,
            "priority": priority,
            "completed": False,
            "created_at": datetime.now().isoformat(),
            "completed_at": None
        }
        self.todos.append(todo)
        self.save_todos()
        print(f"✅ Added: {task}")
    
    def list_todos(self, show_completed: bool = False):
        """List all todos"""
        if not self.todos:
            print("📝 No todos yet. Add some with 'add <task>'")
            return
        
        print("\\n" + "="*60)
        print("📋 YOUR TODO LIST")
        print("="*60)
        
        for todo in self.todos:
            if not show_completed and todo["completed"]:
                continue
            
            status = "✅" if todo["completed"] else "⏳"
            priority = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(todo["priority"], "⚪")
            
            print(f"{status} [{todo['id']:2d}] {priority} {todo['task']}")
            
            if todo["completed"] and todo.get("completed_at"):
                comp_date = datetime.fromisoformat(todo["completed_at"]).strftime("%Y-%m-%d %H:%M")
                print(f"        Completed: {comp_date}")
        
        print("="*60)
    
    def complete_todo(self, todo_id: int):
        """Mark todo as completed"""
        for todo in self.todos:
            if todo["id"] == todo_id:
                if todo["completed"]:
                    print(f"⚠️  Todo {todo_id} is already completed")
                else:
                    todo["completed"] = True
                    todo["completed_at"] = datetime.now().isoformat()
                    self.save_todos()
                    print(f"🎉 Completed: {todo['task']}")
                return
        print(f"❌ Todo with ID {todo_id} not found")
    
    def delete_todo(self, todo_id: int):
        """Delete a todo"""
        self.todos = [todo for todo in self.todos if todo["id"] != todo_id]
        self.save_todos()
        print(f"🗑️  Deleted todo {todo_id}")
    
    def show_stats(self):
        """Show todo statistics"""
        total = len(self.todos)
        completed = sum(1 for todo in self.todos if todo["completed"])
        pending = total - completed
        
        print("\\n" + "="*40)
        print("📊 TODO STATISTICS")
        print("="*40)
        print(f"📝 Total todos: {total}")
        print(f"✅ Completed: {completed}")
        print(f"⏳ Pending: {pending}")
        if total > 0:
            completion_rate = (completed / total) * 100
            print(f"📈 Completion rate: {completion_rate:.1f}%")
        print("="*40)
    
    def show_help(self):
        """Show available commands"""
        print("\\n" + "="*50)
        print("🆘 AVAILABLE COMMANDS")
        print("="*50)
        print("add <task>           - Add a new todo")
        print("list                 - Show pending todos")
        print("list all            - Show all todos") 
        print("complete <id>       - Mark todo as completed")
        print("delete <id>         - Delete a todo")
        print("stats               - Show statistics")
        print("help                - Show this help")
        print("quit/exit           - Exit the application")
        print("="*50)
    
    def run(self):
        """Main application loop with console UI"""
        print("🚀 Welcome to Advanced Todo List!")
        print("Type 'help' for available commands\\n")
        
        while True:
            try:
                command = input("📝 todo> ").strip().lower()
                
                if not command:
                    continue
                
                parts = command.split(maxsplit=1)
                cmd = parts[0]
                args = parts[1] if len(parts) > 1 else ""
                
                if cmd in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                elif cmd == 'add' and args:
                    # Check priority
                    if args.startswith('!'):
                        self.add_todo(args[1:].strip(), "high")
                    elif args.startswith('?'):
                        self.add_todo(args[1:].strip(), "low")  
                    else:
                        self.add_todo(args, "medium")
                
                elif cmd == 'list':
                    show_all = args == 'all'
                    self.list_todos(show_completed=show_all)
                
                elif cmd == 'complete' and args.isdigit():
                    self.complete_todo(int(args))
                
                elif cmd == 'delete' and args.isdigit():
                    self.delete_todo(int(args))
                
                elif cmd == 'stats':
                    self.show_stats()
                
                elif cmd == 'help':
                    self.show_help()
                
                else:
                    print("❌ Unknown command. Type 'help' for available commands.")
            
            except KeyboardInterrupt:
                print("\\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    """Main function with permission request"""
    print("="*60)
    print("🤖 ADVANCED TODO APP - PERMISSION REQUEST")  
    print("="*60)
    print("This app will:")
    print("• Create/read 'todos.json' in current directory")
    print("• Provide interactive console interface")
    print("• Store your todo data persistently")
    print("="*60)
    
    permission = input("\\n✅ Do you give permission to run this app? (y/n): ").strip().lower()
    
    if permission not in ['y', 'yes']:
        print("❌ Permission denied. Exiting.")
        return
    
    print("\\n🎉 Permission granted! Starting Todo App...\\n")
    
    app = TodoApp()
    app.run()

if __name__ == "__main__":
    main()
'''
    
    def _generate_requirements(self, analysis: Dict) -> str:
        """Generate requirements.txt based on tech stack"""
        
        tech_deps = {
            "rich": "rich>=13.0.0",
            "flask": "flask>=2.0.0",
            "django": "django>=4.0.0", 
            "fastapi": "fastapi>=0.68.0",
            "pygame": "pygame>=2.0.0",
            "requests": "requests>=2.25.0",
            "pandas": "pandas>=1.3.0",
            "numpy": "numpy>=1.21.0",
            "pytest": "pytest>=6.0.0",
            "langchain": "langchain>=0.1.0"
        }
        
        deps = []
        for tech in analysis['technology_stack']:
            if tech.lower() in tech_deps:
                deps.append(tech_deps[tech.lower()])
        
        # Add some common dependencies
        if not deps:
            deps = ["requests>=2.25.0"]
            
        deps.append("")  # Empty line at end
        return '\\n'.join(deps)
    
    def _generate_config(self, analysis: Dict) -> str:
        """Generate config.json"""
        
        config = {
            "app_name": analysis['project_name'],
            "version": "1.0.0",
            "project_type": analysis['project_type'],
            "created_by": "ADE Advanced Project Creator",
            "created_at": datetime.now().isoformat(),
            "settings": {
                "debug": True,
                "logging_level": "INFO"
            },
            "features": analysis['main_features']
        }
        
        return json.dumps(config, indent=2)
    
    def _generate_test_file(self, file_path: str, analysis: Dict) -> str:
        """Generate test files"""
        
        if "test_main.py" in file_path:
            return f'''import unittest
import sys
from pathlib import Path

# Add src to path  
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from main import main
except ImportError:
    # If no main function, create a dummy test
    def main():
        return "test"

class TestMain(unittest.TestCase):
    """Test cases for main application"""
    
    def setUp(self):
        """Set up test fixtures"""
        pass
    
    def test_main_exists(self):
        """Test that main function exists"""
        self.assertTrue(callable(main))
    
    def test_basic_functionality(self):
        """Test basic functionality"""
        # Add your tests here
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
'''
        else:
            return "# Test file\\npass\\n"
    
    def _create_console_ui(self, project_path: Path, analysis: Dict):
        """Create enhanced console UI components"""
        
        ui_path = project_path / "src" / "ui.py"
        ui_content = '''"""
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
    print(f'\\r{message} [{bar}] {percentage:.1f}%', end='', flush=True)
    
    if current >= total:
        print()  # New line when complete
'''
        
        # Create UI file
        ui_path.parent.mkdir(parents=True, exist_ok=True)
        with open(ui_path, 'w', encoding='utf-8') as f:
            f.write(ui_content)
        
        print(f"   ✅ src/ui.py (Console UI components)")
    
    def _show_next_steps(self, project_name: str, analysis: Dict):
        """Show next steps after project creation"""
        
        print("\\n" + "="*60)
        print("🎯 NEXT STEPS")
        print("="*60)
        print(f"1. Navigate to project:")
        print(f"   cd {project_name}")
        print("\\n2. Set up virtual environment:")
        print("   python -m venv venv")
        print("   venv\\\\Scripts\\\\activate  # On Windows")
        print("\\n3. Install dependencies:")
        print("   pip install -r requirements.txt")
        print("\\n4. Run the application:")
        print("   python main.py")
        print("\\n5. Run tests:")
        print("   python -m pytest tests/")
        print("="*60)


# Tool function for LangChain integration
@tool
def advanced_project_creator(project_description: str) -> str:
    """
    Create a complete project with AI analysis, permission system, and console UI.
    
    This tool will:
    1. Analyze the project requirements using AI
    2. Request user permission before creating files
    3. Create a complete project structure with all necessary files
    4. Include console UI components and permission handling
    
    Args:
        project_description: Description of the project to create (e.g., "Create a Todo list application")
    
    Returns:
        str: Status of project creation with details
    """
    
    try:
        creator = AdvancedProjectCreator()
        
        # Step 1: Analyze project requirements
        analysis = creator.analyze_project_requirements(project_description)
        
        # Step 2: Request user permission
        if not creator.request_user_permission(analysis):
            return "❌ Project creation cancelled by user."
        
        # Step 3: Create project structure  
        success = creator.create_project_structure(analysis)
        
        if success:
            return f"""🎉 Project '{analysis['project_name']}' created successfully!

📊 Project Summary:
• Type: {analysis['project_type']}
• Files: {len(analysis['essential_files'])}
• Folders: {len(analysis['folder_structure'])}
• Tech Stack: {', '.join(analysis['technology_stack'])}
• Features: {', '.join(analysis['main_features'])}

✅ The project includes:
• Complete file structure
• Console UI with permission system
• Documentation and tests
• Configuration files
• Ready-to-run main application

🚀 Next: Navigate to the project folder and run 'python main.py'
"""
        else:
            return "❌ Failed to create project structure."
        
    except Exception as e:
        return f"❌ Error in project creation: {str(e)}"

