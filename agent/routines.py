import os
import datetime
import json


class RoutinesManager:
    def __init__(self, filepath) -> None:
        self.filepath = filepath
        self.routines = []
        self.reset_routines()

    def tick_route(self, timestamp):
        timestamp_ftime = datetime.datetime.strptime(timestamp, "%H:%M")
        remaining_routines = []
        routine_todo = None
        for routine in self.routines:
            routine_time = routine["time"]
            routine_time_obj = datetime.datetime.strptime(routine_time, "%H:%M")
            if routine_time_obj.strftime("%H:%M") > timestamp_ftime:
                remaining_routines.append(routine)
            else:
                routine_todo = remaining_routines
        self.routines = remaining_routines
        return routine_todo

    def add_routine(self, routine_name, routine_time):
        with open(self.filepath, "r", encoding='utf-8') as file:
            data = json.load(file)
        data.append({"action": routine_name, "time": routine_time})

        with open(self.filepath, "w", encoding='utf-8') as file:
            json.dump(data, file)

    def del_routine(self, action, time=None):
        with open(self.filepath, "r", encoding='utf-8') as file:
            data = json.load(file)

        if time is None:
            # Delete all entries with given action
            data = [entry for entry in data if entry["action"] != action]
        else:
            # Find the closest timestamp for the given action
            closest_entry = None
            closest_time_diff = float('inf')
            for entry in data:
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
                data.remove(closest_entry)

        with open(self.filepath, "w", encoding='utf-8') as file:
            json.dump(data, file)

    def reset_routines(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, "r", encoding='utf-8') as file:
                data = json.load(file)
            self.routines = data
        else:
            return []
