
import os
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import functools
import datetime

import json
PTCLS = 'a{}b{}'
def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

class Agent:
    
    def __init__(self, model_name, client):
        self.client = client
        self.model_name = model_name
        self.file_path = 'routine.json'
        self.log_path = 'logs.json'
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "add_routine",
                    "description": "Add a routine to the calendar",
                    "parameters": {
                         "type": "object",
                         "properties": {
                             "routine_name": {
                                 "type": "string",
                                 "description": "name of the routine to add",
                             },
                             "routine_time": {
                                 "type": "string",
                                 "description": "time to exectute routine",
                             }
                         },
                         "required": ["routine_name", "routine_time"],
                    },}
            },
            {
                "type": "function",
                "function": {
                    "name": "del_routine",
                    "description": "Delete a routine from the calendar",
                    "parameters": {
                         "type": "object",
                         "properties": {
                             "routine_name": {
                                 "type": "string",
                                 "description": "name of the routine to delete",
                             },
                             "routine_time": {
                                 "type": "string",
                                 "description": "time to exectute routine",
                             }
                         },
                         "required": ["routine_name"],
                    },}
            },
            {
                "type": "function",
                "function": {
                    "name": "do_nothing",
                    "description": "do nothing",
                    "parameters": {},}
            }
            ]

        self.names_to_functions = {
        'add_routine': functools.partial(self.add_routine),
        'del_routine': functools.partial(self.del_routine),
        'do_nothing': functools.partial(self.do_nothing),

        }
        self.api(messages = "Can you add make me a coffee every morning at 10:00? ")
        #self.loop()

    def do_nothing(self):
        pass

    def load_next_routine(self):
        current_time = datetime.datetime.now().strftime("%H:%M")  # Current time in "HH:MM" format
        routines = self.get_routine()
        next_routine = None
        min_time_diff = float('inf')
        for routine in routines:
            routine_time = routine["time"]
            routine_time_obj = datetime.datetime.strptime(routine_time, "%H:%M")
            if routine_time_obj.strftime("%H:%M") >= current_time:
                time_diff = (routine_time_obj - datetime.datetime.strptime(current_time, "%H:%M")).total_seconds()
                if time_diff < min_time_diff:
                    min_time_diff = time_diff
                    next_routine = routine
        return next_routine
    
    def next_routine(self):
        routine = self.load_next_routine()
        prompt = PTCLS.format(**routine)
        response = self.api(prompt)


    def identify_tool(self, logs):
        "STEP 1 : identify tool to use"
        log_text = flatten_dict(logs)
        # prompt_for_api = .format(log_text)
        response = self.api(messages=prompt_for_api)
        tool_call = response.choices[0].message.tool_calls[0]
        return tool_call.function_name
        

    def loop(self):
        # get logs from previous days
        logs = self.get_logs()
        # Prompt classification (should call a fct ?)
        prompt = self.model_action_cls(logs)
        
        # check if tool_name, time is in th routine
        # If yes=> Prompt feedback
        user_response = self.ask_user_tool(tool_name, time)
        tool_name, time = self.prompt_feedback(user_response)
        user_response = self.ask_user_register(tool_name, time)
        # enregistrer action?
        pass
    
    def get_logs(self):
        if os.path.exists(self.log_path):
            with open(self.log_path, "r") as file:
                data = json.load(file)
            return data
        else:
            return []

    
    def ask_user(self, message):
        # get user answer
        return message



    def fct_call(self, message):
        tool_call = message.choices[0].message.tool_calls[0]
        function_result = self.names_to_functions[tool_call.function_name]
        


        
    def user_tool_request(self, messages):
        response = self.api(messages=messages)
        tool_call = response.choices[0].message.tool_calls[0]
        while tool_call == None:
            # 'request for parameters'
            messages.append(ChatMessage(role="assistant", content=response.choices[0].message.content))
            messages.append(ChatMessage(role="user", content= self.get_user_response()))
        else:
            print(response)  
            function_name = tool_call.function.name
            function_params = json.loads(tool_call.function.arguments)
            print("\nfunction_name: ", function_name, "\nfunction_params: ", function_params)
            function_result = self.names_to_functions[function_name](**function_params)
            
    def get_user_response(self, message):
        return 

    def api(self, messages):
        messages = [ChatMessage(role="user", content=messages)]
        response = client.chat(
            model=self.model_name,
            messages=messages,
            tools=self.tools,
            tool_choice="auto"
        )
        return response
        
    def add_routine(self, routine_name, routine_time):
        with open(self.file_path, "r") as file:
            data = json.load(file)
        data.append({"action": routine_name, "time": routine_time})

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
                    # Convert time strings to datetime objects for comparison
                    entry_time_obj = datetime.datetime.strptime(entry_time, "%H:%M")
                    time_obj = datetime.datetime.strptime(time, "%H:%M")
                    time_diff = abs((entry_time_obj - time_obj).total_seconds())
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



if __name__ == "__main__":
    api_key = os.environ["MISTRAL_API_KEY"]
    model = "mistral-large-latest"
    client = MistralClient(api_key=api_key)
    agent = Agent(model_name=model, client=client)
