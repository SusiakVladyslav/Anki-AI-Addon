import requests
import os
import time
import re

from aqt import mw, utils
from aqt.operations import QueryOp
from aqt.utils import showInfo
from aqt.qt import QMessageBox

from anki.notes import Note

from utils.constants import NOTES_INFO_PATH, OPENAI_API_KEY, AI_RESPONSE_PATH, MODEL, PROMPT, AI_URL, AUDIO_PATH, TTS_URL
from utils.utils import strip_html

from ai.openai_requests import request_something


def get_full_list_of_words():
    with open(NOTES_INFO_PATH, 'r', encoding='utf-8') as f:
        list_of_words = f.read()
        return list_of_words


def get_korean_words():
    with open(NOTES_INFO_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        korean_words = []

        for line in lines:
            if line == "\n":
                continue
            else:
                korean_word = line.split(" - ", 1)[0]
                korean_words.append(korean_word)

        return korean_words


def on_success_ai(result):
    output, time_spent, input_tokens, output_tokens = result

    with open(AI_RESPONSE_PATH, 'a', encoding='utf-8') as f:
        f.seek(0)
        f.truncate()

        f.write(f"{output}\n\n")

        money_spent = ((input_tokens/1000000) * 0.25) + ((output_tokens/1000000) * 2)

        utils.showInfo(f"✅ AI response written successfully!\n"
                       f"⏱️ Time spent: {time_spent:.2f} seconds\n"
                       f"Input tokens used: {input_tokens}\n"
                       f"Output tokens used: {output_tokens}"
                       f"Money spent {money_spent}$ (gpt-5-mini)")


def ask_tts():
    start_time = time.time()

    with open(AI_RESPONSE_PATH, "r", encoding='utf-8') as AI_file:
        output = AI_file.read()

    list_of_words = get_korean_words()

    lines = output.split("\n")
    responses = {}
    pattern = re.compile(r"^[가-힣\s]+ - [A-Za-z\s,/()-;<>]+$")
    n = 0
    s = 0
    text = ""

    for line in lines:
        line = strip_html(line)
        if re.search(r'[\uac00-\ud7a3]', line) and not pattern.match(line):
            text = line
            s += 1
        elif line == "":
            n += 1
            s = 0
            continue
        else:
            continue

        if n >= len(list_of_words):
            break

        word = list_of_words[n].split(" - ")[0]

        payload = {
            "model": "gpt-4o-mini-tts",
            "input": text,
            "voice": "echo",
            "format": "mp3"
        }

        # Request headers
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        # Send the request
        response = requests.post(TTS_URL, headers=headers, json=payload)

        if response.status_code == 200:
            responses[word + " " + str(s)] = response.content
        else:
            with open("error_log.txt", 'a', encoding='utf-8') as f:
                f.write("Error:" + str(response.status_code) + "\n")
                f.write(response.text)

    end_time = time.time()
    time_spent = end_time - start_time

    return responses, time_spent


def on_success_tts(result):
    audios, time_spent = result
    for audio in audios:
        file_path = os.path.join(AUDIO_PATH, audio + ".mp3")
        with open(file_path, "wb") as f:
            f.write(audios[audio])

    utils.showInfo(f"✅ {str(len(audios))} Audios was successfully generated\n"
                   f"⏱️ Time spent: {time_spent:.2f} seconds")


# function that allows to make a request to API without freezing Anki
# on_success is called with the return value of ask_ai
def write_ai_output_to_file():
    """
    Main function to call - makes a request to OpenAI API and writes output in a file.
    """

    msg = QMessageBox(mw)
    msg.setIcon(QMessageBox.Icon.Question)
    msg.setWindowTitle("Confirmation regarding AI model")
    msg.setText(f"The used model is {MODEL}.\n Do you want to continue?")
    msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    result = msg.exec()

    if result == QMessageBox.StandardButton.Yes:

        # Create the background operation
        op = QueryOp(
            parent=mw,
            op=lambda col: request_something(get_full_list_of_words()),  # Runs in background
            success=on_success_ai  # Called when done
        )

        # To be added
        # Handle failure
        # op.failure(on_failure)

        # Show progress dialog and run in background
        op.with_progress("AI is generating sentences...").run_in_background()


def generate_audios():
    op = QueryOp(
        parent=mw,
        op=lambda col: ask_tts(),  # Runs in background
        success=on_success_tts  # Called when done
    )

    # To be added
    # Handle failure
    # op.failure(on_failure)

    # Show progress dialog and run in background
    op.with_progress("AI is generating audios...").run_in_background()


def make_ai_request(selected_notes: list[Note], prompt: str):
    all_notes_fields_str = get_notes_fields_as_string(selected_notes)

    start_time = time.time()
    output_text, input_tokens, output_tokens, cache_input_tokens = request_something(all_notes_fields_str, prompt=prompt)
    time_spent = time.time() - start_time
    showInfo(all_notes_fields_str)
    showInfo(f"{output_text}\n/// {input_tokens} /// {output_tokens} /// {time_spent} /// {MODEL} /// {cache_input_tokens}")

    return output_text, input_tokens, output_tokens


def get_notes_fields_as_string(selected_notes: list[Note]) -> str:
    all_notes_fields_str = ""
    for note in selected_notes:
        fields_data: list[tuple[str, str]] = note.items()
        for field_name, field_value in fields_data:
            if field_name == "Audio" or field_name == "Number" or field_name == "Hanja":
                continue
            all_notes_fields_str += f"{field_name}|{field_value}\n"

    return all_notes_fields_str

# [<anki.notes.Note object at 0x0000022E6B246A50>, <anki.notes.Note object at 0x0000022E6B206A40>]
