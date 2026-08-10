from aqt import mw
import html
import re
from aqt import utils
from aqt.qt import *
from aqt.browser import Browser
from aqt.utils import showInfo

from utils.constants import TAG, NOTES_INFO_PATH, AI_RESPONSE_PATH, AUDIO_PATH, SAVE_FILE_PATH
import gui.gui as my_gui
import gui.dialogs as dialogs


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


def get_card_ids(tag=TAG):
    card_ids = mw.col.find_cards(f"tag:{tag}")
    return card_ids


def get_field(field, n):
    card = mw.col.get_card(get_card_ids(tag=TAG)[n])
    note = card.note()
    return strip_html(note[field])


def write_notes_to_file():
    with open(NOTES_INFO_PATH, 'a', encoding="utf-8") as f:
        f.seek(0)
        f.truncate()

        card_ids = get_card_ids(tag=TAG)
        for num in range(len(card_ids)):
            number_data = get_field("Number", num)
            f.write(f"{number_data} ")
            korean_data = get_field("Korean", num)
            f.write(f"{korean_data} - ")
            english_data = get_field("English", num).replace(";", " /// ")
            f.write(f"{english_data}\n\n")


def create_save_file():
    utils.showWarning("The number of Note and current number is not the same.\nCreating a save file")
    with open(SAVE_FILE_PATH, 'a', encoding='utf-8') as save_file:
        with open(NOTES_INFO_PATH, "r", encoding='utf-8') as notes_file:
            notes = notes_file.readlines()
        with open(AI_RESPONSE_PATH, "r", encoding='utf-8') as AI_file:
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
    with open(AI_RESPONSE_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        card_ids = get_card_ids(tag=TAG)
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
                add_audio_to_note(get_all_files_by_number(AUDIO_PATH, Number), card_ids, card_num)

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


def extract_field_data(browser: Browser):
    selected_note_ids = browser.selected_notes()

    if len(selected_note_ids) == 0:
        dialogs.no_cards_were_selected_warning()

    if more_than_one_note_type_selected(selected_note_ids):
        dialogs.more_than_one_note_type_selected_warning()

    note_type = mw.col.get_note(selected_note_ids[0]).note_type()["name"]

    list_of_notes_fields_data = []
    for note_id in selected_note_ids:
        note = mw.col.get_note(note_id)
        list_of_notes_fields_data.append(note.items())
    
    return list_of_notes_fields_data

    # if note_type_not_in_profile():
    #     print("Unkown note_type")
    #
    # prompt = config_get_prompt_for_note_type(note_type)


def more_than_one_note_type_selected(selected_note_ids):
    set_of_note_types = set()
    for note_id in selected_note_ids:
        note = mw.col.get_note(note_id)
        set_of_note_types.add(note.note_type()["name"])

    if len(set_of_note_types) > 1:
        return True
    else:
        return False
