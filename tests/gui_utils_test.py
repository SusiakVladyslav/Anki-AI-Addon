import sys
import pytest
from unittest.mock import MagicMock

anki_mock = MagicMock()
aqt_mock = MagicMock()
qt_mock = MagicMock()

mw_mock = MagicMock()
mw_mock.addonManager.addon_from_module.return_value = "ankiaddon"
aqt_mock.mw = mw_mock

sys.modules["anki"] = anki_mock
sys.modules["anki.hooks"] = anki_mock.hooks
sys.modules["anki.notes"] = anki_mock.notes
sys.modules["aqt"] = aqt_mock
sys.modules["aqt.qt"] = qt_mock
sys.modules["aqt.utils"] = aqt_mock.utils
sys.modules["aqt.sound"] = aqt_mock.sound
sys.modules["aqt.browser"] = aqt_mock.browser
sys.modules["aqt.theme"] = aqt_mock.theme
sys.modules["aqt.operations"] = aqt_mock.operations

from utils.gui_utils import strip_html, strip_square_brackets, convert_cloze_to_plain_text, strip_non_ascii


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