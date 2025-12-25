from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Tuple

class CollectRequest(BaseModel):
    app_name: str
    limit: int = Field(default=100, ge=10, le=300)

    @field_validator("app_name")
    def normalize_app_name(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("app_name must be a string")
        normalized = value.strip().lower()
        if not normalized:
            raise ValueError("app_name must not be empty")
        return normalized
    
class Review(BaseModel):
    review_id: str
    title: str
    text: str
    rating: int

class CollectResponse(BaseModel):
    app_name: str
    reviews_count: int
    reviews: List[Review]


class InsightItem(BaseModel):
    area: str
    problem_summary: str
    evidence: List[str]
    count: int = 0
    total: int = 0
    confidence: float = 0.0
    recommendation: str


class Metrics(BaseModel):
    average_rating: float
    rating_distribution: Dict[str, float]
    total_reviews: int


class InsightsResponse(BaseModel):
    app_name: str
    auto_collected: bool
    metrics: Metrics
    sentiment_distribution: Dict[str, int]
    negative_phrases: List[str]
    negative_keywords: List[Tuple[str, int]]
    insights: List[InsightItem]


class ReviewsResponse(BaseModel):
    app_name: str
    reviews_count: int
    reviews: List[Review]
