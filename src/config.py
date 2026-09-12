"""Central project paths and constants.

All paths are resolved relative to the repository root so scripts and the
notebook behave the same regardless of the current working directory.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = PROJECT_ROOT / "data" / "insurance_data.csv"
SCREENSHOTS_DIR = PROJECT_ROOT / "screenshots"
OUTPUT_DIR = PROJECT_ROOT / "output"
DOCS_DIR = PROJECT_ROOT / "docs"

# Age buckets used for demographic breakdowns.
AGE_BINS = [17, 25, 35, 45, 55, 65, 120]
AGE_LABELS = ["18-25", "26-35", "36-45", "46-55", "56-65", "65+"]

# Claim statuses present in the data. "Settled" and "Pending" represent a
# claim that was accepted or is still open; "Rejected" was declined.
CLAIM_STATUSES = ("Settled", "Pending", "Rejected")
VALID_CLAIM_STATUSES = ("Settled", "Pending")

__all__ = [
    "PROJECT_ROOT",
    "DATA_FILE",
    "SCREENSHOTS_DIR",
    "OUTPUT_DIR",
    "DOCS_DIR",
    "AGE_BINS",
    "AGE_LABELS",
    "CLAIM_STATUSES",
    "VALID_CLAIM_STATUSES",
]
