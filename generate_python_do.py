import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import datetime

class ToDoApp:
    """
    A simple to-do list application built using Tkinter.
    """

    def __init__(self, master):
        """Initializes the to-do list application."""
        self.master = master
        master.title("To-Do List")

        self.tasks = []  # List to store to-do items

        # UI elements
        self.task_entry = ttk.Entry(master, width=30)
        self.task_entry.pack(pady=5)

        self.due_date_entry = ttk.Entry(master, width=15)
        self.due_date_entry.pack(pady=2)
        self.due_date_label = ttk.Label(master, text="Due Date (YYYY-MM-DD):")
        self.due_date_label.pack()


        self.add_button = ttk.Button(master, text="Add Task", command=self.add_task)
        self.add_button.pack(pady=5)

        self.task_listbox = tk.Listbox(master, selectmode="SINGLE", width=40)
        self.task_listbox.pack(pady=10)

        self.remove_button = ttk.Button(master, text="Remove Task", command=self.remove_task)
        self.remove_button.pack(pady=5)

        self.complete_button = ttk.Button(master, text="Mark as Complete", command=self.mark_complete)
        self.complete_button.pack(pady=5)

        self.update_listbox()


    def add_task(self):
        """Adds a new task to the to-do list."""
        task = self.task_entry.get().strip()
        due_date = self.due_date_entry.get().strip()

        if not task:
            messagebox.showerror("Error", "Please enter a task.")
            return

        try:
            if due_date:
                datetime.datetime.strptime(due_date, '%Y-%m-%d') #Validate date format
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")
            return


        new_task = {"task": task, "completed": False, "due_date": due_date}
        self.tasks.append(new_task)
        self.task_entry.delete(0, tk.END)
        self.due_date_entry.delete(0, tk.END)
        self.update_listbox()

    def remove_task(self):
        """Removes a selected task from the to-do list."""
        try:
            selection = self.task_listbox.curselection()[0]
            del self.tasks[selection]
            self.update_listbox()
        except IndexError:
            messagebox.showwarning("Warning", "Please select a task to remove.")

    def mark_complete(self):
        """Marks a selected task as complete."""
        try:
            selection = self.task_listbox.curselection()[0]
            self.tasks[selection]["completed"] = not self.tasks[selection]["completed"]
            self.update_listbox()
        except IndexError:
            messagebox.showwarning("Warning", "Please select a task to mark as complete.")

    def update_listbox(self):
        """Updates the listbox with the current to-do items."""
        self.task_listbox.delete(0, tk.END)
        for i, task in enumerate(self.tasks):
            status = "[x]" if task["completed"] else "[ ]"
            due_date_str = f" (Due: {task['due_date']})" if task['due_date'] else ""
            self.task_listbox.insert(i, f"{status} {task['task']}{due_date_str}")


root = tk.Tk()
app = ToDoApp(root)
root.mainloop()

