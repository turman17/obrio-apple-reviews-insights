from typing import List, Dict

from app.services.processing import preprocess_reviews
from app.services.metrics import calculate_metrics
from app.services.phrases import extract_problem_sentences
from app.services.ai_insights import generate_ai_insights
from app.services.insights import add_sentiment, extract_negative_keywords


def run_pipeline(app_name: str, reviews: List[dict]) -> Dict[str, object]:
    processed = preprocess_reviews(reviews)
    processed = add_sentiment(processed)
    metrics = calculate_metrics(processed)

    sentiment_distribution = {
        "positive": sum(1 for r in processed if r["sentiment"] == "positive"),
        "neutral": sum(1 for r in processed if r["sentiment"] == "neutral"),
        "negative": sum(1 for r in processed if r["sentiment"] == "negative"),
    }

    negative_phrases = extract_problem_sentences(processed)
    negative_keywords = extract_negative_keywords(processed)

    insights = generate_ai_insights(
        app_name=app_name,
        negative_phrases=negative_phrases,
        metrics=metrics,
    )

    return {
        "metrics": metrics,
        "sentiment_distribution": sentiment_distribution,
        "negative_phrases": negative_phrases,
        "negative_keywords": negative_keywords,
        "insights": insights,
    }
