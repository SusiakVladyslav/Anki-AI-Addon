import pytest
from ai import OpenAI_Anki


@pytest.mark.parametrize("html_text, text_without_html", [
    ('<font color="#ff0000">도둑</font>이 <font color="#55aaff">지갑</font>을 '
     '<font color="#55ffff">훔쳐서 </font>경찰에 신고했어요.',
     "도둑이 지갑을 훔쳐서 경찰에 신고했어요.")
],
    ids=["Korean_sentence_1"]
)
def test_strip_html(html_text, text_without_html):
    assert OpenAI_Anki.strip_html(html_text) == text_without_html

