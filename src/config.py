"""Central project paths and constants.

All paths are resolved relative to the repository root so scripts and the
notebook behave the same regardless of the current working directory.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = PROJECT_ROOT / "data" / "insurance_data.csv"
FEEDBACK_FILE = PROJECT_ROOT / "data" / "customer_feedback.csv"
SCREENSHOTS_DIR = PROJECT_ROOT / "screenshots"
OUTPUT_DIR = PROJECT_ROOT / "output"
DOCS_DIR = PROJECT_ROOT / "docs"
MODEL_DIR = PROJECT_ROOT / "models"

# Age buckets used for demographic breakdowns.
AGE_BINS = [17, 25, 35, 45, 55, 65, 120]
AGE_LABELS = ["18-25", "26-35", "36-45", "46-55", "56-65", "65+"]

# Claim statuses present in the data. "Settled" and "Pending" represent a
# claim that was accepted or is still open; "Rejected" was declined.
CLAIM_STATUSES = ("Settled", "Pending", "Rejected")
VALID_CLAIM_STATUSES = ("Settled", "Pending")

# --- customer-feedback sentiment ------------------------------------
# Pretrained transformer used to create the "teacher" sentiment labels.
SENTIMENT_MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
# Trained sklearn model distilled from the teacher (runs without torch).
SENTIMENT_MODEL_FILE = MODEL_DIR / "sentiment_model.joblib"
SENTIMENT_METRICS_FILE = MODEL_DIR / "sentiment_metrics.json"
# Score -> label thresholds (0-1 score, matching the Power BI dashboard bands).
EXCELLENT_MIN_SCORE = 0.80
GOOD_MIN_SCORE = 0.50
SENTIMENT_LABELS = ("Needs Improvement", "Good", "Excellent")
RANDOM_SEED = 42

__all__ = [
    "PROJECT_ROOT",
    "DATA_FILE",
    "FEEDBACK_FILE",
    "SCREENSHOTS_DIR",
    "OUTPUT_DIR",
    "DOCS_DIR",
    "MODEL_DIR",
    "AGE_BINS",
    "AGE_LABELS",
    "CLAIM_STATUSES",
    "VALID_CLAIM_STATUSES",
    "SENTIMENT_MODEL_NAME",
    "SENTIMENT_MODEL_FILE",
    "SENTIMENT_METRICS_FILE",
    "EXCELLENT_MIN_SCORE",
    "GOOD_MIN_SCORE",
    "SENTIMENT_LABELS",
    "RANDOM_SEED",
]
