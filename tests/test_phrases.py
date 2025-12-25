from app.services.phrases import extract_problem_sentences


def test_extract_problem_sentences_filters_empty_and_returns_non_empty():
    reviews = [
        {"sentiment": "negative", "clean_text_raw": "App crash every time I open it. ok."},
        {"sentiment": "negative", "clean_text_raw": ""},
        {"sentiment": "positive", "clean_text_raw": "Love it."},
    ]

    result = extract_problem_sentences(reviews, max_results=5)

    assert result
    assert "App crash every time I open it" in result
    assert "ok" not in result
