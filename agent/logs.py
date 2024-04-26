import datetime
import json


class LogsManager:
    def __init__(self, filepath) -> None:
        self.filepath = filepath
        with open(self.filepath, "r", encoding='utf-8') as file:
            self.data = json.load(file)

    def add_event(self, time, event):
        self.data[-1].append({"event": event, "time": time})

    def cutoff_fun(self, cutoff_str, max_num_days=3):
        out_content = self.data[-max_num_days:-1]
        cutoff_obj = datetime.datetime.strptime(cutoff_str, "%H:%M")
        last_day = []
        for day_entry in self.data[-1]:
            day_time_obj = datetime.datetime.strptime(day_entry['time'], "%H:%M")
            if day_time_obj > cutoff_obj:
                break
            last_day.append(day_entry)
        out_content.append(last_day)
        self.data = out_content

    def get_logs(self, max_num_days=3):
        format_content = []
        for day_dict_list in self.data[-max_num_days:]:
            day_str_list = []
            for day_entry in day_dict_list:
                format_str = f"{day_entry['time']}: {day_entry['event']}"
                day_str_list.append(format_str)
            activity_log = "\n".join(day_str_list)
            format_content.append(activity_log)
        return self.data, format_content
