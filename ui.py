import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
from tkcalendar import Calendar

DATA_FILE = "data/exercises.json"
HISTORY_FILE = "data/history.json"
INVENTORY_FILE = "data/inventory.json"

class ExerciseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Exercise Dungeon")
        self.root.geometry("800x500")

        self.exercises = []  # Store added exercises
        self.history = {}  # Store exercise history
        self.commited_exercises = []
        self.current_date = datetime.today().date()

        self.inventory = {}

        self.load_exercises()
        self.load_history()

        self.create_widgets()

        print(self.current_date)

    def create_widgets(self):
        # Notebook for different views
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both")

        # Tabs
        self.exercise_tab = ttk.Frame(self.notebook)
        self.calendar_tab = ttk.Frame(self.notebook)
        self.overview_tab = ttk.Frame(self.notebook)
        self.dungeonsim_tab = ttk.Frame(self.notebook)
        self.settings_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.exercise_tab, text="Add Exercise")
        self.notebook.add(self.calendar_tab, text="Calendar")
        self.notebook.add(self.overview_tab, text="Overview")
        self.notebook.add(self.dungeonsim_tab, text="Dungeon")
        self.notebook.add(self.settings_tab, text="Settings")

        self.setup_exercise_tab()
        self.setup_calendar_tab()
        self.setup_dungeonsim_tab()
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

        self.add_exercise_button = tk.Button(frame_left, text="Add Exercise", command=self.add_exercise)
        self.add_exercise_button.pack(pady=10)

        self.remove_exercise_button = tk.Button(frame_left, text="Remove Exercise", command=self.remove_exercise)
        self.remove_exercise_button.pack()

    def update_exercise_list(self, listbox_to_update):
        listbox_to_update.delete(0, tk.END)

        self.exercises = sorted(self.exercises, key=lambda x: x['sheet_id'])
        for exercise in self.exercises:
            entry = f"{exercise['sheet_id']}: {exercise['name']} ({exercise['max_reps']} reps) - {exercise['difficulty']}"
            listbox_to_update.insert(tk.END, entry)
            if exercise['difficulty'] == "Easy":
                listbox_to_update.itemconfig(tk.END, {'bg': '#90ee90', 'fg': 'black'})
            elif exercise['difficulty'] == "Medium":
                listbox_to_update.itemconfig(tk.END, {'bg': '#ffffe0', 'fg': 'black'})
            elif exercise['difficulty'] == "Hard":
                listbox_to_update.itemconfig(tk.END, {'bg': '#ff7f7f', 'fg': 'black'})

    def update_date(self, _):
        self.current_date = self.calendar.get_date()
        self.commit_day_button.config(state=tk.NORMAL)
        self.commit_exercise_button.config(state=tk.NORMAL)

        if (len(self.commited_exercises) <= 0):
            self.commit_day_button.config(state=tk.DISABLED)

        if (datetime.fromisoformat(self.current_date) > datetime.today()):
            self.commit_day_button.config(state=tk.DISABLED)
            self.commit_exercise_button.config(state=tk.DISABLED)

    def setup_calendar_tab(self):
        frame_top = tk.Frame(self.calendar_tab)
        frame_top.pack(fill=tk.X, padx=10, pady=10)

        self.calendar = Calendar(
            frame_top, 
            selectmode='day', 
            year=self.current_date.year, 
            month=self.current_date.month, 
            day=self.current_date.day, 
            date_pattern="y-mm-dd")
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
        self.commit_exercise_button = tk.Button(frame_middle, text="Commit Exercise", command=self.commit_exercise)
        self.commit_exercise_button.pack()
        self.uncommit_exercise_button = tk.Button(frame_middle, text="Uncommit Exercise", command=self.uncommit_exercise)
        self.uncommit_exercise_button.pack()
        self.commit_day_button = tk.Button(frame_middle, text="Commit Day", command=self.commit_day)
        self.commit_day_button.pack()
        self.commit_day_button.config(state=tk.DISABLED)

        tk.Label(frame_right, text="Exercises Done").pack()
        self.completed_exercises_listbox = tk.Listbox(frame_right, width=30, height=10)
        self.completed_exercises_listbox.pack(fill=tk.BOTH, expand=True)

    def setup_dungeonsim_tab(self):
        tk.Label(self.dungeonsim_tab, text="Battle Arena").pack(pady=10)
        tk.Label(self.dungeonsim_tab, text="Defeat enemies by staying consistent!").pack()

    def add_exercise(self):
        sheet_id = self.sheet_id_entry.get()
        name = self.name_entry.get()
        max_reps = self.max_reps_entry.get()
        difficulty = self.difficulty_var.get()
        
        if sheet_id and name and max_reps.isdigit():
            self.exercises.append({"sheet_id": sheet_id, "name": name, "max_reps": int(max_reps), "difficulty": difficulty})
            # TODO: Disallow for duplicate sheet_ids!!!
            self.save_exercises()
            self.update_exercise_list(self.exercise_listbox)
            self.update_exercise_list(self.available_exercises_listbox)
        else:
            print("Invalid input. Please fill all fields correctly.")

    def add_exercise_to_history(self, exercise):
        # Load existing history or create a new one
        date = exercise["date"]
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r") as file:
                    self.history = json.load(file)
            except json.decoder.JSONDecodeError:
                pass

        # Ensure the date exists in the history dictionary
        if date not in self.history:
            self.history[date] = []

        # Add the exercise entry
        self.history[date].append(exercise)

    def remove_exercise(self):
        exercise_selected = self.exercise_listbox.selection_get()
        print(exercise_selected)
        for e in self.exercises:
            if e["sheet_id"] == exercise_selected[0]:
                self.exercises.remove(e)
            self.update_exercise_list(self.exercise_listbox)
            self.update_exercise_list(self.available_exercises_listbox)
        self.save_exercises()

    def commit_exercise(self):
        selected_date = self.calendar.get_date()
        reps = self.reps_entry.get()
        if reps.isdigit():
            if selected_date not in self.history:
                self.history[selected_date] = []
            self.reps_entry.delete(0, tk.END)
            self.commit_day_button.config(state=tk.NORMAL)
            entry = self.available_exercises_listbox.selection_get() + f" reps done: {reps}"
            self.completed_exercises_listbox.insert(tk.END, entry)
            entry_in_list = None

            for e in self.exercises:
                if int(entry[:2].strip(':')) == int(e['sheet_id']):
                    entry_in_list = e
                    break

            if entry_in_list is None:
                return
            
            entry_in_list["repsdone"] = reps
            entry_in_list["date"] = selected_date
            self.commited_exercises.append(entry_in_list)
            
            if entry_in_list['difficulty'] == "Easy":
                self.completed_exercises_listbox.itemconfig(tk.END, {'bg': '#90ee90', 'fg': 'black'})
            elif entry_in_list['difficulty'] == "Medium":
                self.completed_exercises_listbox.itemconfig(tk.END, {'bg': '#ffffe0', 'fg': 'black'})
            elif entry_in_list['difficulty'] == "Hard":
                self.completed_exercises_listbox.itemconfig(tk.END, {'bg': '#ff7f7f', 'fg': 'black'})

        else:
            messagebox.showerror("Input Error", "Please enter a valid number of reps.")

    def uncommit_exercise(self):
        # find it by sheet id
        e = self.completed_exercises_listbox.selection_get()
        for idx, ce in enumerate(self.commited_exercises):
            if int(e[:2].strip(':')) == int(ce['sheet_id']):
                self.commited_exercises.remove(ce)
                self.completed_exercises_listbox.delete(idx, idx)

    def commit_day(self):
        for cex in self.commited_exercises:
            self.add_exercise_to_history(cex)
            print(cex)
        self.save_history()
        self.commited_exercises = []
        self.completed_exercises_listbox.delete(0, tk.END)

    def setup_dungeonsim_tab(self):
        frame_left = tk.Frame(self.dungeonsim_tab)
        frame_left.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        frame_right = tk.Frame(self.dungeonsim_tab)
        frame_right.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)

        # Player Info
        tk.Label(frame_right, text="Character").pack()
        
        # Paper Doll Equipment Slots
        self.equipment_slots = {
            "Ring": tk.StringVar(value="o"),
            "Armor": tk.StringVar(value="[ ]"),
            "Weapon": tk.StringVar(value="I"),
            "Boots": tk.StringVar(value="/ \\")
        }
        
        for slot, var in self.equipment_slots.items():
            frame = tk.Frame(frame_right)
            frame.pack()
            tk.Label(frame, text=f"{slot}: ").pack(side=tk.LEFT)
            ttk.Combobox(frame, textvariable=var, values=self.get_inventory_items(slot)).pack(side=tk.LEFT)
        
        self.name_label = tk.Label(frame_right, text="Name: Hero")
        self.name_label.pack()
        
        self.hp_var = tk.IntVar(value=100)
        self.mana_var = tk.IntVar(value=50)
        
        tk.Label(frame_right, text="HP:").pack()
        self.hp_bar = ttk.Progressbar(frame_right, orient="horizontal", length=150, mode="determinate", variable=self.hp_var, maximum=100)
        self.hp_bar.pack()

        tk.Label(frame_right, text="Mana:").pack()
        self.mana_bar = ttk.Progressbar(frame_right, orient="horizontal", length=150, mode="determinate", variable=self.mana_var, maximum=50)
        self.mana_bar.pack()

        self.exp_label = tk.Label(frame_right, text="XP: 0 / 100")
        self.exp_label.pack()
        self.level_label = tk.Label(frame_right, text="Level: 1")
        self.level_label.pack()
        self.armor_label = tk.Label(frame_right, text="Armor: 10")
        self.armor_label.pack()
        self.class_label = tk.Label(frame_right, text="Class: Warrior")
        self.class_label.pack()

        # Monster Info
        tk.Label(frame_left, text="Monster").pack()
        self.monster_name = tk.Label(frame_left, text="Slime")
        self.monster_name.pack()
        
        self.monster_hp_var = tk.IntVar(value=100)
        self.monster_mana_var = tk.IntVar(value=30)
        
        tk.Label(frame_left, text="HP:").pack()
        self.monster_hp_bar = ttk.Progressbar(frame_left, orient="horizontal", length=150, mode="determinate", variable=self.monster_hp_var, maximum=100)
        self.monster_hp_bar.pack()

        tk.Label(frame_left, text="Mana:").pack()
        self.monster_mana_bar = ttk.Progressbar(frame_left, orient="horizontal", length=150, mode="determinate", variable=self.monster_mana_var, maximum=30)
        self.monster_mana_bar.pack()
        
        self.monster_def_label = tk.Label(frame_left, text="Defense: 5")
        self.monster_def_label.pack()
        self.monster_level_label = tk.Label(frame_left, text="Level: 1")
        self.monster_level_label.pack()
        
        self.battle_log = tk.Text(frame_left, height=10, width=40, state=tk.DISABLED)
        self.battle_log.pack(fill=tk.BOTH, expand=True)
        
        self.execute_turn_button = tk.Button(frame_left, text="Execute Turn", command=self.execute_turn)
        self.execute_turn_button.pack()

    def get_inventory_items(self, slot):
        return self.inventory.get(slot, [self.equipment_slots[slot].get()])

    def load_inventory(self):
        if os.path.exists(INVENTORY_FILE):
            with open(INVENTORY_FILE, "r") as file:
                self.inventory = json.load(file)
        else:
            self.inventory = {"Ring": ["o"], "Armor": ["[ ]"], "Weapon": ["I"], "Boots": ["/ \\"]}

    def execute_turn(self):
        self.battle_log.insert(tk.END, "You attack the monster!\n")

    def save_exercises(self): # save available exercises after addition
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
