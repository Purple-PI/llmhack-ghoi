import json
import os

from mistralai.client import MistralClient
from prompts.fun_prompt import classification, feedback_todo, feedback_todo_classification, feedback_register, feedback_register_classification, auto_evaluation

EXAMPLE_FILENAME = "example.json"
TIME_CUTOFF = 1800

model_name = "mistral-large-latest"

client = MistralClient(
                        api_key=os.environ.get("MISTRAL_API_KEY"),
                    )

with open(EXAMPLE_FILENAME, 'r') as file_json:
    example_content = json.load(file_json)

format_content = []
for k, day_dict_list in enumerate(example_content):
    day_str_list = []
    for day_entry in day_dict_list:
        timestamp = int(day_entry['timestamp'].replace(':',''))
        if (k==2 and timestamp < TIME_CUTOFF) or k < 2:
            format_str = f"{day_entry['timestamp']}: {day_entry['observation']}"
            day_str_list.append(format_str)
    activity_log = "\n".join(day_str_list)
    format_content.append(activity_log)

entry = {"logs_pp_day": format_content[0], "logs_p_day": format_content[1], "logs_current_day": format_content[2]}
entry['time'] = '18:30'
entry['action'] = 'Prepare dinner'
entry['answer'] = "Why ? That does not make any sense."

print("test_classification")
inputs = classification(**entry)

print("test_todo")
inputs = feedback_todo(**entry)
print()

print("test_todo_classification")
inputs = feedback_todo_classification(**entry)
response = client.chat(
            model=model_name,
            **inputs
        )
text = response.choices[0].message.content
tool_call = response.choices[0].message.tool_calls[0]
function_name = tool_call.function.name

print(text)
print(function_name)
print()

print("test_register")
inputs = feedback_register(**entry)
print()

print("test_register_classification")
inputs = feedback_register_classification(**entry)
print()

print("test_auto_evaluation")
inputs = auto_evaluation(**entry)
print()