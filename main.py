
import os
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import functools



class Agent:
    
    def __init__(self, model_name, client):
        self.client = client
        self.model_name = model_name


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

        self.generate(x = 'make a coffee')
    
    def generate(self, x):
        messages = [ChatMessage(role="user", content=x)]
        response = client.chat(
            model=self.model_name,
            messages=messages,
            tools=self.tools,
            tool_choice="auto"
        )

        print(response)

    def make_coffee(self):
        print("I am making a coffee")


if __name__ == "__main__":
    api_key = os.environ["MISTRAL_API_KEY"]
    model = "mistral-large-latest"
    client = MistralClient(api_key=api_key)
    agent = Agent(model_name=model, client=client)

