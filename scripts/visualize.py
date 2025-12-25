import json
from pathlib import Path

import matplotlib.pyplot as plt


def visualize(app_name: str, save: bool = True):
    report_dir = Path(f"reports/{app_name.lower()}")
    report_path = report_dir / "report.json"

    if not report_path.exists():
        raise FileNotFoundError(
            f"No report found for '{app_name}'. Run export_report.py first."
        )

    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)

    plot_ratings(
        report["metrics"]["rating_distribution"],
        app_name,
        report_dir,
        save,
    )

    plot_sentiment(
        report["sentiment_distribution"],
        app_name,
        report_dir,
        save,
    )


def plot_ratings(dist: dict, app_name: str, out_dir: Path, save: bool):
    labels = list(dist.keys())
    values = list(dist.values())

    plt.figure()
    plt.bar(labels, values)
    plt.title(f"Rating Distribution — {app_name}")
    plt.xlabel("Rating")
    plt.ylabel("Percentage")
    plt.tight_layout()

    if save:
        plt.savefig(out_dir / "rating_distribution.png")
        plt.close()
    else:
        plt.show()


def plot_sentiment(dist: dict, app_name: str, out_dir: Path, save: bool):
    labels = list(dist.keys())
    values = list(dist.values())

    plt.figure()
    plt.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
    plt.title(f"Sentiment Distribution — {app_name}")
    plt.tight_layout()

    if save:
        plt.savefig(out_dir / "sentiment_distribution.png")
        plt.close()
    else:
        plt.show()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python scripts/visualize.py <app_name>")
        sys.exit(1)

    visualize(sys.argv[1], save=True)