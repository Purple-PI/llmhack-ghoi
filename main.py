import os
import json
import datetime

from mistralai.client import MistralClient

from agent.logs import LogsManager
from agent.agent import Agent

if __name__ == "__main__":
    api_key = os.environ["MISTRAL_API_KEY"]
    model = "mistral-large-latest"
    log_filepath = "data/logs/activitylog_uci_detailed_labour_xes8.json"
    logs = LogsManager(log_filepath)
    logs.cutoff_fun("11:00")
    for k in range(14):
        print(f"{str(11+k)}:00")
        client = MistralClient(api_key=api_key)
        agent = Agent(model_name=model, client=client, logs=logs)
        action = agent.tick(f"{str(11+k)}:00")
        print(f'Current action: {action}')
