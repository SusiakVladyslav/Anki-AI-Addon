import os
import json
from typing import Final

AI_DIR: Final = os.path.dirname(os.path.abspath(__file__))
ADDON_PATH: Final = os.path.abspath(os.path.join(AI_DIR, ".."))
META_PATH: Final = ADDON_PATH + "/meta.json"

if os.path.exists(META_PATH):
    with open(META_PATH, "r") as f:
        CONFIG = json.load(f)["config"]

NOTES_INFO_FILE_NAME: Final = CONFIG.get("Notes_info")
NOTES_INFO_PATH: Final = os.path.join(ADDON_PATH, NOTES_INFO_FILE_NAME)
AI_RESPONSE: Final = CONFIG.get("AI_response")
AI_RESPONSE_PATH: Final = os.path.join(ADDON_PATH, AI_RESPONSE)
SAVE_FILE_PATH = os.path.join(ADDON_PATH, "../Save file.txt")

if not os.path.exists("../Audios"):
    os.mkdir("../Audios")

AUDIO_PATH: Final = os.path.join(ADDON_PATH, "../Audios")

TAG = CONFIG.get("TAG")
OPENAI_API_KEY: Final = CONFIG.get("OPENAI_API_KEY")
AI_URL: Final = "https://api.openai.com/v1/responses"
TTS_URL: Final = "https://api.openai.com/v1/audio/speech"

MODEL: Final = CONFIG.get("Model")

# PROMPT = """I’m learning Korean. I know around 700 Korean words,
#     and I’d like you to create Korean sentences using the words I provide so I can add them to my Anki deck.
#
# Please make sure that each sentence helps me understand the meaning of the word from context.
#
# The words will be provided in this format:
# "number" "Korean word" - "translation /// translation2 /// ...".
# Some words have more than 1 translation. Please take into account, different translations are divided by ///.
# If a word divided by comma it is still only one translation and I need only one sentence.
#
# Instructions:
# For each korean word, generate one sentence per translation.
# You should wrap both the Korean word and its translation in the following HTML span tag for coloring:
# <span style="color: rgb(255, 0, 0);">WORD</span>
# Important!:
# If a translation contains a comma (,), treat it as part of the same translation and generate only one sentence for it.
# Only generate multiple sentences if the translations are separated by ///.
#
#
# Output in plain text using this format:
# "number
# Korean sentence 1
# Korean word - Korean word translation
# Sentence translation 1
# Korean sentence 2
# Sentence translation 2
# Korean sentence n
# Sentence translation n
# An empty line"
#
# Example:
# List of words: "606 글쎄 - well, let me see, 913 떨어지다 - to fall, crash /// to be short of, run out"
# Expected output:
# "606
# <span style="color: rgb(255, 0, 0);">글쎄</span>, 저는 잘 모르겠어요..
# 글쎄 - well, let me see
# <span style="color: rgb(255, 0, 0);">Well</span>, I’m not sure..
#
# 913
# 사과가 나무에서 <span style="color: rgb(255, 0, 0);">떨어졌어요</span>.
# 떨어지다 - to fall, crash /// to be short of, run out
# The apple <span style="color: rgb(255, 0, 0);">fell</span> from the tree.
# 기름이 거의 다 <span style="color: rgb(255, 0, 0);">떨어졌어요</span>.
# We’ve almost <span style="color: rgb(255, 0, 0);">run out</span> of fuel."
#
# List of words:"""

PROMPT = """I’m learning Korean,
    and I’d like you to create Korean sentences using the words I provide so I can add them to my Anki deck.

Please make sure that each sentence helps me understand the meaning of the word from context.

The words will be provided in this format:
"number" "Korean word" - "translation /// translation2 /// ...".
Some words have more than 1 translation. Please take into account, different translations are divided by ///.
If a word divided by comma it is still only one translation and I need only one sentence.

Instructions:
Important!:
If a translation contains a comma (,), treat it as part of the same translation and generate only one translation for it.
Only generate multiple translations if the translations are separated by ///.


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
글쎄, 저는 잘 모르겠어요..
글쎄 - well, let me see
Well, I’m not sure..

913
사과가 나무에서 떨어졌어요
떨어지다 - to fall, crash /// to be short of, run out
The apple fell from the tree.
기름이 거의 다 떨어졌어요
We’ve almost run out of fuel."

List of words:"""


if __name__ == '__main__':
    pass