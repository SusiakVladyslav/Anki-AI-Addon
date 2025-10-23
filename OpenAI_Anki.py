import requests
import json
import os
import traceback
from datetime import datetime
import os

ADDON_PATH = os.path.dirname(__file__)
config_file = os.path.join(ADDON_PATH, "config.json")
if os.path.exists(config_file):
    with open(config_file, "r") as f:
        config = json.load(f)

OPENAI_API_KEY = config.get("OPENAI_API_KEY")
url = "https://api.openai.com/v1/responses"

prompt = """I’m learning Korean. I know around 700 Korean words,
    and I’d like you to create Korean sentences using the words I provide so I can add them to my Anki deck.

Please make sure that each sentence helps me understand the meaning of the word from context.
Also, you can create several sentences for one word in one row if needed.

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


def ask_ai(list_of_words):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "gpt-5-mini",
        "input": prompt + list_of_words
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    output = ""
    for item in result.get("output", []):
        if item.get("type") == "message":
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    output += content.get("text", "")

    return output



