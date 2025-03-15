import random
import json
import os

XP_FILE = "data/progress.json"

class DungeonSim:
    def __init__(self):
        self.load_progress()



    

    def load_progress(self):
        if not os.path.exists(XP_FILE):
            self.progress = {"xp": 0, "level": 1, "streak": 0}
            self.save_progress()
        else:
            try:
                with open(XP_FILE, "r") as file:
                    self.progress = json.load(file)
            except json.decoder.JSONDecodeError:
                pass

    def save_progress(self):
        with open(XP_FILE, "w") as file:
            json.dump(self.progress, file, indent=4)

    def gain_experience(self):
        self.progress["xp"] += 10
        self.progress["streak"] += 1
        if self.progress["xp"] >= self.progress["level"] * 50:
            self.progress["level"] += 1
            print(f"Level up! Now level {self.progress['level']}")
        if random.random() < 0.2:
            print("You found a loot item!")
        self.save_progress()