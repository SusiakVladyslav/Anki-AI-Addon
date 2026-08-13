import pytest
from unittest.mock import MagicMock
from utils import func_utils

from anki.collection import Collection


@pytest.mark.parametrize("html_text, text_without_html", [
    ('<font color="#ff0000">도둑</font>이 <font color="#55aaff">지갑</font>을 '
     '<font color="#55ffff">훔쳐서 </font>경찰에 신고했어요.',
     "도둑이 지갑을 훔쳐서 경찰에 신고했어요.")
],
    ids=["Korean_sentence_1"]
)
def test_strip_html(html_text, text_without_html):
    assert utils.strip_html(html_text) == text_without_html


@pytest.fixture
def mock_anki_collection(tmp_path):
    col_path = str(tmp_path / "test.anki2")
    col = Collection(col_path)

    utils.mw = MagicMock()

    utils.mw.col = col

    yield col

    col.close()


def test_get_cards_ids(mock_anki_collection):
    col = mock_anki_collection
    deck_id = col.decks.id("Default")

    for i in range(1, 11):
        note = col.new_note(col.models.by_name("Basic"))
        note["Front"] = f"Test Front Content #{i}"
        note["Back"] = f"Test Back Content #{i}"
        note.add_tag("Test_tag")

        col.add_note(note, deck_id=deck_id)

    card_ids = utils.get_card_ids(tag="Test_tag")

    assert card_ids == utils.mw.col.find_cards(f"tag:Test_tag")
    assert len(card_ids) == 10


def test_get_field(mock_anki_collection, monkeypatch):
    col = mock_anki_collection
    deck_id = col.decks.id("Default")

    note = col.new_note(col.models.by_name("Basic"))
    note["Front"] = '<font color="#ff0000">Test Front</font> Content'
    note["Back"] = "Test Back Content"
    note.add_tag("Test_tag")

    col.add_note(note, deck_id=deck_id)

    monkeypatch.setattr(utils, "Tag", "Test_tag")
    front_value = utils.get_field("Front", 0)
    back_value = utils.get_field("Back", 0)

    assert front_value == "Test Front Content"
    assert back_value == "Test Back Content"


@pytest.fixture
def mock_korean_vocab_note_type(mock_anki_collection):
    col = mock_anki_collection

    note_type = col.models.new("Test Korean Vocab")
    for field_name in ["Number", "Korean", "English"]:
        col.models.add_field(note_type, col.models.new_field(field_name))

    template = col.models.new_template("Card 1")
    template['qfmt'] = "{{Korean}}"
    template['afmt'] = "{{FrontSide}}\n\n<hr id=answer>\n\n{{English}}"
    col.models.add_template(note_type, template)

    col.models.add_dict(note_type)

    return col.models.by_name("Test Korean Vocab")


def test_write_notes_to_file(mock_anki_collection, mock_korean_vocab_note_type, tmp_path, monkeypatch):
    col = mock_anki_collection
    note_type = mock_korean_vocab_note_type
    deck_id = col.decks.id("Default")

    note = col.new_note(note_type)
    note["Number"] = "1"
    note["Korean"] = "차"
    note["English"] = "tea;<div>car</div>"
    note.add_tag("Test_tag")
    col.add_note(note, deck_id)

    test_file_path = tmp_path / "Notes info.txt"
    monkeypatch.setattr(utils, "Notes_info_path", str(test_file_path))
    monkeypatch.setattr(utils, "Tag", "Test_tag")

    utils.write_notes_to_file()

    content = test_file_path.read_text(encoding="utf-8")
    assert content == "1 차 - tea /// car\n\n"

    with open(str(test_file_path), "r+") as file:
        file.seek(0)  # Move the file pointer to the very beginning
        file.truncate(0)
    note.remove_tag("Test_tag")
    col.update_note(note)

    note_2 = col.new_note(note_type)
    note_2["Number"] = "33"
    note_2["Korean"] = "물"
    note_2["English"] = "water"
    note_2.add_tag("Test_tag")
    col.add_note(note_2, deck_id)

    utils.write_notes_to_file()

    content = test_file_path.read_text(encoding="utf-8")
    assert content == "33 물 - water\n\n"
