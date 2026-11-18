import pytest
from unittest.mock import patch

import copy

from ankiaddon.utils import gui_utils
from ankiaddon.utils.gui_utils import strip_html, strip_square_brackets, convert_cloze_to_plain_text, strip_non_ascii

@pytest.mark.parametrize(
    "html_text, clean_text",
    [
        ("", ""),
        ("<style>body { color: red; }</style><p>Hello</p>", "Hello"),
        ("<script>console.log('test');</script><div>World</div>", "World"),
        ("<div>Line 1</div><div>Line 2</div>", "Line 1\nLine 2"),
        ("<p>Paragraph 1</p><p>Paragraph 2</p>", "Paragraph 1\nParagraph 2"),
        ("Student<span>Text</span>", "StudentText"),
        ("<b>Bold</b> word", "Bold word"),
        ("Tom&nbsp;&amp;&nbsp;Jerry", "Tom & Jerry"),
        ("5 &lt; 10 &gt; 2", "5 < 10 > 2"),
        ("Word\xa0Space", "Word Space"),
        ("   \n\n <div>  Trimmed content  </div> \n\n  ", "Trimmed content"),
        ("<div>{{c1::Paris}} is capital</div>", "{{c1::Paris}} is capital"),
        ("<b>{{c1::<b>Oxygen</b>::element}}</b>", "{{c1::Oxygen::element}}"),
        (
            '<p>The output is {{c1::<span style="color: red;">error</span>::status}}.</p>',
            'The output is {{c1::error::status}}.',
        ),
        ("<div>[sound:audio.mp3]</div>", "[sound:audio.mp3]"),
        ("<p>Word [tag] <b>explanation</b></p>", "Word [tag] explanation"),
        (
            "<b>[sound:audio1.mp3]</b> <span>[sound:audio2.mp3]</span>",
            "[sound:audio1.mp3] [sound:audio2.mp3]",
        ),
    ],
)
def test_strip_html(html_text: str, clean_text: str) -> None:
    output = strip_html(html_text)
    assert output == clean_text


@pytest.mark.parametrize(
    "square_brackets_text, clean_text",
    [
        ("", ""),
        ("[sound:hypertts-c6aa5a956d6fdb2ffbd0344509e84855fcea1c622b8b8894c20b756e.mp3]", ""),
        ("[sound:audio_file_123.mp3]", ""),
        ("Hello [sound:test.mp3] world", "Hello world"),
        ("[sound:audio.mp3] Explanation text", "Explanation text"),
        ("[sound:one.mp3] middle text [sound:two.mp3]", "middle text"),
        ("[tag1] text [tag2] extra", "text extra"),
        ("Word [extra info] end", "Word end"),
        ("[bracket at start] Text", "Text"),
        ("No square brackets text", "No square brackets text"),
        ("Text with () and {}", "Text with () and {}"),
        ("[[nested]]", ""),
        ("[first][second]", ""),
    ],
)
def test_strip_square_brackets(square_brackets_text: str, clean_text:str) -> None:
    output = strip_square_brackets(square_brackets_text)
    assert output == clean_text

@pytest.mark.parametrize(
    "cloze_text, clean_text",
    [
        ("", ""),
        ("{{c1::Paris}} is capital of France", "Paris is capital of France"),
        ("{{c1::Canberra::capital}} is the capital of Australia.", "Canberra is the capital of Australia."),
        ("The process is called {{c2::photosynthesis::biological process}}.", "The process is called photosynthesis."),
        ("{{c1::Tokyo}} is in {{c2::Japan}}.", "Tokyo is in Japan."),
        (
            "{{c1::Python}} was created by {{c2::Guido van Rossum}} in {{c3::1991}}.",
            "Python was created by Guido van Rossum in 1991."
        ),
        ("{{c1::<b>Oxygеn</b>}} is required for respiration.", "<b>Oxygеn</b> is required for respiration."),
        (
            "The output is {{c1::<span style=\"color: red;\">error</span>::status}}.",
            "The output is <span style=\"color: red;\">error</span>."
        ),
        ("This is just regular text without any clozes.", "This is just regular text without any clozes."),
        ("Run {{c1::db:migrate::command}} to update database.", "Run db:migrate to update database."),
        ("Text with {curly braces}", "Text with {curly braces}"),
        ("Text with {single curly braces : and semicolon}", "Text with {single curly braces : and semicolon}")
    ],
)
def test_convert_cloze_to_plain_text(cloze_text: str, clean_text: str) -> None:
    output = convert_cloze_to_plain_text(cloze_text)
    assert output == clean_text


