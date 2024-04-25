
import os
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import functools
import datetime

import json

class Agent:
    
    def __init__(self, model_name, client):
        self.client = client
        self.model_name = model_name
        self.file_path = 'logs.json'

        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "coffee",
                    "description": "Make a coffee",
                    # "parameters": {
                    #     "type": "object",
                    #     "properties": {
                    #         "transaction_id": {
                    #             "type": "string",
                    #             "description": "The transaction id.",
                    #         }
                    #     },
                    },
            }]

        self.names_to_functions = {
        'function_name': functools.partial(self.make_coffee)
        }
        self.add_routine(action = 'make coffee', time = datetime.datetime.now().timestamp())
        self.add_routine(action = 'make coffee1', time = datetime.datetime.now().timestamp())
        self.add_routine(action = 'make coffee2', time = datetime.datetime.now().timestamp())


    def generate(self, x):
        messages = [ChatMessage(role="user", content=x)]
        response = client.chat(
            model=self.model_name,
            messages=messages,
            tools=self.tools,
            tool_choice="auto"
        )
        print(response)

    def add_routine(self, action, time):
        with open(self.file_path, "r") as file:
            data = json.load(file)
        data.append({"action": action, "time": time})

        with open(self.file_path, "w") as file:
            json.dump(data, file)

    def del_routine(self, action, time=None):
        with open(self.file_path, "r") as file:
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
                    time_diff = abs(entry_time - time)
                    if time_diff < closest_time_diff:
                        closest_entry = entry
                        closest_time_diff = time_diff
            if closest_entry:
                data.remove(closest_entry)

        with open(self.file_path, "w") as file:
            json.dump(data, file)

    def get_routine(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as file:
                data = json.load(file)
            return data
        else:
            return []

    def make_coffee(self):
        print("I am making a coffee")


if __name__ == "__main__":
    api_key = os.environ["MISTRAL_API_KEY"]
    model = "mistral-large-latest"
    client = MistralClient(api_key=api_key)
    agent = Agent(model_name=model, client=client)

