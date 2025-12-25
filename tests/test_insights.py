from app.services import insights


def test_sentiment_init_does_not_crash_without_vader(monkeypatch):
    def _raise_lookup_error():
        raise LookupError("missing vader")

    monkeypatch.setattr(insights, "SentimentIntensityAnalyzer", _raise_lookup_error)
    insights._SIA = None

    result = insights.analyze_sentiment("I love this app")

    assert result == "neutral"
