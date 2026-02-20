"""Enumerations for the application."""
from enum import Enum

class AIReadinessCategory(str, Enum):
    LEADING = "leading"
    OPERATIONAL = "operational"
    LAGGING = "lagging"
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
