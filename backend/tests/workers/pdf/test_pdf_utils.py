from workers.pdf.pdf_utils import is_text_block_usable


def test_is_text_block_usable_accepts_normal_text():
    assert is_text_block_usable("Hello world from a PDF page")


def test_is_text_block_usable_rejects_null_bytes():
    assert not is_text_block_usable("Hello\x00world")


def test_is_text_block_usable_rejects_control_characters():
    assert not is_text_block_usable("Hello\x01world")


def test_is_text_block_usable_accepts_text_with_few_replacement_characters():
    assert is_text_block_usable("Hello\ufffd world from a PDF page")


def test_is_text_block_usable_rejects_when_stripping_replacement_chars_leaves_unusable_text():
    assert not is_text_block_usable("\ufffd\ufffd!!")


def test_is_text_block_usable_rejects_mostly_non_printable_garbage():
    assert not is_text_block_usable("\x00\x45\x46\x47\x48")


def test_is_text_block_usable_rejects_whitespace_only():
    assert not is_text_block_usable("   \n\t  ")


def test_is_text_block_usable_rejects_too_few_alphanumeric_characters():
    assert not is_text_block_usable("!!")
