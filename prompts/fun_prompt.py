import os
import json

from mistralai.models.chat_completion import ChatMessage

prompt_filenames = os.listdir('prompts/')
mapping_prompt = {}
mapping_tools = {}
for filename in prompt_filenames:
    if filename.endswith('.txt'):
        with open('prompts/' + filename, 'r', encoding='utf-8') as prompt_file:
            filename = filename.split('.')[0]
            mapping_prompt[filename] = prompt_file.read()
    if filename.endswith('.json'):
        with open('prompts/' + filename, 'r', encoding='utf-8') as prompt_file:
            filename = filename.split('.')[0]
            mapping_tools[filename] = json.load(prompt_file)

def classification(**entry):
    """
    inputs:
        "logs_pp_day" logs of D-2
        "logs_p_day" logs of D-1
        "logs_day" logs of current day
        "time" timestamp
    output = tool to call
    """
    prompt = mapping_prompt['prompt_classification'].format(**entry)
    messages = [ChatMessage(role= "user", content=prompt)]
    return {"messages": messages, "tools": mapping_tools['prompt_classification'], "tool_choice":"any"}

def feedback_todo(**entry):
    """
    inputs:
        "logs_day" logs of current day
        "action" action infer by classifier

    output = question to ask to the user to know she/he wants to do the action given by the classifier
    """
    prompt = mapping_prompt['prompt_feedback_todo'].format(**entry)
    messages = [ChatMessage(role= "user", content=prompt)]
    return  {"messages": messages}

def feedback_todo_classification(**entry):
    """
    inputs:
        "action" action infer by classifier
        "answer" answer given by the user to AI request to trigger action
    output = tool Yes/No
    """
    prompt = mapping_prompt['prompt_feedback_todo_classification'].format(**entry)
    messages = [ChatMessage(role= "user", content=prompt)]
    return {"messages": messages, "tools": mapping_tools['prompt_feedback_todo_classification'], "tool_choice":"any"}

def feedback_register(**entry):
    """
    inputs:
        "logs_day" logs of current day
        "action" action infer by classifier
    output = question to ask to the user to know she/he wants to add the action to routines set
    """
    prompt = mapping_prompt['prompt_feedback_register'].format(**entry)
    messages = [ChatMessage(role= "user", content=prompt)]
    return {"messages": messages}

def feedback_register_classification(**entry):
    """
    inputs:
        "action" action infer by classifier
        "answer" answer given by the user to AI request to trigger action
    output = tool Yes/No
    """
    prompt = mapping_prompt['prompt_feedback_register_classification'].format(**entry)
    messages = [ChatMessage(role= "user", content=prompt)]
    return {"messages": messages, "tools": mapping_tools['prompt_feedback_register_classification'], "tool_choice":"any"}

def auto_evaluation(**entry):
    """
    inputs:
        "logs_autotask" logs of the day autotask was learned
        "logs_day" logs of current day
        "action" action from the routine set
        "time" time
    output = tool Yes/No
    """
    prompt = mapping_prompt['prompt_auto_evaluation'].format(**entry)
    messages = [ChatMessage(role= "user", content=prompt)]
    return {"messages": messages, "tools": mapping_tools['prompt_auto_evaluation'], "tool_choice":"any"}

def query(**entry):
    """
    inputs:
        "user_input"
        "time" time
    output = tool Yes/No
    """
    prompt = mapping_prompt['prompt_query'].format(**entry)
    messages = [ChatMessage(role= "user", content=prompt)]
    return {"messages": messages, "tools": mapping_tools['prompt_query']}