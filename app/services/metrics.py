from collections import Counter
from typing import List


def calculate_metrics(reviews: list[dict]) -> dict:
    ratings = [r["rating"] for r in reviews if isinstance(r.get("rating"), int)]

    if not ratings:
        return {
            "average_rating": 0,
            "rating_distribution": {},
            "total_reviews": 0,
        }

    total = len(ratings)
    avg = round(sum(ratings) / total, 2)

    distribution = {}
    for i in range(1, 6):
        distribution[f"{i}_star"] = round(
            ratings.count(i) / total * 100, 2
        )

    return {
        "average_rating": avg,
        "rating_distribution": distribution,
        "total_reviews": total,
    }