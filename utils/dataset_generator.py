import argparse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import json
import numpy as np
import os


def string_to_datetime(str):
    return datetime.fromisoformat(str)


def extract_hour_from_date(date_time_obj):
    hour = date_time_obj.strftime("%H")
    minute = date_time_obj.strftime("%M")
    return f"{hour}:{minute}"



def remove_minutes_from_date(str, minutes_to_remove):
    return string_to_datetime(str) - timedelta(minutes=minutes_to_remove)

def add_minutes_from_date(str, minutes_to_remove):
    return string_to_datetime(str) + timedelta(minutes=minutes_to_remove)


def sort_and_merge_lists(A, B):
    # Iterate over each element in list B
    for b in B:
        # Find the correct position to insert b into list A
        insert_index = 0
        for a in A:
            if b["time"] < a["time"]:
                break
            insert_index += 1

        # Insert b into list A at the correct position
        A.insert(insert_index, b)

    return A

def write_dict_to_json_file(data_dict, filename):
    with open(filename, 'w') as json_file:
        json.dump(data_dict, json_file, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a dataset file.')

    parser.add_argument('filename', type=str, help='The filename to parse', default="activitylog_uci_detailed_labour.xes")
    args = parser.parse_args()
    filename = args.filename

    tree = ET.parse(filename)
    root = tree.getroot()

    ns = {'xes': 'http://www.xes-standard.org'}

    # Find all event elements

    #s = set()

    observations = [
        'sleeping',
        'eatingBreakfast',
        'prepareBreakfast',
        'toilet',
        'watchingtv',
        'grooming',
        'washing',
        'shower',
        'eatingLunch',
        'eatingDinner',
        'prepareLunch',
        'snack',
        'prepareDinner',
    ]

    'setalarm'
    'heatoven'
    'preparecoffee'
    'listeningmusic'
    'watchingtv'
    'readnews'
    'orderfood'



    traces = root.findall('.//xes:trace', namespaces=ns)

    memory = None
    last_name = None
    last_lifecycle = None
    add_after = None

    # Iterate over each event element
    for i, trace in enumerate(traces):
        logs = []
        events = root.findall('.//xes:event', namespaces=ns)
        for event in events:
            # Do something with each event element, for example, print its attributes
            for child in event:
                name = event.find('xes:string[@key="concept:name"]', namespaces=ns).attrib.get('value', '')
                lifecycle = event.find('xes:string[@key="lifecycle:transition"]', namespaces=ns).attrib.get('value', '')
                timestamp = event.find('xes:date[@key="time:timestamp"]', namespaces=ns).attrib.get('value', '')

                obs = {"event": name, "time": string_to_datetime(timestamp), "lifecycle": lifecycle}

                if name in observations and (len(logs) == 0 or (last_name != obs and last_lifecycle != lifecycle) ):
                    if name == "watchingtv" and lifecycle == "start":
                        memory = np.random.choice(["watchingtv", "listeningMusic"], p=[0.6, 0.4])
                        obs["event"] = memory
                        add_after = None
                    elif name == "watchingtv" and lifecycle == "complete":
                        obs["event"] = memory
                        add_after = None
                    if name == "prepareDinner" and lifecycle == "start":
                        memory = np.random.choice(["prepareDinner", "orderFood"], p=[0.75, 0.25])
                        obs["event"] = memory
                        add_after = None
                    elif name == "prepareDinner" and lifecycle == "complete":
                        obs["event"] = memory
                        add_after = None
                    if name == "prepareLunch" and lifecycle == "start":
                        memory = np.random.choice(["prepareLunch", "orderFood"], p=[0.9, 0.1])
                        obs["event"] = memory
                        add_after = None
                    elif name == "prepareLunch" and lifecycle == "complete":
                        obs["event"] = memory
                        add_after = None
                    elif name == "sleeping" and lifecycle == "start":
                        if np.random.random() < .9 and obs["time"].hour > 19 and obs["time"].hour < 5:
                            add_after = {"event": "setAlarm", "time": add_minutes_from_date(timestamp, np.random.randint(1, 5)), "lifecycle": "run"}
                    elif name == "prepareLunch" and lifecycle == "start" and np.random.random() < .75:
                        add_after = {"event": "heatOven", "time": add_minutes_from_date(timestamp, np.random.randint(1, 5)), "lifecycle": "run"}
                    elif name == "prepareDinner" and lifecycle == "start" and np.random.random() < .3:
                        add_after = {"event": "heatOven", "time": add_minutes_from_date(timestamp, np.random.randint(1, 5)), "lifecycle": "run"}
                    elif name == "prepareBreakfast" and lifecycle == "start":
                        if np.random.random() < .9:
                            add_after = {"event": "prepareCoffee", "time": add_minutes_from_date(timestamp, np.random.randint(1, 5)), "lifecycle": "run"}
                    else:
                        add_after = None
                    logs.append(obs)
                    if add_after is not None:
                        logs.append(add_after)
                    last_name = obs["event"]
                    last_lifecycle = obs["lifecycle"]

        for log in logs:
            log["time"] = extract_hour_from_date(log["time"])
        write_dict_to_json_file(logs, os.path.basename(filename) + str(i) + ".csv")
