import requests
import json
import os
import time
import re
from aqt import mw, utils
from aqt.operations import QueryOp
from aqt.utils import showInfo


ADDON_PATH = os.path.dirname(__file__)
config_file = os.path.join(ADDON_PATH, "config.json")
if os.path.exists(config_file):
    with open(config_file, "r") as f:
        config = json.load(f)

Notes_info = config.get("Notes_info")
Notes_info_path = os.path.join(ADDON_PATH, Notes_info)
AI_response = config.get("AI_response")
AI_response_path = os.path.join(ADDON_PATH, AI_response)

OPENAI_API_KEY = config.get("OPENAI_API_KEY")
ai_url = "https://api.openai.com/v1/responses"
tts_url = "https://api.openai.com/v1/audio/speech"

prompt = """I’m learning Korean. I know around 700 Korean words,
    and I’d like you to create Korean sentences using the words I provide so I can add them to my Anki deck.

Please make sure that each sentence helps me understand the meaning of the word from context.

The words will be provided in this format:
"number" "Korean word" - "translation /// translation2 /// ...".
Some words have more than 1 translation. Please take into account, different translations are divided by ///.
If a word divided by comma it is still only one translation and I need only one sentence.

Instructions:
For each korean word, generate one sentence per translation.
You should wrap both the Korean word and its translation in the following HTML span tag for coloring:
<span style="color: rgb(255, 0, 0);">WORD</span>
Important!:
If a translation contains a comma (,), treat it as part of the same translation and generate only one sentence for it.
Only generate multiple sentences if the translations are separated by ///.


Output in plain text using this format:
"number
Korean sentence 1
Korean word - Korean word translation
Sentence translation 1
Korean sentence 2
Sentence translation 2
Korean sentence n
Sentence translation n
An empty line"

Example:
List of words: "606 글쎄 - well, let me see, 913 떨어지다 - to fall, crash /// to be short of, run out"
Expected output:
"606
<span style="color: rgb(255, 0, 0);">글쎄</span>, 저는 잘 모르겠어요..
글쎄 - well, let me see
<span style="color: rgb(255, 0, 0);">Well</span>, I’m not sure..

913
사과가 나무에서 <span style="color: rgb(255, 0, 0);">떨어졌어요</span>.
떨어지다 - to fall, crash /// to be short of, run out
The apple <span style="color: rgb(255, 0, 0);">fell</span> from the tree.
기름이 거의 다 <span style="color: rgb(255, 0, 0);">떨어졌어요</span>.
We’ve almost <span style="color: rgb(255, 0, 0);">run out</span> of fuel."

List of words:"""


def get_full_list_of_words():
    with open(Notes_info_path, 'r', encoding='utf-8') as f:
        list_of_words = f.read()
        return list_of_words


def get_korean_words():
    with open(Notes_info_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        korean_words = []

        for line in lines:
            if line == "\n":
                continue
            else:
                korean_word = line.split(" - ", 1)[0]
                korean_words.append(korean_word)

        return korean_words


def ask_ai(list_of_words):
    start_time = time.time()

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "gpt-5-mini",
        "input": prompt + list_of_words
    }

    response = requests.post(ai_url, headers=headers, json=data)
    end_time = time.time()
    time_spent = end_time - start_time

    result = response.json()

    output = ""
    for item in result.get("output", []):
        if item.get("type") == "message":
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    output += content.get("text", "")

    usage = result.get("usage", {})
    input_tokens = usage.get("input_tokens", 0)
    output_tokens = usage.get("output_tokens", 0)

    return output, time_spent, input_tokens, output_tokens


def ask_tts(output):

    list_of_words = get_korean_words()

    lines = output.split("\n")
    responses = {}
    pattern = re.compile(r"^[가-힣\s]+ - [A-Za-z\s,/]+$")
    n = 0
    s = 0
    text = ""

    for line in lines:
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
        response = requests.post(tts_url, headers=headers, json=payload)

        if response.status_code == 200:
            responses[word + " " + str(s)] = response.content
        else:
            with open("error_log.txt", 'a', encoding='utf-8') as f:
                f.write("Error:" + str(response.status_code) + "\n")
                f.write(response.text)

    return responses


def on_success(result):
    result1, result2 = result
    output, time_spent, input_tokens, output_tokens = result1
    audios = result2

    with open(AI_response_path, 'a', encoding='utf-8') as f:
        f.seek(0)
        f.truncate()

        f.write(f"{output}")

        for audio in audios:
            with open(audio + ".mp3", "wb") as f:
                f.write(audios[audio])

        utils.showInfo(f"✅ AI response written successfully!\n"
                       f"⏱️ Time spent: {time_spent:.2f} seconds\n"
                       f"Input tokens used: {input_tokens}\n"
                       f"Output tokens used: {output_tokens}")


def on_failure():
    None

# function that allows to make a request to API without freezing Anki
# on_success is called with the return value of ask_ai
def write_ai_output_to_file():
    """
    Main function to call - makes a request to OpenAI API and writes output in a file.
    """

    def run_ais():
        result1 = ask_ai(get_full_list_of_words())
        result2 = ask_tts(result1[0])

        return result1, result2

    # Create the background operation
    op = QueryOp(
        parent=mw,
        op=lambda col: run_ais(),  # Runs in background
        success=on_success  # Called when done
    )

    # To be added
    # Handle failure
    # op.failure(on_failure)

    # Show progress dialog and run in background
    op.with_progress("AI is generating sentences...").run_in_background()


def main():
    print(get_korean_words())


if __name__:
    main()
