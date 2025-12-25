import json
import sys
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.services.pipeline import run_pipeline


def export_report(app_name: str):
    raw_path = Path(f"data/raw/{app_name.lower()}_reviews.json")

    if not raw_path.exists():
        raise FileNotFoundError(
            f"No reviews found for '{app_name}'. Run /collect first."
        )

    with open(raw_path, "r", encoding="utf-8") as f:
        reviews = json.load(f)

    pipeline_result = run_pipeline(app_name=app_name, reviews=reviews)

    report = {
        "app_name": app_name,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "metrics": pipeline_result["metrics"],
        "sentiment_distribution": pipeline_result["sentiment_distribution"],
        "negative_phrases": pipeline_result["negative_phrases"],
        "negative_keywords": pipeline_result["negative_keywords"],
        "insights": pipeline_result["insights"],
    }

    report["insights"] = sorted(
        report["insights"],
        key=lambda x: (x.get("area") == "other", -x.get("confidence", 0)),
    )

    out_dir = Path(f"reports/{app_name.lower()}")
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(out_dir / "report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    with open(out_dir / "report.md", "w", encoding="utf-8") as f:
        f.write(render_markdown(report))

    print(f"Report exported to {out_dir.resolve()}")


def render_markdown(report: dict) -> str:
    lines = []

    lines.append(f"# Review Insights Report — {report['app_name']}\n")
    lines.append(f"_Generated at: {report['generated_at']}_\n")
    lines.append("## Metrics\n")
    lines.append(f"- **Average rating:** {report['metrics']['average_rating']}")
    lines.append(f"- **Total reviews:** {report['metrics']['total_reviews']}\n")
    lines.append("## Sentiment Distribution\n")
    for k, v in report["sentiment_distribution"].items():
        lines.append(f"- **{k.capitalize()}**: {v}")
    lines.append("")

    lines.append("## Key Insights\n")

    for i, insight in enumerate(report["insights"], 1):
        lines.append(f"### {i}. {insight['area'].replace('_', ' ').title()}")
        lines.append(f"**Summary:** {insight['problem_summary']}")

        if insight.get("count") is not None:
            lines.append(
                f"- **Affected problem reports:** {insight['count']} / {insight['total']} "
                f"({int(insight['confidence'] * 100)}%)"
            )

        if insight.get("evidence"):
            lines.append("**Evidence:**")
            for e in insight["evidence"]:
                lines.append(f"- {e}")

        if insight.get("recommendation"):
            lines.append(f"**Recommendation:** {insight['recommendation']}")

        lines.append("")

    lines.append("## Negative Keywords\n")
    for keyword, count in report.get("negative_keywords", []):
        lines.append(f"- **{keyword}**: {count}")
    lines.append("")

    lines.append("## Visualizations\n")
    lines.append("### Rating Distribution\n")
    lines.append("![Rating Distribution](rating_distribution.png)\n")
    lines.append("### Sentiment Distribution\n")
    lines.append("![Sentiment Distribution](sentiment_distribution.png)\n")

    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/export_report.py <app_name>")
        sys.exit(1)

    export_report(sys.argv[1])
