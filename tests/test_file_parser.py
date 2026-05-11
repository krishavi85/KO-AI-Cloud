from app.services.file_parser import chunk_text


def test_chunk_text_empty():
    assert chunk_text("") == []


def test_chunk_text_splits_with_overlap():
    text = "a" * 3000
    chunks = chunk_text(text, chunk_size=1000, overlap=100)
    assert len(chunks) >= 3
    assert all(len(chunk) <= 1000 for chunk in chunks)
