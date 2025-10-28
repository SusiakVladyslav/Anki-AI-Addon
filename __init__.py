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

from .OpenAI_Anki import write_ai_output_to_file, generate_audios

config_file = os.path.join(ADDON_PATH, "config.json")
if os.path.exists(config_file):
    with open(config_file, "r") as f:
        config = json.load(f)

Tag = config.get("TAG")

Notes_info = config.get("Notes_info")
Notes_info_path = os.path.join(ADDON_PATH, Notes_info)
AI_response = config.get("AI_response")
AI_response_path = os.path.join(ADDON_PATH, AI_response)
Save_file_path = os.path.join(ADDON_PATH, "Save file.txt")
Audio_path = os.path.join(ADDON_PATH, "Audios")


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
    card_ids = mw.col.find_cards(f"tag:{tag}")
    return card_ids


def get_field(field, n):
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


def create_save_file():
    utils.showWarning("The number of Note and current number is not the same.\nCreating a save file")
    with open(Save_file_path, 'a', encoding='utf-8') as save_file:
        with open(Notes_info_path, "r", encoding='utf-8') as notes_file:
            notes = notes_file.readlines()
        with open(AI_response_path, "r", encoding='utf-8') as AI_file:
            AI = AI_file.readlines()

        save_file.writelines(notes)
        save_file.write("\n---\n")
        save_file.writelines(AI)


def get_all_files_by_number(folder_path, number):
    """
    Returns a list of ALL files that start with the number
    """
    number_str = str(number)
    files = os.listdir(folder_path)

    matching_files = []
    for filename in files:
        if filename.startswith(number_str):
            full_path = os.path.join(folder_path, filename)
            matching_files.append(full_path)

    return matching_files  # Returns list (empty if none found)


def add_audio_to_note(files, card_ids, card_num):
    col = mw.col

    card = mw.col.get_card(card_ids[card_num])
    note = card.note()

    note["Audio"] = ""

    for file in files:
        audio_tag = col.media.add_file(file)
        note["Audio"] += f"[sound:{audio_tag}]"
        col.update_note(note)


def write_file_to_notes():
    col = mw.col
    with open(AI_response_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        card_ids = get_card_ids(tag=Tag)
        card_num = 0  # a count variable for a card in card_ids

        # line variable
        n = 0
        # variable which checks whether it is a new word or not
        is_a_new_word = True
        Number = None

        while n < len(lines):
            # A check whether a line is a number
            if lines[n].strip().isdigit():

                card = mw.col.get_card(card_ids[card_num])
                note = card.note()
                Number = lines[n].strip()

                if Number == note["Number"]:
                    n += 1
                    continue
                else:
                    create_save_file()
                    n += 1

            # A check whether a line is empty
            elif lines[n] == "\n":
                add_audio_to_note(get_all_files_by_number(Audio_path, Number), card_ids, card_num)

                n += 1
                is_a_new_word = True
                card_num += 1
                continue

            # A check whether a line is Korean and whether it is a new word
            elif re.search(r'[\uac00-\ud7a3]', lines[n]) and is_a_new_word:
                Korean = lines[n].strip()
                English = lines[n + 1].strip() + "<br><br>" + lines[n + 2].strip()

                card = mw.col.get_card(card_ids[card_num])
                note = card.note()

                note["Korean"] = Korean
                note["English"] = English
                col.update_note(note)

                n += 3
                is_a_new_word = False
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


my_menu = QMenu("My add-on", mw)
mw.form.menubar.addMenu(my_menu)


Transfer_Notes_to_file = QAction("📥 Copy Note's fields to file")
qconnect(Transfer_Notes_to_file.triggered, write_notes_to_file)
my_menu.addAction(Transfer_Notes_to_file)

AI_to_file = QAction("🤖 Ask AI to generate sentences")
qconnect(AI_to_file.triggered, write_ai_output_to_file)
my_menu.addAction(AI_to_file)

TTS_audios = QAction("🔊 Ask AI to generate audios")
qconnect(TTS_audios.triggered, generate_audios)
my_menu.addAction(TTS_audios)

Transfer_file_to_Notes = QAction("📤 Transfer sentences and audio to Notes")
qconnect(Transfer_file_to_Notes.triggered, write_file_to_notes)
my_menu.addAction(Transfer_file_to_Notes)
