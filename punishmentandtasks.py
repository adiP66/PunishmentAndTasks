import datetime
import os
from pushups import count_pushups

def load_tasks(file_path):
    tasks = {}
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            for line in file:
                index, task, status = line.strip().split(": ", 2)
                tasks[int(index)] = (task, status)
    return tasks

def save_tasks(file_path, tasks):
    with open(file_path, "w") as file:
        for index, (task, status) in tasks.items():
            file.write(f"{index}: {task}: {status}\n")

def add_tasks(tasks):
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
    return tasks

def view_tasks(tasks):
    if not tasks:
        print("No tasks available.")
    else:
        for index, (task, status) in tasks.items():
            print(f"************** {index}) {task}: {status} ***************")

def delete_task(tasks):
    task_to_delete = int(input("Enter the task index to delete: "))
    if task_to_delete in tasks:
        del tasks[task_to_delete]
        print(f"Task {task_to_delete} deleted.")
    else:
        print("Task not found.")
    return tasks

def update_task_status(tasks):
    task_to_update = int(input("Enter the task index to update: "))
    if task_to_update in tasks:
        new_status = input("Enter the new status: ")
        tasks[task_to_update] = (tasks[task_to_update][0], new_status)
        print(f"Task {task_to_update} updated to '{new_status}'.")
    else:
        print("Task not found.")
    return tasks

def view_pending_punishment(root_directory):
    punishment = 0
    files_to_update = []
    today = datetime.date.today().strftime("%d-%m-%Y")
    
    for dirpath, _, filenames in os.walk(root_directory):
        if os.path.basename(dirpath) >= today:
            continue
        for filename in filenames:
            if filename.endswith(".txt"):
                file_path = os.path.join(dirpath, filename)
                tasks = load_tasks(file_path)
                for index, (task, status) in tasks.items():
                    if status == 'Not Done':
                        punishment += 50
                        tasks[index] = (task, 'Done')
                if punishment > 0:
                    files_to_update.append((file_path, tasks))
    
    if punishment > 0:
        print(f"\n**********{punishment} pushups!!!************")
        return punishment
    else:
        print("\nNo pending punishment.\n")




def main():
    today = datetime.date.today()
    date_string = today.strftime("%d-%m-%Y")
    directory_path = f"C:/Users/aditya/Desktop/PunishmentAndTasks/tasksfolder/{date_string}"
    root_directory = "C:/Users/aditya/Desktop/PunishmentAndTasks/tasksfolder"
    file_path = f"{directory_path}/{date_string}.txt"
    punishment = view_pending_punishment(root_directory)

    os.makedirs(directory_path, exist_ok=True)

    tasks = load_tasks(file_path)

    while True:
        try:
            choose = int(input("Enter: \n1/ To add tasks \n2/ To view tasks \n3/ To delete a task \n4/ To update the status of a task \n5/ To exit\n6/ View pending punishment\n7/ Begin your punishment\n"))
             
            if choose == 1:
                tasks = add_tasks(tasks)
            elif choose == 2:
                view_tasks(tasks)
            elif choose == 3:
                tasks = delete_task(tasks)
            elif choose == 4:
                tasks = update_task_status(tasks)
            elif choose == 5:
                break   
            elif choose == 6:
                view_pending_punishment(root_directory)
            elif choose == 7:
                pushup_count  = count_pushups(punishment)
                punishment -= pushup_count
                print(f"You completed {pushup_count} push-ups. Remaining punishment: {punishment}")
            else:
                print("Invalid choice. Please try again.")

            save_tasks(file_path, tasks)
        except ValueError as e:
            print('\n*********Invalid input! Please enter a number.**************')
        except Exception as e:
            print('\n*********An error occurred!**************', e)

if __name__ == "__main__":
    main()
