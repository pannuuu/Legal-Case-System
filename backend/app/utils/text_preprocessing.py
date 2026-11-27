"""Text preprocessing and constitutional article extraction matching the Experiment 3 notebook."""

from functools import lru_cache
from pathlib import Path
import re

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

_NLTK_DATA_DIR = Path(__file__).resolve().parents[2] / ".venv" / "nltk_data"
if _NLTK_DATA_DIR.exists():
    nltk_dir_str = str(_NLTK_DATA_DIR)
    if nltk_dir_str not in nltk.data.path:
        nltk.data.path.insert(0, nltk_dir_str)

# Notebook Cell 73: has_constitutional_article_v2 patterns (applied to raw text)
_CONSTITUTIONAL_PATTERNS = (
    re.compile(
        r"\barticles?\s*[-.]?\s*\d{1,3}"
        r"(?:\s*[a-z]{1,2})?"
        r"(?:\s*(?:and|,)\s*\d{1,3}"
        r"(?:\s*[a-z]{1,2})?)*"
        r"\s+(?:of|under)\s+"
        r"(?:the\s+)?constitution\b",
        flags=re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"\barticles?\s*[-.]?\s*\d{1,3}"
        r"(?:\s*[a-z]{1,2})?"
        r".{0,250}?"
        r"\bconstitution\b",
        flags=re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"\bconstitution\b"
        r".{0,250}?"
        r"\barticles?\s*[-.]?\s*\d{1,3}"
        r"(?:\s*[a-z]{1,2})?",
        flags=re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"\bart\.\s*"
        r"\d{1,3}"
        r"(?:\s*[a-z]{1,2})?"
        r".{0,250}?"
        r"\bconstitution\b",
        flags=re.IGNORECASE | re.DOTALL,
    ),
)

_PRESERVED_NEGATIONS = {"not", "no", "nor"}


@lru_cache(maxsize=1)
def _get_nlp_resources() -> tuple[set[str], WordNetLemmatizer]:
    """Load NLTK stopwords (preserving negations) and WordNet lemmatizer once."""
    required = [
        ("corpora/stopwords", "stopwords"),
        ("corpora/wordnet", "wordnet"),
        ("corpora/omw-1.4", "omw-1.4"),
        ("tokenizers/punkt", "punkt"),
        ("tokenizers/punkt_tab", "punkt_tab"),
    ]
    for resource_path, package_name in required:
        try:
            nltk.data.find(resource_path)
        except LookupError:
            download_target = str(_NLTK_DATA_DIR) if _NLTK_DATA_DIR.parent.exists() else None
            nltk.download(package_name, download_dir=download_target, quiet=True)

    stop_words = set(stopwords.words("english")) - _PRESERVED_NEGATIONS
    lemmatizer = WordNetLemmatizer()
    return stop_words, lemmatizer


def clean_case_text(case_text: str) -> str:
    """Validate and normalize whitespace on raw case_text."""
    if not isinstance(case_text, str):
        raise ValueError("case_text must be a string.")
    cleaned = " ".join(case_text.split()).strip()
    if not cleaned:
        raise ValueError("case_text must not be empty or whitespace-only.")
    return cleaned


def preprocess_text(text: str) -> str:
    """Reproduce Experiment 3 notebook Step 7 (Cell 11) preprocessing before TF-IDF."""
    if not isinstance(text, str) or not text.strip():
        return ""

    stop_words, lemmatizer = _get_nlp_resources()
    lowered = text.lower()
    alnum = re.sub(r"[^a-z0-9\s]", " ", lowered)
    words = word_tokenize(alnum)
    processed = [
        lemmatizer.lemmatize(word)
        for word in words
        if word not in stop_words and len(word) > 2
    ]
    return " ".join(processed)


def detect_constitutional_article_reference(case_text: str) -> bool:
    """Reproduce Experiment 3 notebook Cell 73 (`has_constitutional_article_v2`) on raw text."""
    if not isinstance(case_text, str) or not case_text.strip():
        return False

    lowered = case_text.lower()
    return any(pattern.search(lowered) for pattern in _CONSTITUTIONAL_PATTERNS)
