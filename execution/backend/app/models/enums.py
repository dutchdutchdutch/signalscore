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
    PRESS_RELEASE = "press_release"
    INVESTOR_RELATIONS = "investor_relations"
    NEWSROOM = "newsroom"
    OTHER = "other"


class VerificationStatus(str, Enum):
    VERIFIED = "verified"
    PENDING = "pending"
    REJECTED = "rejected"
