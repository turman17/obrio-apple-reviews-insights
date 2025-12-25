# Apple App Store Reviews Insights

## Short Description
A Python system that collects Apple App Store reviews via SerpApi, processes and analyzes the text with rule-based NLP, and exposes insights through a REST API and offline reports with visualizations.

## Scope Disclaimer

This project is intentionally scoped as a take-home assignment.

Production-grade concerns such as pagination, concurrency-safe storage,
rate-limiting, retries, and distributed persistence are acknowledged but
intentionally omitted to keep the solution focused, readable, and easy to review.

## Key Features
- Collects Apple App Store reviews using SerpApi (Apple Reviews engine)
- Samples exactly 100 random reviews when available to keep datasets consistent
- Processes and enriches reviews with sentiment labels and extracted problem phrases
- Computes core product metrics and sentiment distribution
- Generates actionable insights with optional LLM enhancement via LM Studio
- Exposes a FastAPI-based REST API for programmatic access
- Produces offline reports and matplotlib visualizations

## System Architecture
1. Data collection fetches reviews from SerpApi and stores raw JSON locally.
2. Processing normalizes reviews, applies rule-based sentiment analysis, and extracts phrases.
3. Metrics aggregation computes ratings and sentiment statistics.
4. Insights generation uses deterministic rules, optionally refined by a local LLM.
5. Outputs are served through the API and/or exported as reports with charts.

## Tech Stack
- Python 3.10+
- FastAPI for the REST API
- Requests for external API calls
- NLTK for rule-based sentiment analysis and text processing
- Matplotlib for visualizations
- LM Studio (optional) for local LLM insights

## API Overview
Base path: `/api`

- `GET /api/health` — Health check
- `POST /api/collect` — Collect reviews for a given app and persist locally
- `GET /api/reviews` — Download raw stored reviews for a given app (query param `app_name`)
- `GET /api/insights` — Generate metrics and insights from stored reviews (supports query params like `app_name`, `auto_collect`, `limit`)

## Data Processing & NLP Approach
- Sentiment analysis: rule-based classification using NLTK to label reviews as positive, neutral, or negative.
- Phrase extraction: identifies problem phrases/sentences from negative reviews for qualitative signals.
- Metrics: computes average rating, total review count, and sentiment distribution.

## AI-Powered Insights
- Optional LLM enrichment via a locally hosted LM Studio instance.
- If the LLM is unavailable or returns invalid output, the system automatically falls back to deterministic insights. This guarantees that the API always returns usable results and never fails due to AI instability.

## Why This Approach

This system intentionally combines deterministic NLP with optional LLM-based enrichment.

Rule-based sentiment analysis ensures:
- predictable behavior
- fast execution
- zero external inference dependency

Local LLM enrichment (via LM Studio) is used only for higher-level reasoning:
- clustering issues
- summarizing root causes
- generating actionable recommendations

This hybrid design keeps the system reliable in production while allowing AI-powered insights when available.

## Visualization & Reporting
- Offline report generation exports JSON and Markdown to `reports/<app_name>/`.
- Matplotlib visualizations include rating distribution and sentiment distribution charts.

## Folder Structure
```
.
├── app/
│   ├── api/
│   ├── scripts/
│   └── services/
├── data/
│   ├── processed/
│   └── raw/
├── reports/
├── scripts/
├── requirements.txt
└── README.md
```

## Setup & Installation
- Python: 3.10+
- Create and activate a virtual environment
- Install dependencies:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Environment Variables
Create a `.env` file in the project root and set the SerpApi key:

```bash
SERPAPI_API_KEY=your_key_here
```

#### LLM (optional)
To enable AI insights, run LM Studio locally and set:

```bash
LM_STUDIO_BASE_URL=http://localhost:1234/v1
LM_STUDIO_MODEL=qwen2.5-7b-instruct-1m
```

If LM Studio is not available, the system automatically falls back to rule-based insights.

## Running the Project

Get reviews/Generate insights (via API):
```bash
uvicorn app.main:app --reload  
```

Export report:
```bash
python scripts/export_report.py <app_name>
```

Generate visualizations:
```bash
python scripts/visualize.py <app_name>
```

## Testing
Run the test suite with pytest:

```bash
pytest -q
```

## Sample Output
Reports are written to `reports/<app_name>/` and include:
- `report.json` with metrics, sentiment distribution, and extracted phrases
- `report.md` with a human-readable summary
- Charts for rating distribution and sentiment distribution

Included examples:
- `reports/instagram/`(processed without AI) and `reports/facebook/`(processed with AI) contain sample reports.
- `data/raw/instagram_reviews.json` and `data/raw/facebook_reviews.json` provide raw imports to test insight generation.
- `reports/ai-tiktok` and `reports/non-ai-tiktok` examples from demo video

## Error Handling & Edge Cases
- Missing SerpApi key raises an explicit error before network calls.
- Empty or missing review data triggers a clear exception and avoids generating partial reports.
- LLM failures do not block report generation; deterministic insights are used instead.

## Design Decisions & Trade-offs
- Sampling 100 random reviews provides consistent dataset size for downstream analysis.
- Rule-based sentiment avoids external dependencies and keeps inference fast and deterministic.
- Concurrency is intentionally minimized to reduce API rate-limit and stability issues.

## Known Limitations

- Insights quality depends on the quality and diversity of user reviews.
- Rule-based sentiment may miss sarcasm or nuanced emotion.
- LLM-generated insights are not deterministic and should be treated as advisory.

## Scalability & Production Notes

- Review collection is currently executed on-demand and stored locally.
- The storage layer can be replaced with S3 / GCS without changing business logic.
- Insight generation is stateless and can be horizontally scaled.
- Visualization and report export are intentionally separated from the API layer.

## Deliverables Checklist
- [x] Python codebase
- [x] REST API
- [x] Offline analytics reports
- [x] Visualized insights
- [x] Demo-ready project structure
- [ ] Cloud deployment
