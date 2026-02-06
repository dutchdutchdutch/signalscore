"""Enumerations for the application."""
from enum import Enum

class AIReadinessCategory(str, Enum):
    HIGH = "high"
    MEDIUM_HIGH = "medium_high"
    MEDIUM_LOW = "medium_low"
    LOW = "low"
    TRANSFORMATIONAL = "transformational"
    NO_SIGNAL = "no_signal"


class SourceType(str, Enum):
    CAREERS_PAGE = "careers_page"
    BLOG = "blog"
    GITHUB = "github"
    NEWS = "news"
    OTHER = "other"
