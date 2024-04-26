import os
import datetime
import json


class RoutinesManager:
    def __init__(self, filepath) -> None:
        self.filepath = filepath
        self.routines = []
        self.load_routines()

    def tick_routine(self, timestamp):
        timestamp_ftime = datetime.datetime.strftime(timestamp, "%H:%M")
        remaining_routines = []
        routine_todo = None
        for routine in self.routines:
            routine_time = routine["time"]
            routine_time_obj = datetime.datetime.strptime(routine_time, "%H:%M")
            if routine_time_obj.strftime("%H:%M") > timestamp_ftime:
                remaining_routines.append(routine)
            else:
                routine_todo = routine
        self.routines = remaining_routines
        return routine_todo

    def add_routine(self, routine_name, routine_time, logs_autotask):
        self.routines.append({"action": routine_name, "time": routine_time, "logs_autotask": logs_autotask})
        self.save_routines()

    def del_routine(self, action, time=None):
        if time is None:
            # Delete all entries with given action
            self.routines = [entry for entry in self.routines if entry["action"] != action]
        else:
            # Find the closest timestamp for the given action
            closest_entry = None
            closest_time_diff = float('inf')
            for entry in self.routines:
                if entry["action"] == action:
                    entry_time = entry["time"]
                    # Convert time strings to datetime objects for comparison
                    entry_time_obj = datetime.datetime.strptime(entry_time, "%H:%M")
                    time_obj = datetime.datetime.strptime(time, "%H:%M")
                    time_diff = abs((entry_time_obj - time_obj).total_seconds())
                    if time_diff < closest_time_diff:
                        closest_entry = entry
                        closest_time_diff = time_diff
            if closest_entry:
                self.routines.remove(closest_entry)
        self.save_routines()

    def load_routines(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, "r", encoding='utf-8') as file:
                data = json.load(file)
            self.routines = data
        else:
            return []

    def save_routines(self):
        with open(self.filepath, "w", encoding='utf-8') as file:
            json.dump(self.routines, file, indent=4)