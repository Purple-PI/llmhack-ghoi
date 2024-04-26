import datetime

from prompts.fun_prompt import classification, feedback_register, feedback_register_classification, feedback_todo, feedback_todo_classification, query, auto_evaluation
from agent.routines import RoutinesManager

class Agent:
    def __init__(self, model_name, client, logs):
        self.client = client
        self.model_name = model_name
        self.file_path = 'data/routines.json'
        self.logs = logs
        self.timestamp = datetime.datetime.strptime("00:00", "%H:%M")
        #load routines once a day
        self.routines = RoutinesManager(self.file_path)
        self.states = {"state0": {}, "state1": {}, "state2": {}, "state3": {}}
    
    def tick(self, timestamp):
        self.timestamp = datetime.datetime.strptime(timestamp, "%H:%M")
        self.states = {"state0": {}, "state1": {}, "state2": {}, "state3": {}}
        return self._tick_trigger()

    def classification_fn(self, logs, time):
        "STEP 1: LLM prediction of next useful action"
        entry = {"logs_pp_day": logs[-3], "logs_p_day": logs[-2], "logs_day": logs[-1], "time": time}
        params = classification(**entry)
        response = self.api(**params)
        if response.choices[0].message.tool_calls:
            tool_call = response.choices[0].message.tool_calls[0]
            return tool_call.function.name
        else:
            return "do_nothing"
    
    def feedback_todo_fn(self, logs, action):
        "STEP 2: ask a confirmation to execute action to user"
        entry = {"logs_day": logs[-1], "action": action}
        params = feedback_todo(**entry)
        response = self.api(**params)
        return response.choices[0].message.content
    
    def feedback_todo_classification_fn(self, action, answer):
        "STEP 3: classify user answer regarding execution of action"
        entry = {"action": action, "answer": answer}
        params = feedback_todo_classification(**entry)
        response = self.api(**params)
        tool_call = response.choices[0].message.tool_calls[0]
        return tool_call.function.name

    def feedback_register_fn(self, logs, action, output, user_input):
        "STEP 4: ask a confirmation to register action to user"
        entry = {"logs_day": logs[-1], "action": action, 'output': output, 'user_input':user_input }
        params = feedback_register(**entry)
        response = self.api(**params)
        return response.choices[0].message.content

    def feedback_register_classification_fn(self, action, answer):
        "STEP 5: classify user answer regarding storage of automatic task"
        entry = {"action": action, "user_input": answer}
        params = feedback_register_classification(**entry)
        response = self.api(**params)
        tool_call = response.choices[0].message.tool_calls[0]
        return tool_call.function.name
    
    def auto_evaluation(self, logs_autotask, logs, action, timestamp):
        "Check if auto task should be executed."
        entry = {"logs_autotask": logs_autotask, "logs_day": logs[-1], "action":action, "time": timestamp}
        params = auto_evaluation(**entry)
        response = self.api(**params)
        tool_call = response.choices[0].message.tool_calls[0]
        return tool_call.function.name

    def query(self, user_input, time):
        "Query a modification to routines following user_input"
        entry = {"user_input": user_input, "time": time}
        params = feedback_register_classification(**entry)
        response = self.api(**params)
        tool_call = response.choices[0].message.tool_calls[0]
        return tool_call.function_name
    
    def _tick_trigger(self):
        # get logs from previous days
        logs, formatted_logs = self.logs.get_logs()
        str_timestamp = self.timestamp.strftime("%H:%M")
        action = self.routines.tick_routine(self.timestamp)
        if action != None:
            action_to_execute = self.auto_evaluation(logs[-1], formatted_logs, action, str_timestamp)
        action_to_execute = self.classification_fn(formatted_logs, str_timestamp)
        if action_to_execute != "do_nothing":
            self.states["state0"] = action_to_execute
        _, formatted_logs = self.logs.get_logs()
        action_to_execute = self.states["state0"]
        if action_to_execute:
            output_user = self.feedback_todo_fn(formatted_logs, action_to_execute)
            self.states["state1"] = {"action": action_to_execute, "output_user": output_user}
            return output_user
        else:
            return ""
    
    def input_user_0(self, input_user):
        _, formatted_logs = self.logs.get_logs()
        if self.states["state1"]:
            action_to_execute, output_user = self.states["state1"]['action'], self.states["state1"]['output_user']
            str_timestamp = self.timestamp.strftime("%H:%M")
            execute_action = self.feedback_todo_classification_fn(action_to_execute, input_user)
            if execute_action == "yes":
                self.logs.add_event(str_timestamp, action_to_execute)
            output_user = self.feedback_register_fn(formatted_logs, action_to_execute, output_user, input_user)
            return output_user
        return ""

    def input_user_1(self, input_user):
        str_timestamp = self.timestamp.strftime("%H:%M")
        if self.states["state1"]:
            action = self.states["state1"]['action']
            register_action = self.feedback_register_classification_fn(action, input_user)
            if register_action == 'yes':
                #TO UPDATE: replace parameters with the one from tools
                self.routines.add_routine(action, str_timestamp, self.logs.data[-1])

    def user_direct_request(self, user_input):
        resp = self.query(user_input, self.timestamp)
        # feedback routines

    def api(self, **params):
        response = self.client.chat(
            model=self.model_name,
            **params
        )
        return response
