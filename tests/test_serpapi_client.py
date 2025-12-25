from app.services import serpapi_client


def test_parse_reviews_skips_invalid_rating():
    reviews = [
        {"id": "1", "title": "Ok", "text": "Fine", "rating": "5"},
        {"id": "2", "title": None, "text": "Bad data", "rating": "N/A"},
        {"id": "3", "title": "No rating", "text": "Missing", "rating": None},
    ]

    parsed = serpapi_client._parse_reviews(reviews)

    assert len(parsed) == 1
    assert parsed[0]["review_id"] == "1"
    assert parsed[0]["rating"] == 5
