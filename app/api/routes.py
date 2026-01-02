import json
import logging
import time
import uuid
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import (
    CollectRequest,
    CollectResponse,
    InsightsResponse,
    ReviewsResponse,
)
from app.services.scraper import collect_reviews

from app.services.pipeline import run_pipeline

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")


@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.post("/collect", response_model=CollectResponse)
async def collect_reviews_endpoint(payload: CollectRequest):
    correlation_id = uuid.uuid4().hex
    start_time = time.perf_counter()
    try:
        reviews = await collect_reviews(app_name=payload.app_name, limit=payload.limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    data_dir = Path("data/raw")
    data_dir.mkdir(parents=True, exist_ok=True)

    file_path = data_dir / f"{payload.app_name.lower()}_reviews.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(reviews, f, ensure_ascii=False, indent=2)

    elapsed = time.perf_counter() - start_time
    logger.info(
        "reviews_collected app=%s limit=%s duration_s=%.3f correlation_id=%s",
        payload.app_name,
        payload.limit,
        elapsed,
        correlation_id,
    )
    return CollectResponse(
        app_name=payload.app_name, reviews_count=len(reviews), reviews=reviews
    )


@router.get("/reviews", response_model=ReviewsResponse)
def get_reviews(app_name: str):
    correlation_id = uuid.uuid4().hex
    app_name = app_name.strip().lower()
    if not app_name:
        raise HTTPException(status_code=422, detail="app_name must not be empty")

    file_path = Path(f"data/raw/{app_name}_reviews.json")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="No reviews found for this app.")

    with open(file_path, "r", encoding="utf-8") as f:
        reviews = json.load(f)

    logger.info(
        "reviews_fetched app=%s reviews_count=%s correlation_id=%s",
        app_name,
        len(reviews),
        correlation_id,
    )
    return {
        "app_name": app_name,
        "reviews_count": len(reviews),
        "reviews": reviews,
    }


@router.get("/insights", response_model=InsightsResponse)
async def get_insights(
    app_name: str,
    auto_collect: bool = False,
    limit: int = Query(default=100, ge=10, le=300),
):
    correlation_id = uuid.uuid4().hex
    start_time = time.perf_counter()
    app_name = app_name.strip().lower()
    if not app_name:
        raise HTTPException(status_code=422, detail="app_name must not be empty")

    file_path = Path(f"data/raw/{app_name}_reviews.json")
    auto_collected = False

    if not file_path.exists():
        if not auto_collect:
            raise HTTPException(
                status_code=404,
                detail="No reviews found. Please collect reviews first or enable auto_collect.",
            )

        try:
            reviews = await collect_reviews(app_name=app_name, limit=limit)
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Auto-collection failed: {str(e)}"
            )

        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(reviews, f, ensure_ascii=False, indent=2)
        auto_collected = True

    with open(file_path, "r", encoding="utf-8") as f:
        reviews = json.load(f)

    pipeline_result = run_pipeline(app_name=app_name, reviews=reviews)

    response = {
        "app_name": app_name,
        "auto_collected": auto_collected,
        "metrics": pipeline_result["metrics"],
        "sentiment_distribution": pipeline_result["sentiment_distribution"],
        "negative_phrases": pipeline_result["negative_phrases"],
        "negative_keywords": pipeline_result["negative_keywords"],
        "insights": pipeline_result["insights"],
    }
    elapsed = time.perf_counter() - start_time
    logger.info(
        "insights_generated app=%s auto_collect=%s duration_s=%.3f correlation_id=%s",
        app_name,
        auto_collected,
        elapsed,
        correlation_id,
    )
    return response
