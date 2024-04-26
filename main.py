import os
import json
import datetime

from mistralai.client import MistralClient

from agent.agent import Agent

def cutoff_fun(log_filepath, out_filepath, cutoff_str, max_num_days=3):
    with open(log_filepath, "r", encoding='utf-8') as file:
        data = json.load(file)
    out_content = data[-max_num_days:-max_num_days+2]
    cutoff_obj = datetime.datetime.strptime(cutoff_str, "%H:%M")
    last_day = []
    for day_entry in data[-1]:
        day_time_obj = datetime.datetime.strptime(day_entry['time'], "%H:%M")
        if day_time_obj > cutoff_obj:
            break
        last_day.append(day_entry)
    out_content.append(last_day)
    with open(out_filepath, "w", encoding='utf-8') as file:
        json.dump(out_content, file, indent=4)

if __name__ == "__main__":
    api_key = os.environ["MISTRAL_API_KEY"]
    model = "mistral-large-latest"
    log_filepath = "data/logs/activitylog_uci_detailed_labour_xes8.json"
    new_log_filepath = "data/logs/log.json"

    for k in range(10):
        print(f"{str(10+k)}:00")
        client = MistralClient(api_key=api_key)
        cutoff_fun(log_filepath, new_log_filepath, f"{str(10+k)}:00", max_num_days=3)
        agent = Agent(model_name=model, client=client, log_path=new_log_filepath)
        action = agent.tick(f"{str(10+k)}:00")
        print(f'Current action: {action}')