@pytest.mark.parametrize(
    "input_text, expected_output",
    [
        ("", ""),
        ("Hello World 123!", "Hello World 123!"),
        ("Standard text with punctuation: @#$%", "Standard text with punctuation: @#$%"),
        ("Café", "Caf"),
        ("Naïve", "Nave"),
        ("абвгде", ""),
        ("한국어", ""),
        ("Hello, 세계!", "Hello, !"),
        ("Flashcard 🎴 study 🧠", "Flashcard  study "),
        ("Price: 100€ or $100", "Price: 100 or $100"),
        ("“Smart quotes” and — em dash", "Smart quotes and  em dash"),
        ("Line 1\nLine 2\tTabbed", "Line 1\nLine 2\tTabbed"),
    ],
)
def test_strip_non_ascii(input_text: str, expected_output: str) -> None:
    output = strip_non_ascii(input_text)
    assert output == expected_output

SAMPLE_PROFILE = {
        "Korean Profile (Proper Prompt)": {
            "selected_card_type": "Korean Vocab",
            "selected_fields": [
                "Korean",
                "English",
                "Number"
            ],
            "selected_fields_settings": {
                "Korean": {
                    "strip_html": True,
                    "strip_brackets": False,
                    "convert_cloze": False,
                    "strip_non_ascii": False
                },
                "English": {
                    "strip_html": True,
                    "strip_brackets": False,
                    "convert_cloze": False,
                    "strip_non_ascii": False
                },
                "Number": {
                    "strip_html": True,
                    "strip_brackets": False,
                    "convert_cloze": False,
                    "strip_non_ascii": False
                }
            },
            "selected_model": "gpt-6-luna",
            "generate_as_new_cards": False,
            "deck_for_generated_cards": None,
            "add_tag_to_generated_cards": False,
            "tag_name_for_generated_cards": None,
            "prompt_text": "You are a proficient Korean teacher. Enhance these cards"
        }
    }

@pytest.fixture
def sample_profile() -> dict:
    return copy.deepcopy(SAMPLE_PROFILE)


def test_insert_profile_settings_in_config_success(sample_profile: dict):
    fake_config = {
        "OPENAI_API_KEY": "",
        "Profiles": {}
    }

    with (
        patch.object(gui_utils, "CONFIG", fake_config),
        patch.object(gui_utils, "ADDON_PACKAGE", "ankiaddon"),
        patch.object(gui_utils, "mw") as mock_mw,
        patch.object(gui_utils, "notifications") as mock_notifications,
    ):
        result = gui_utils.insert_profile_settings_in_config(sample_profile)

        assert result == True
        assert fake_config["Profiles"] == sample_profile
        assert fake_config["OPENAI_API_KEY"] == ""
        assert list(fake_config.keys()) == ["OPENAI_API_KEY", "Profiles"]

        mock_mw.addonManager.writeConfig.assert_called_once_with("ankiaddon", fake_config)
        mock_notifications.profile_with_such_name_already_exists.assert_not_called()
        mock_notifications.config_not_found_error.assert_not_called()


def test_insert_profile_settings_in_config_duplicate_name(sample_profile: dict):
    already_existing_profile = copy.deepcopy(sample_profile)

    fake_config = {
        "OPENAI_API_KEY": "",
        "Profiles": already_existing_profile
    }

    same_name_profile = {
        "Korean Profile (Proper Prompt)": {
            "selected_card_type": "Basic",
            "selected_fields": [
                "Front",
                "Back"
            ],
            "selected_fields_settings": {
                "Front": {
                    "strip_html": False,
                    "strip_brackets": False,
                    "convert_cloze": False,
                    "strip_non_ascii": False
                },
                "Back": {
                    "strip_html": False,
                    "strip_brackets": False,
                    "convert_cloze": False,
                    "strip_non_ascii": False
                }
            },
            "selected_model": "gpt-6-astra",
            "generate_as_new_cards": False,
            "deck_for_generated_cards": None,
            "add_tag_to_generated_cards": False,
            "tag_name_for_generated_cards": None,
            "prompt_text": "Enhance the cards"
        }
    }

    with (
        patch.object(gui_utils, "CONFIG", fake_config),
        patch.object(gui_utils, "ADDON_PACKAGE", "ankiaddon"),
        patch.object(gui_utils, "mw") as mock_mw,
        patch.object(gui_utils, "notifications") as mock_notifications,
    ):
        result = gui_utils.insert_profile_settings_in_config(same_name_profile)

    assert result == False
    assert len(fake_config["Profiles"]) == 1
    assert fake_config["Profiles"] == sample_profile
    assert fake_config["OPENAI_API_KEY"] == ""
    assert list(fake_config.keys()) == ["OPENAI_API_KEY", "Profiles"]

    mock_mw.addonManager.writeConfig.assert_not_called()
    mock_notifications.profile_with_such_name_already_exists.assert_called_once()
    mock_notifications.config_not_found_error.assert_not_called()


