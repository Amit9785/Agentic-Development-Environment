#!/usr/bin/env python3
"""
File and Folder Creation Tool
A utility to create files and directories as per requirements
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Union


class FileSystemCreator:
    """A tool to create files and folders with specified content and structure."""
    
    def __init__(self, base_path: str = "."):
        """
        Initialize the FileSystemCreator.
        
        Args:
            base_path: Base directory path for operations (default: current directory)
        """
        self.base_path = Path(base_path).resolve()
        self.created_items = []
        
    def create_folder(self, folder_path: str, create_parents: bool = True) -> bool:
        """
        Create a folder at the specified path.
        
        Args:
            folder_path: Path where the folder should be created
            create_parents: Whether to create parent directories if they don't exist
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            full_path = self.base_path / folder_path
            
            if create_parents:
                full_path.mkdir(parents=True, exist_ok=True)
            else:
                full_path.mkdir(exist_ok=True)
                
            self.created_items.append({"type": "folder", "path": str(full_path)})
            print(f"✅ Folder created: {full_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating folder '{folder_path}': {e}")
            return False
    
    def create_file(self, file_path: str, content: str = "", encoding: str = "utf-8") -> bool:
        """
        Create a file with specified content.
        
        Args:
            file_path: Path where the file should be created
            content: Content to write to the file
            encoding: File encoding (default: utf-8)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            full_path = self.base_path / file_path
            
            # Create parent directories if they don't exist
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content to file
            with open(full_path, 'w', encoding=encoding) as f:
                f.write(content)
                
            self.created_items.append({"type": "file", "path": str(full_path), "size": len(content)})
            print(f"✅ File created: {full_path} ({len(content)} characters)")
            return True
            
        except Exception as e:
            print(f"❌ Error creating file '{file_path}': {e}")
            return False
    
    def create_from_template(self, template_name: str, **kwargs) -> bool:
        """
        Create files from predefined templates.
        
        Args:
            template_name: Name of the template to use
            **kwargs: Template parameters
            
        Returns:
            bool: True if successful, False otherwise
        """
        templates = {
            "python_script": {
                "file": "{name}.py",
                "content": '''#!/usr/bin/env python3
"""
{description}
"""

def main():
    """Main function."""
    print("Hello, World!")

if __name__ == "__main__":
    main()
'''
            },
            "readme": {
                "file": "README.md",
                "content": '''# {title}

{description}

## Installation

```bash
# Installation instructions here
```

## Usage

```bash
# Usage examples here
```

## License

MIT License
'''
            },
            "config_json": {
                "file": "config.json",
                "content": '''{
    "name": "{name}",
    "version": "1.0.0",
    "description": "{description}",
    "settings": {
        "debug": false,
        "port": 8080
    }
}'''
            },
            "html_page": {
                "file": "{name}.html",
                "content": '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
</head>
<body>
    <h1>{title}</h1>
    <p>{description}</p>
</body>
</html>'''
            }
        }
        
        if template_name not in templates:
            print(f"❌ Template '{template_name}' not found")
            return False
        
        template = templates[template_name]
        file_path = template["file"].format(**kwargs)
        content = template["content"].format(**kwargs)
        
        return self.create_file(file_path, content)
    
    def create_project_structure(self, project_config: Dict) -> bool:
        """
        Create a complete project structure from configuration.
        
        Args:
            project_config: Dictionary containing project structure configuration
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            project_name = project_config.get("name", "new_project")
            
            # Create project root folder
            if not self.create_folder(project_name):
                return False
            
            # Change base path to project folder
            old_base = self.base_path
            self.base_path = self.base_path / project_name
            
            # Create folders
            folders = project_config.get("folders", [])
            for folder in folders:
                self.create_folder(folder)
            
            # Create files
            files = project_config.get("files", {})
            for file_path, content in files.items():
                self.create_file(file_path, content)
            
            # Restore base path
            self.base_path = old_base
            
            print(f"🎉 Project '{project_name}' structure created successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error creating project structure: {e}")
            return False
    
    def list_created_items(self):
        """List all items created in this session."""
        if not self.created_items:
            print("No items have been created yet.")
            return
        
        print("\n📋 Created Items:")
        print("-" * 50)
        for item in self.created_items:
            icon = "📁" if item["type"] == "folder" else "📄"
            if item["type"] == "file":
                print(f"{icon} {item['path']} ({item['size']} chars)")
            else:
                print(f"{icon} {item['path']}")
    
    def clear_history(self):
        """Clear the creation history."""
        self.created_items.clear()
        print("✅ Creation history cleared.")


def main():
    """Main function for command-line usage."""
    if len(sys.argv) < 2:
        print("Usage examples:")
        print("python file_folder_creator.py create_folder 'my_folder'")
        print("python file_folder_creator.py create_file 'test.txt' 'Hello World'")
        print("python file_folder_creator.py create_template python_script name=test description='Test script'")
        return
    
    creator = FileSystemCreator()
    command = sys.argv[1]
    
    if command == "create_folder":
        if len(sys.argv) >= 3:
            creator.create_folder(sys.argv[2])
        else:
            print("❌ Please provide folder path")
    
    elif command == "create_file":
        if len(sys.argv) >= 3:
            content = sys.argv[3] if len(sys.argv) > 3 else ""
            creator.create_file(sys.argv[2], content)
        else:
            print("❌ Please provide file path")
    
    elif command == "create_template":
        if len(sys.argv) >= 3:
            template_name = sys.argv[2]
            kwargs = {}
            for arg in sys.argv[3:]:
                if "=" in arg:
                    key, value = arg.split("=", 1)
                    kwargs[key] = value
            creator.create_from_template(template_name, **kwargs)
        else:
            print("❌ Please provide template name")
    
    elif command == "demo":
        demo_project_structure(creator)
    
    else:
        print(f"❌ Unknown command: {command}")
    
    creator.list_created_items()


def demo_project_structure(creator: FileSystemCreator):
    """Demonstrate creating a complete project structure."""
    project_config = {
        "name": "sample_project",
        "folders": [
            "src",
            "tests",
            "docs",
            "config",
            "data",
            "scripts"
        ],
        "files": {
            "README.md": """# Sample Project

This is a sample project created by the File and Folder Creation Tool.

## Structure

- `src/` - Source code
- `tests/` - Test files
- `docs/` - Documentation
- `config/` - Configuration files
- `data/` - Data files
- `scripts/` - Utility scripts
""",
            "src/__init__.py": "",
            "src/main.py": '''#!/usr/bin/env python3
"""
Main application module.
"""

def main():
    """Main function."""
    print("Sample Project is running!")

if __name__ == "__main__":
    main()
''',
            "tests/__init__.py": "",
            "tests/test_main.py": '''import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import main

class TestMain(unittest.TestCase):
    def test_main(self):
        """Test main function."""
        # Add your tests here
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
''',
            "config/settings.json": '''{
    "app_name": "Sample Project",
    "version": "1.0.0",
    "debug": true,
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "sample_db"
    }
}''',
            "requirements.txt": """# Project dependencies
requests>=2.28.0
pandas>=1.5.0
numpy>=1.24.0
""",
            ".gitignore": """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""
        }
    }
    
    creator.create_project_structure(project_config)


if __name__ == "__main__":
    main()
