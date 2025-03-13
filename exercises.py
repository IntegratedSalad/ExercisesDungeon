import json
import os

DATA_FILE = "data/exercises.json"

class ExerciseManager:
    def __init__(self):
        self.data = []
        self.load_data()

    def load_data(self):
        if not os.path.exists(DATA_FILE):
            self.save_data()
        else:
            try:
                with open(DATA_FILE, "r") as file:
                    self.data = json.load(file)
            except json.decoder.JSONDecodeError:
                pass

    def save_data(self):
        with open(DATA_FILE, "w") as file:
            json.dump(self.data, file, indent=4)

    def log_exercise(self, name, reps):
        self.data.append({"exercise": name, "reps": reps})
        self.save_data()
        