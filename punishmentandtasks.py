import datetime
import os
import psycopg2
from pushups import count_pushups
from dotenv import load_dotenv
import tkinter as tk
from tkinter import messagebox, simpledialog

load_dotenv()

# Database configuration
DB_NAME = os.getenv("PGDATABASE")
DB_USER = os.getenv("PGUSER")
DB_PASSWORD = os.getenv("PGPASSWORD")
DB_HOST = os.getenv("PGHOST")
DB_PORT = os.getenv("PGPORT")

def connect_to_db():
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    return conn

def load_tasks(date):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, task, status FROM tasks WHERE date = %s", (date,))
    tasks = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}
    cursor.close()
    conn.close()
    return tasks

def save_tasks(tasks, date):
    conn = connect_to_db()
    cursor = conn.cursor()
    for index, (task, status) in tasks.items():
        cursor.execute("INSERT INTO tasks (id, task, status, date) VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO UPDATE SET task = %s, status = %s",
                       (index, task, status, date, task, status))
    conn.commit()
    cursor.close()
    conn.close()

def add_tasks(tasks, date, task_entry):
    task = task_entry.get()
    if task:
        index = max(tasks.keys(), default=0) + 1
        tasks[index] = (task, 'Not Done')
        save_tasks(tasks, date)
        task_entry.delete(0, tk.END)
        update_task_list(tasks)

def update_task_list(tasks):
    task_list.delete(0, tk.END)
    for index, (task, status) in tasks.items():
        task_list.insert(tk.END, f"{index}) {task}: {status}")

def delete_task(tasks, date, task_index):
    try:
        task_to_delete = int(task_index)
        if task_to_delete in tasks:
            del tasks[task_to_delete]
            conn = connect_to_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = %s", (task_to_delete,))
            conn.commit()
            cursor.close()
            conn.close()
            update_task_list(tasks)
        else:
            messagebox.showerror("Error", "Task not found.")
    except ValueError:
        messagebox.showerror("Error", "Invalid input. Please enter a valid task index.")

def update_task_status(tasks, date, task_index, new_status):
    try:
        task_to_update = int(task_index)
        if task_to_update in tasks:
            tasks[task_to_update] = (tasks[task_to_update][0], new_status)
            conn = connect_to_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE tasks SET status = %s WHERE id = %s", (new_status, task_to_update))
            conn.commit()
            cursor.close()
            conn.close()
            update_task_list(tasks)
        else:
            messagebox.showerror("Error", "Task not found.")
    except ValueError:
        messagebox.showerror("Error", "Invalid input. Please enter a valid task index.")

def view_pending_punishment():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'Not Done' AND date < CURRENT_DATE")
    uncompleted_tasks = cursor.fetchone()[0]
    punishment = uncompleted_tasks * 50
    cursor.close()
    conn.close()
    return punishment

def delete_prior_day_tasks():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE date < CURRENT_DATE")
    conn.commit()
    cursor.close()
    conn.close()

def on_right_click(event):
    try:
        selected_index = task_list.curselection()[0]
        task_id = task_list.get(selected_index).split(')')[0]
        if messagebox.askyesno("Delete Task", f"Do you want to delete task {task_id}?"):
            delete_task(tasks, date_string, task_id)
    except IndexError:
        messagebox.showerror("Error", "No task selected.")

def main():
    global task_list, tasks, date_string

    today = datetime.date.today()
    date_string = today.strftime("%Y-%m-%d")
    tasks = load_tasks(date_string)

    root = tk.Tk()
    root.title("Task Manager")

    task_entry = tk.Entry(root, width=50)
    task_entry.pack(pady=10)

    add_button = tk.Button(root, text="Add Task", command=lambda: add_tasks(tasks, date_string, task_entry))
    add_button.pack(pady=5)

    task_list = tk.Listbox(root, width=50, height=15)
    task_list.pack(pady=10)

    update_task_list(tasks)

    task_list.bind("<Button-3>", on_right_click)

  
    update_entry = tk.Entry(root, width=50)
    update_entry.pack(pady=10)

    status_entry = tk.Entry(root, width=50)
    status_entry.pack(pady=10)

    update_button = tk.Button(root, text="Update Task Status", command=lambda: update_task_status(tasks, date_string, update_entry.get(), status_entry.get()))
    update_button.pack(pady=5)

    punishment_button = tk.Button(root, text="View Pending Punishment", command=lambda: messagebox.showinfo("Pending Punishment", f"{view_pending_punishment()} pushups"))
    punishment_button.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