@pytest.mark.parametrize("empty_config", [None, {}])
def test_insert_profile_settings_config_not_found(sample_profile, empty_config):
    with (
        patch.object(gui_utils, "CONFIG", empty_config),
        patch.object(gui_utils, "ADDON_PACKAGE", "ankiaddon"),
        patch.object(gui_utils, "mw") as mock_mw,
        patch.object(gui_utils, "notifications") as mock_notifications,
    ):
        result = gui_utils.insert_profile_settings_in_config(sample_profile)

        assert result is False
        mock_notifications.config_not_found_error.assert_called_once()
        mock_mw.addonManager.writeConfig.assert_not_called()
        mock_notifications.profile_with_such_name_already_exists.assert_not_called()


def test_update_profile_settings_same_name(sample_profile):
    original_name = "Korean Profile (Proper Prompt)"
    fake_config = {
        "OPENAI_API_KEY": "",
        "Profiles": copy.deepcopy(sample_profile),
    }

    edited_profile = copy.deepcopy(sample_profile)
    edited_profile[original_name]["selected_model"] = "New Ai model"
    edited_profile[original_name]["prompt_text"] = "Updated prompt text"

    with (
        patch.object(gui_utils, "CONFIG", fake_config),
        patch.object(gui_utils, "ADDON_PACKAGE", "ankiaddon"),
        patch.object(gui_utils, "mw") as mock_mw,
        patch.object(gui_utils, "notifications") as mock_notifications,
        patch.object(gui_utils, "sort_profiles_dict") as mock_sort,
    ):
        result = gui_utils.update_profile_settings_name(
            edited_profile,
            profile_name_was_edited=False,
        )

        assert result is True
        assert fake_config["Profiles"][original_name]["selected_model"] == "New Ai model"
        assert fake_config["Profiles"][original_name]["prompt_text"] == "Updated prompt text"
        assert fake_config["OPENAI_API_KEY"] == ""
        assert list(fake_config.keys()) == ["OPENAI_API_KEY", "Profiles"]
        assert len(fake_config["Profiles"]) == 1

        mock_sort.assert_not_called()
        mock_mw.addonManager.writeConfig.assert_called_once_with("ankiaddon", fake_config)
        mock_notifications.profile_with_such_name_already_exists.assert_not_called()
        mock_notifications.config_not_found_error.assert_not_called()


def test_update_profile_settings_rename_success(sample_profile):
    original_name = "Korean Profile (Proper Prompt)"
    new_name = "Korean Vocab v2"
    second_profile = {
        "Korean Profile (Make text red)": {
            "selected_card_type": "Korean Vocab",
            "selected_fields": [
                "Korean",
                "English"
            ],
            "selected_fields_settings": {
                "Korean": {
                    "strip_html": False,
                    "strip_brackets": False,
                    "convert_cloze": False,
                    "strip_non_ascii": False
                },
                "English": {
                    "strip_html": False,
                    "strip_brackets": False,
                    "convert_cloze": False,
                    "strip_non_ascii": False
                }
            },
            "selected_model": "gpt-6-luna",
            "generate_as_new_cards": True,
            "deck_for_generated_cards": "Test Deck",
            "add_tag_to_generated_cards": False,
            "tag_name_for_generated_cards": None,
            "prompt_text": "Don't change the fields in any way(You can only change field color). Make fields red using HTML tags."
    }
}

    existing_profiles = {
        original_name: copy.deepcopy(sample_profile[original_name]),
        **second_profile,
    }

    fake_config = {
        "OPENAI_API_KEY": "",
        "Profiles": copy.deepcopy(existing_profiles),
    }

    edited_profile = {
        new_name: copy.deepcopy(sample_profile[original_name]),
    }
    sorted_result = {
        new_name: copy.deepcopy(sample_profile[original_name]),
        **second_profile,
    }

    with (
        patch.object(gui_utils, "CONFIG", fake_config),
        patch.object(gui_utils, "ADDON_PACKAGE", "ankiaddon"),
        patch.object(gui_utils, "mw") as mock_mw,
        patch.object(gui_utils, "notifications") as mock_notifications,
        patch.object(gui_utils, "sort_profiles_dict", return_value=sorted_result) as mock_sort,
    ):
        result = gui_utils.update_profile_settings_name(
                edited_profile,
                profile_name_was_edited=True,
                original_profile_name=original_name,
            )

        assert result is True
        assert fake_config["Profiles"] == sorted_result
        assert original_name not in fake_config["Profiles"]
        assert fake_config["OPENAI_API_KEY"] == ""
        assert list(fake_config.keys()) == ["OPENAI_API_KEY", "Profiles"]
        assert len(fake_config["Profiles"]) == 2

        mock_sort.assert_called_once()
        mock_mw.addonManager.writeConfig.assert_called_once_with("ankiaddon", fake_config)
        mock_notifications.profile_with_such_name_already_exists.assert_not_called()
        mock_notifications.config_not_found_error.assert_not_called()


