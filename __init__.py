from aqt import mw
from anki.notes import Note
from aqt.utils import showInfo, qconnect
from aqt.qt import *
from aqt import gui_hooks
from aqt import utils
import html
import re
import json

import sys, os
ADDON_PATH = os.path.dirname(__file__)
sys.path.append(os.path.join(ADDON_PATH, "lib"))

from .OpenAI_Anki import write_ai_output_to_file

config_file = os.path.join(ADDON_PATH, "config.json")
if os.path.exists(config_file):
    with open(config_file, "r") as f:
        config = json.load(f)

Tag = config.get("TAG")

Notes_info = config.get("Notes_info")
Notes_info_path = os.path.join(ADDON_PATH, Notes_info)
AI_response = config.get("AI_response")
AI_response_path = os.path.join(ADDON_PATH, AI_response)


def new_file_message():
    with open(AI_response_path, "a", encoding="utf-8") as f:
        f.write("Hello ai response\n")


def strip_html(text):
    """Remove HTML tags and decode HTML entities"""
    if not text:
        return ""

    # First, decode HTML entities like &amp; &lt; &gt;
    text = html.unescape(text)

    # Remove HTML tags using regex
    clean_text = re.sub(r'<[^>]+>', '', text)

    # Clean up extra whitespace
    clean_text = ' '.join(clean_text.split())

    return clean_text


def get_card_ids(tag=Tag):
    col = mw.col
    card_ids = mw.col.find_cards(f"tag:{tag}")
    return card_ids


def get_field(field,n):
    card = mw.col.get_card(get_card_ids(tag=Tag)[n])
    note = card.note()
    return strip_html(note[field])


def write_notes_to_file():
    with open(Notes_info_path, 'a') as f:
        f.seek(0)
        f.truncate()

        card_ids = get_card_ids(tag=Tag)
        for num in range(len(card_ids)):
            number_data = get_field("Number", num)
            f.write(f"{number_data} ")
            korean_data = get_field("Korean", num)
            f.write(f"{korean_data} - ")
            english_data = get_field("English", num).replace(";", " /// ")
            f.write(f"{english_data}\n\n")


def write_file_to_notes():
    col = mw.col
    with open(AI_response_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        card_ids = get_card_ids(tag=Tag)
        card_num = 0  # a count variable for a card in card_ids

        # line variable
        n = 0
        # variable which checks whether it is a new word or not
        i = 0
        while n < len(lines):
            # A check whether a line is a number
            if lines[n].strip().isdigit():
                n += 1
                continue
            # A check whether a line is empty
            elif lines[n] == "\n":
                n += 1
                i = 0
                card_num += 1
                continue
            # A check whether a line is Korean and whether it is a new word
            elif re.search(r'[\uac00-\ud7a3]', lines[n]) and i == 0:
                Korean = lines[n].strip()
                English = lines[n + 1].strip() + "<br><br>" + lines[n + 2].strip()

                card = mw.col.get_card(card_ids[card_num])
                note = card.note()

                note["Korean"] = Korean
                note["English"] = English
                col.update_note(note)

                n += 3
                i = 1
                continue
            # A condition which happens if word has several translations and meanings
            else:
                Korean = "<br><br>" + lines[n].strip()
                English = "<br><br>" + lines[n + 1].strip()

                card = mw.col.get_card(card_ids[card_num])
                note = card.note()

                note["Korean"] += Korean
                note["English"] += English
                col.update_note(note)

                n += 2
                continue


Transfer_Notes_to_file = QAction("Transfer Notes to file")
qconnect(Transfer_Notes_to_file.triggered, write_notes_to_file)
mw.form.menuTools.addAction(Transfer_Notes_to_file)

AI_to_file = QAction("Ask AI to write to the file")
qconnect(AI_to_file.triggered, write_ai_output_to_file)
mw.form.menuTools.addAction(AI_to_file)

Transfer_file_to_Notes = QAction("Transfer from file to Notes")
qconnect(Transfer_file_to_Notes.triggered, write_file_to_notes)
mw.form.menuTools.addAction(Transfer_file_to_Notes)

Test = QAction("Test file")
qconnect(Test.triggered, new_file_message)
mw.form.menuTools.addAction(Test)
