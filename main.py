import os

from mistralai.client import MistralClient

from agent.agent import Agent

if __name__ == "__main__":
    api_key = os.environ["MISTRAL_API_KEY"]
    model = "mistral-large-latest"
    client = MistralClient(api_key=api_key)
    agent = Agent(model_name=model, client=client)
    agent.tick("12:00")