def test_update_profile_settings_rename_duplicate_name(sample_profile):
    original_name = "Korean Profile (Proper Prompt)"

    second_profile = {
        "Korean Profile (Make text red)": {
            "selected_card_type": "Korean Vocab",
            "selected_fields": [
                "Korean",
                "English"
            ],
            "selected_fields_settings": {
                "Korean": {
                    "strip_html": False,
                    "strip_brackets": False,
                    "convert_cloze": False,
                    "strip_non_ascii": False
                },
                "English": {
                    "strip_html": False,
                    "strip_brackets": False,
                    "convert_cloze": False,
                    "strip_non_ascii": False
                }
            },
            "selected_model": "gpt-6-luna",
            "generate_as_new_cards": True,
            "deck_for_generated_cards": "Test Deck",
            "add_tag_to_generated_cards": False,
            "tag_name_for_generated_cards": None,
            "prompt_text": "Don't change the fields in any way(You can only change field color). Make fields red using HTML tags."
        }
    }
    second_profile_name = next(iter(second_profile))

    existing_profiles = {
        original_name: copy.deepcopy(sample_profile[original_name]),
        **second_profile,
    }

    fake_config = {
        "OPENAI_API_KEY": "",
        "Profiles": copy.deepcopy(existing_profiles),
    }

    edited_profile = {
        second_profile_name: sample_profile[original_name],
    }

    with (
        patch.object(gui_utils, "CONFIG", fake_config),
        patch.object(gui_utils, "ADDON_PACKAGE", "ankiaddon"),
        patch.object(gui_utils, "mw") as mock_mw,
        patch.object(gui_utils, "notifications") as mock_notifications,
        patch.object(gui_utils, "sort_profiles_dict") as mock_sort,
    ):
        result = gui_utils.update_profile_settings_name(
            edited_profile,
            profile_name_was_edited=True,
            original_profile_name=original_name,
        )

        assert result is False
        assert fake_config["Profiles"] == existing_profiles
        assert fake_config["OPENAI_API_KEY"] == ""
        assert list(fake_config.keys()) == ["OPENAI_API_KEY", "Profiles"]
        assert len(fake_config["Profiles"]) == 2

        mock_notifications.profile_with_such_name_already_exists.assert_called_once_with(second_profile_name)
        mock_sort.assert_not_called()
        mock_mw.addonManager.writeConfig.assert_not_called()
        mock_notifications.config_not_found_error.assert_not_called()


@pytest.mark.parametrize("empty_config", [None, {}])
def test_update_profile_settings_config_not_found(sample_profile, empty_config):
    with (
        patch.object(gui_utils, "CONFIG", empty_config),
        patch.object(gui_utils, "ADDON_PACKAGE", "ankiaddon"),
        patch.object(gui_utils, "mw") as mock_mw,
        patch.object(gui_utils, "notifications") as mock_notifications,
    ):
        result = gui_utils.update_profile_settings_name(
            sample_profile,
            profile_name_was_edited=False,
        )

        assert result is False
        mock_notifications.config_not_found_error.assert_called_once()
        mock_mw.addonManager.writeConfig.assert_not_called()
        mock_notifications.profile_with_such_name_already_exists.assert_not_called()