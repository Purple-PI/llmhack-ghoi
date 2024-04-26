import gradio as gr
import time
import json
from datetime import datetime

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


def format_objects(objects):
    formatted_strings = []
    for obj in objects:
        formatted_obj = ", ".join([f"{key}: {value}" for key, value in obj.items()])
        formatted_strings.append(formatted_obj)
    return "\n".join(formatted_strings)


def proactive_interaction_agent_fn(image_description, time, chat_history):
    global agent_logs
    logger.info(f"Run LLM on image description {image_description}...")
    agent.add_event(image_description, time)
    llm_answer = agent.tick_event(time)
    chat_history.append((None, llm_answer))
    return chat_history, format_objects(agent_logs)


def speech_to_text(audio):
    logger.info(f"Run speech-to-text on {audio}...")
    time.sleep(1)
    return "Transcripted text"


def human_answer_to_llm_fn(audio, chat_history):
    global number_of_interaction, i, routines_to_display
    logger.info(f"Run speech-to-text on {audio}...")
    human_text = speech_to_text(audio)

    if number_of_interaction == 0:
        llm_answer = agent.input_user_0(human_text)
    elif number_of_interaction == 1:
        llm_answer = agent.input_user_1(human_text)

        last_routine = agent.get_last_routine()
        last_routine_time = last_routine["time"]
        time = logs[i]["time"]

        last_routine_datetime = datetime.strptime(last_routine_time, "%H:%M")
        current_time_datetime = datetime.strptime(time, "%H:%M")

        if last_routine_datetime >= current_time_datetime:
            routines_to_display.append(last_routine)
    else:
        llm_answer = "I have Nothing to say anymore"
    if llm_answer == "":
        llm_answer = "**Nothing to do**"
    number_of_interaction += 1

    chat_history.append((human_text, llm_answer))
    return chat_history, format_objects(routines_to_display), format_objects(agent_logs)


if __name__ == "__main__":
    log_file = "data/logs/activitylog_uci_detailed_labour.xes0_test.json"
    with open(log_file, "r") as file:
        logs = json.load(file)
    i = 0
    number_of_interaction = 0
    routines_to_display = []
    agent_logs = []
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

    def next_event_fn():
        global i
        while True:
            i += 1
            if logs[i]["event"] in event_to_video or i >= len(logs):
                break
        i = i % len(logs)

        return "data/videos/" + event_to_video[logs[i]["event"]], logs[i]["time"], []

    with gr.Blocks() as app:
        date = gr.Textbox(label="Time", interactive=False, value=logs[i]["time"])

        video = gr.Video(
            value="data/videos/" + event_to_video[logs[i]["event"]],
            autoplay=True,
            height=240
        )
        vlm_output = gr.Textbox(
            label="Vision-Language Model output",
            placeholder="System is thinking... 🧠",
            interactive=False,
        )

        with gr.Row():
            logs_text = gr.Textbox(label="Logs", scale=1, interactive=False)
            routine_text = gr.Textbox(label="Routine", scale=1, interactive=False)
            chatbot = gr.Chatbot(scale=3)

        with gr.Row():
            msg = gr.Audio(sources=["microphone"], scale=5)
            send_button = gr.Button("Send 🚀", scale=1)

        next_button = gr.Button("Go to event day ➡️")

        # Logic
        video.change(vlm_output_fn, inputs=video, outputs=vlm_output)
        app.load(vlm_output_fn, inputs=video, outputs=vlm_output)

        vlm_output.change(proactive_interaction_agent_fn, inputs=[vlm_output, date, chatbot], outputs=[chatbot, logs_text])
        send_button.click(human_answer_to_llm_fn, inputs=[msg, chatbot], outputs=[chatbot, routine_text, logs_text])
        next_button.click(next_event_fn, inputs=None, outputs=[video, date, chatbot])
    app.launch()

