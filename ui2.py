import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
from tkcalendar import Calendar

DATA_FILE = "data/exercises.json"
HISTORY_FILE = "data/history.json"

class ExerciseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Exercise Dungeon")
        self.root.geometry("800x500")

        self.exercises = []  # Store added exercises
        self.history = {}  # Store exercise history
        self.load_exercises()
        self.load_history()

        self.create_widgets()

        self.current_date = datetime.today().date()
        print(self.current_date)

    def create_widgets(self):
        # Notebook for different views
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both")

        # Tabs
        self.exercise_tab = ttk.Frame(self.notebook)
        self.calendar_tab = ttk.Frame(self.notebook)
        self.battle_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.exercise_tab, text="Add Exercise")
        self.notebook.add(self.calendar_tab, text="Calendar")
        self.notebook.add(self.battle_tab, text="Battle")

        self.setup_exercise_tab()
        self.setup_calendar_tab()
        self.setup_battle_tab()
        self.update_exercise_list(self.exercise_listbox)
        self.update_exercise_list(self.available_exercises_listbox)

    def setup_exercise_tab(self):
        frame_left = tk.Frame(self.exercise_tab)
        frame_left.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)

        frame_right = tk.Frame(self.exercise_tab)
        frame_right.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Form Fields
        tk.Label(frame_left, text="Sheet ID:").pack(pady=5)
        self.sheet_id_entry = tk.Entry(frame_left)
        self.sheet_id_entry.pack(pady=5)

        tk.Label(frame_left, text="Exercise Name:").pack(pady=5)
        self.name_entry = tk.Entry(frame_left)
        self.name_entry.pack(pady=5)

        tk.Label(frame_left, text="Max Reps:").pack(pady=5)
        self.max_reps_entry = tk.Entry(frame_left)
        self.max_reps_entry.pack(pady=5)

        tk.Label(frame_left, text="Difficulty:").pack(pady=5)
        self.difficulty_var = tk.StringVar()
        self.difficulty_combobox = ttk.Combobox(frame_left, textvariable=self.difficulty_var)
        self.difficulty_combobox['values'] = ("Easy", "Medium", "Hard")
        self.difficulty_combobox.pack(pady=5)
        self.difficulty_combobox.current(0)

        # List of Exercises
        tk.Label(frame_right, text="Added Exercises:").pack()
        self.exercise_listbox = tk.Listbox(frame_right, width=30, height=10)
        self.exercise_listbox.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)

        self.add_button = tk.Button(frame_left, text="Add Exercise", command=self.add_exercise)
        self.add_button.pack(pady=10)

    def update_exercise_list(self, listbox_to_update):
        listbox_to_update.delete(0, tk.END)
        for exercise in self.exercises:
            entry = f"{exercise['name']} ({exercise['max_reps']} reps) - {exercise['difficulty']}"
            listbox_to_update.insert(tk.END, entry)
            if exercise['difficulty'] == "Easy":
                listbox_to_update.itemconfig(tk.END, {'bg': '#90ee90', 'fg': 'black'})
            elif exercise['difficulty'] == "Medium":
                listbox_to_update.itemconfig(tk.END, {'bg': '#ffffe0', 'fg': 'black'})
            elif exercise['difficulty'] == "Hard":
                listbox_to_update.itemconfig(tk.END, {'bg': '#ff7f7f', 'fg': 'black'})

    def update_date(self, date):
        self.current_date = self.calendar.get_date()

    def setup_calendar_tab(self):
        frame_top = tk.Frame(self.calendar_tab)
        frame_top.pack(fill=tk.X, padx=10, pady=10)

        self.calendar = Calendar(frame_top, selectmode='day', year=2025, month=3, day=13, date_pattern="y-mm-dd")
        self.calendar.bind("<<CalendarSelected>>", self.update_date)
        self.calendar.pack()

        frame_bottom = tk.Frame(self.calendar_tab)
        frame_bottom.pack(fill=tk.BOTH, expand=True)

        frame_left = tk.Frame(frame_bottom)
        frame_left.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.Y)
        frame_middle = tk.Frame(frame_bottom)
        frame_middle.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.Y)
        frame_right = tk.Frame(frame_bottom)
        frame_right.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.Y)

        tk.Label(frame_left, text="Available Exercises").pack()
        self.available_exercises_listbox = tk.Listbox(frame_left, width=30, height=10)
        self.available_exercises_listbox.pack()

        tk.Label(frame_middle, text="Reps Achieved").pack()
        self.reps_entry = tk.Entry(frame_middle)
        self.reps_entry.pack()
        self.commit_button = tk.Button(frame_middle, text="Commit Exercise", command=self.commit_exercise)
        self.commit_button.pack()
        self.commit_day_button = tk.Button(frame_middle, text="Commit Day", command=self.commit_day)
        self.commit_day_button.pack()

        tk.Label(frame_right, text="Exercises Done").pack()
        self.completed_exercises_listbox = tk.Listbox(frame_right, width=30, height=10)
        self.completed_exercises_listbox.pack(fill=tk.BOTH, expand=True)

    def setup_battle_tab(self):
        tk.Label(self.battle_tab, text="Battle Arena").pack(pady=10)
        tk.Label(self.battle_tab, text="Defeat enemies by staying consistent!").pack()

    def add_exercise(self):
        sheet_id = self.sheet_id_entry.get()
        name = self.name_entry.get()
        max_reps = self.max_reps_entry.get()
        difficulty = self.difficulty_var.get()
        
        if sheet_id and name and max_reps.isdigit():
            self.exercises.append({"sheet_id": sheet_id, "name": name, "max_reps": int(max_reps), "difficulty": difficulty})
            self.save_exercises()
            self.update_exercise_list(self.exercise_listbox)
            self.update_exercise_list(self.available_exercises_listbox)
        else:
            print("Invalid input. Please fill all fields correctly.")

    def commit_exercise(self):
        selected_date = self.calendar.get_date()
        reps = self.reps_entry.get()
        if reps.isdigit():
            if selected_date not in self.history:
                self.history[selected_date] = []
            self.history[selected_date].append({"reps": int(reps)})
            self.save_history()
            self.reps_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Input Error", "Please enter a valid number of reps.")

    def commit_day(self):
        pass

    def save_exercises(self):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, "w") as file:
            json.dump(self.exercises, file, indent=4)

    def save_history(self):
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
        with open(HISTORY_FILE, "w") as file:
            json.dump(self.history, file, indent=4)

    def load_exercises(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as file:
                self.exercises = json.load(file)

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r") as file:
                    self.history = json.load(file)
            except json.decoder.JSONDecodeError:
                pass

if __name__ == "__main__":
    root = tk.Tk()
    app = ExerciseApp(root)
    root.mainloop()
