import datetime
import os
import psycopg2
from pushups import count_pushups

# Database configuration
DB_NAME = "task_manager"
DB_USER = "postgres"
DB_PASSWORD = "admin"
DB_HOST = "localhost"
DB_PORT = "5432"

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

def add_tasks(tasks, date):
    while True:
        user_input = input("Enter the tasks that you are going to perform (or type 'exit()' to finish): ").split()
        if not user_input:
            print("Enter some tasks!")
            continue
        if user_input[0].lower() == "exit()":
            break
        for task in user_input:
            index = max(tasks.keys(), default=0) + 1
            tasks[index] = (task, 'Not Done')
    save_tasks(tasks, date)
    return tasks

def view_tasks(tasks):
    if not tasks:
        print("No tasks available.")
    else:
        for index, (task, status) in tasks.items():
            print(f"************** {index}) {task}: {status} ***************")

def delete_task(tasks, date):
    try:
        task_to_delete = int(input("Enter the task index to delete: "))
        if task_to_delete in tasks:
            del tasks[task_to_delete]
            conn = connect_to_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = %s", (task_to_delete,))
            conn.commit()
            cursor.close()
            conn.close()
            print(f"Task {task_to_delete} deleted.")
        else:
            print("Task not found.")
    except ValueError:
        print("Invalid input. Please enter a valid task index.")
    return tasks

def update_task_status(tasks, date):
    try:
        task_to_update = int(input("Enter the task index to update: "))
        if task_to_update in tasks:
            new_status = input("Enter the new status: ")
            tasks[task_to_update] = (tasks[task_to_update][0], new_status)
            conn = connect_to_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE tasks SET status = %s WHERE id = %s", (new_status, task_to_update))
            conn.commit()
            cursor.close()
            conn.close()
            print(f"Task {task_to_update} updated to '{new_status}'.")
        else:
            print("Task not found.")
    except ValueError:
        print("Invalid input. Please enter a valid task index.")
    return tasks

def view_pending_punishment():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'Not Done' AND date < CURRENT_DATE")
    uncompleted_tasks = cursor.fetchone()[0]
    punishment = uncompleted_tasks * 2
    cursor.close()
    conn.close()

    if punishment > 0:
        print(f"\n**********{punishment} pushups!!!************")
        return punishment
    else:
        print("\nNo pending punishment.\n")

def delete_prior_day_tasks():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE date < CURRENT_DATE")
    conn.commit()
    cursor.close()
    conn.close()

def main():
    today = datetime.date.today()
    date_string = today.strftime("%d-%m-%Y")
    punishment = view_pending_punishment()

    tasks = load_tasks(date_string)

    while True:
        try:
            choose = int(input("Enter: \n1/ To add tasks \n2/ To view tasks \n3/ To delete a task \n4/ To update the status of a task \n5/ To exit\n6/ View pending punishment\n7/ Begin your punishment\n"))

            if choose == 1:
                tasks = add_tasks(tasks, date_string)
            elif choose == 2:
                view_tasks(tasks)
            elif choose == 3:
                tasks = delete_task(tasks, date_string)
            elif choose == 4:
                tasks = update_task_status(tasks, date_string)
            elif choose == 5:
                break
            elif choose == 6:
                view_pending_punishment()
            elif choose == 7:
                pushup_count = count_pushups(punishment)
                punishment -= pushup_count
                print(f"You completed {pushup_count} push-ups. Remaining punishment: {punishment}")
                if punishment <= 0:
                    delete_prior_day_tasks()
                    print("Prior day's tasks have been deleted.")
            else:
                print("Invalid choice. Please try again.")

        except ValueError as e:
            print('\n*********Invalid input! Please enter a number.**************')
        except Exception as e:
            print('\n*********An error occurred!**************', e)

if __name__ == "__main__":
    main()
