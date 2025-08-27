# Todo List Application
"""
A simple todo list management system
"""

import json
from pathlib import Path
from datetime import datetime

class TodoItem:
    def __init__(self, description, completed=False, created_at=None):
        self.description = description
        self.completed = completed
        self.created_at = created_at or datetime.now().isoformat()
    
    def __str__(self):
        status = "✓" if self.completed else "○"
        return f"{status} {self.description}"
    
    def to_dict(self):
        return {
            "description": self.description,
            "completed": self.completed,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            data["description"], 
            data["completed"], 
            data.get("created_at")
        )

class TodoList:
    def __init__(self, filename="todo_data.json"):
        self.filename = filename
        self.items = []
        self.load()
    
    def load(self):
        """Load todo items from file"""
        try:
            if Path(self.filename).exists():
                with open(self.filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.items = [TodoItem.from_dict(item) for item in data]
            else:
                self.items = []
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading todo list: {e}")
            self.items = []
    
    def save(self):
        """Save todo items to file"""
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump([item.to_dict() for item in self.items], f, indent=2)
        except Exception as e:
            print(f"Error saving todo list: {e}")
    
    def add_task(self, description):
        """Add a new task to the todo list"""
        if description.strip():
            task = TodoItem(description.strip())
            self.items.append(task)
            self.save()
            print(f"✓ Added: {description}")
            return True
        else:
            print("Error: Task description cannot be empty")
            return False
    
    def list_tasks(self, show_completed=True):
        """Display all tasks"""
        if not self.items:
            print("📝 No tasks in your todo list!")
            return
        
        print(f"\n📋 Todo List ({len(self.items)} tasks):")
        print("-" * 40)
        
        pending_count = 0
        completed_count = 0
        
        for i, item in enumerate(self.items):
            if item.completed:
                completed_count += 1
                if show_completed:
                    print(f"{i:2d}. {item}")
            else:
                pending_count += 1
                print(f"{i:2d}. {item}")
        
        print("-" * 40)
        print(f"Pending: {pending_count} | Completed: {completed_count}")
    
    def complete_task(self, index):
        """Mark a task as completed"""
        if 0 <= index < len(self.items):
            if not self.items[index].completed:
                self.items[index].completed = True
                self.save()
                print(f"✓ Completed: {self.items[index].description}")
            else:
                print("Task is already completed!")
        else:
            print("Error: Invalid task number")
    
    def uncomplete_task(self, index):
        """Mark a task as not completed"""
        if 0 <= index < len(self.items):
            if self.items[index].completed:
                self.items[index].completed = False
                self.save()
                print(f"○ Reopened: {self.items[index].description}")
            else:
                print("Task is already pending!")
        else:
            print("Error: Invalid task number")
    
    def remove_task(self, index):
        """Remove a task from the list"""
        if 0 <= index < len(self.items):
            removed_task = self.items.pop(index)
            self.save()
            print(f"🗑️ Removed: {removed_task.description}")
        else:
            print("Error: Invalid task number")
    
    def clear_completed(self):
        """Remove all completed tasks"""
        initial_count = len(self.items)
        self.items = [item for item in self.items if not item.completed]
        removed_count = initial_count - len(self.items)
        
        if removed_count > 0:
            self.save()
            print(f"🗑️ Removed {removed_count} completed task(s)")
        else:
            print("No completed tasks to remove")
    
    def get_stats(self):
        """Get statistics about the todo list"""
        total = len(self.items)
        completed = sum(1 for item in self.items if item.completed)
        pending = total - completed
        
        if total == 0:
            completion_rate = 0
        else:
            completion_rate = (completed / total) * 100
        
        return {
            "total": total,
            "completed": completed, 
            "pending": pending,
            "completion_rate": completion_rate
        }

def print_menu():
    """Print the main menu"""
    print("\n" + "="*50)
    print("🔥 TODO LIST MANAGER")
    print("="*50)
    print("1. ➕ Add new task")
    print("2. 📋 List all tasks")
    print("3. ✅ Mark task complete")
    print("4. ↩️  Mark task incomplete") 
    print("5. 🗑️ Remove task")
    print("6. 🧹 Clear completed tasks")
    print("7. 📊 Show statistics")
    print("8. 🚪 Exit")
    print("="*50)

def main():
    """Main function to run the todo list application"""
    todo = TodoList()
    
    print("🎉 Welcome to Todo List Manager!")
    
    while True:
        print_menu()
        
        try:
            choice = input("👉 Enter your choice (1-8): ").strip()
            
            if choice == "1":
                task_desc = input("📝 Enter task description: ").strip()
                todo.add_task(task_desc)
                
            elif choice == "2":
                todo.list_tasks()
                
            elif choice == "3":
                todo.list_tasks(show_completed=False)
                if any(not item.completed for item in todo.items):
                    try:
                        index = int(input("Enter task number to complete: "))
                        todo.complete_task(index)
                    except ValueError:
                        print("Error: Please enter a valid number")
                        
            elif choice == "4":
                completed_tasks = [item for item in todo.items if item.completed]
                if completed_tasks:
                    todo.list_tasks()
                    try:
                        index = int(input("Enter task number to reopen: "))
                        todo.uncomplete_task(index)
                    except ValueError:
                        print("Error: Please enter a valid number")
                else:
                    print("No completed tasks to reopen!")
                    
            elif choice == "5":
                todo.list_tasks()
                if todo.items:
                    try:
                        index = int(input("Enter task number to remove: "))
                        todo.remove_task(index)
                    except ValueError:
                        print("Error: Please enter a valid number")
                        
            elif choice == "6":
                todo.clear_completed()
                
            elif choice == "7":
                stats = todo.get_stats()
                print(f"\n📊 TODO STATISTICS")
                print("-" * 30)
                print(f"Total tasks: {stats['total']}")
                print(f"Completed: {stats['completed']}")
                print(f"Pending: {stats['pending']}")
                print(f"Completion rate: {stats['completion_rate']:.1f}%")
                
            elif choice == "8":
                print("👋 Goodbye! Stay productive!")
                break
                
            else:
                print("❌ Invalid choice. Please select 1-8.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    main()
