import gradio as gr
import time
import json

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def vlm_output_fn(image):
    logger.info(f"Run VLM on image {image}...")
    time.sleep(5)
    return "An image description..."


def proactive_interaction_agent_fn(image_description, chat_history):
    logger.info(f"Run LLM on image description {image_description}...")
    time.sleep(2)
    llm_answer = "I see that you are doing task1, you usually do task2 after task1, If you need I can do the task2."
    chat_history.append((None, llm_answer))
    return chat_history


def speech_to_text(audio):
    logger.info(f"Run speech-to-text on {audio}...")
    time.sleep(1)
    return "Transcripted text"


def human_answer_to_llm_fn(audio, chat_history):
    logger.info(f"Run speech-to-text on {audio}...")
    human_text = speech_to_text(audio)

    time.sleep(2)
    llm_answer = "No problem, I will do it"
    chat_history.append((human_text, llm_answer))
    return chat_history


if __name__ == "__main__":
    log_file = "data/logs/activitylog_uci_detailed_labour.xes0_test.json"
    with open(log_file, "r") as file:
        logs = json.load(file)
    i = 0
    event_to_video = {
        "sleeping": "sleep.mp4",
        "prepareBreakfast": "breakfast.mp4",
        "watchingtv": "tv.mp4",
        "washing": "washing.mp4",
        "shower": "shower.mp4",
        "eatingLunch": "eating.mp4",
        "eatingDinner": "eating.mp4",
        "prepareLunch": "cook.mp4",
        "prepareDinner": "cook.mp4",
        "setAlarm": "alarm.mp4",
        "heatOven": "oven.mp4",
        "prepareCoffee": "coffee.mp4",
        "listeningMusic": "music.mp4",
        "orderFood": "orderfood.mp4"
    }


    with gr.Blocks() as app:
        date = gr.Textbox(label="Time", interactive=False, value="11:30")

        video = gr.Video(
            value="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
            autoplay=True,
            height=240
        )
        vlm_output = gr.Textbox(
            label="Vision-Language Model output",
            placeholder="System is thinking... 🧠",
            interactive=False,
        )
        chatbot = gr.Chatbot()

        with gr.Row():
            msg = gr.Audio(sources=["microphone"], scale=5)
            send_button = gr.Button("Send 🚀", scale=1)

        next_button = gr.Button("Go to next day ➡️")

        # Logic
        video.change(vlm_output_fn, inputs=video, outputs=vlm_output)
        app.load(vlm_output_fn, inputs=video, outputs=vlm_output)

        vlm_output.change(proactive_interaction_agent_fn, inputs=[vlm_output, chatbot], outputs=chatbot)
        send_button.click(human_answer_to_llm_fn, inputs=[msg, chatbot], outputs=chatbot)
    app.launch()

