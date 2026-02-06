"""
AI Readiness Signal Weights and Category Thresholds.

Based on validation sprint findings:
- Nordstrom: 68 (Medium-High) - 23 AI keywords, SageMaker/Vertex AI
- Target: 62 (Medium-High) - 12 AI keywords, OpenAI, strong agentic signals
- Shopify: 58 (Medium-High) - 17 AI keywords, culture mentions
- Macy's: 8 (Low) - 0 signals despite AI Strategy role
- Stellantis: 5 (Low) - 0 AI keywords across all domains
"""

from dataclasses import dataclass
from typing import List, Optional

from app.models.enums import AIReadinessCategory


@dataclass
class SignalWeights:
    """Weights for each signal category (must sum to 1.0)."""
    ai_keywords: float = 0.25
    agentic_signals: float = 0.20
    tool_stack: float = 0.20
    non_eng_ai: float = 0.25
    ai_platform_team: float = 0.10
    
    def validate(self) -> bool:
        """Ensure weights sum to 1.0."""
        total = (
            self.ai_keywords +
            self.agentic_signals +
            self.tool_stack +
            self.non_eng_ai +
            self.ai_platform_team
        )
        return abs(total - 1.0) < 0.001


# Default weights based on validation findings
DEFAULT_WEIGHTS = SignalWeights()


# Category thresholds (0-100 scale)
# Category thresholds (0-100 scale)
CATEGORY_THRESHOLDS = {
    AIReadinessCategory.TRANSFORMATIONAL: 95,
    AIReadinessCategory.HIGH: 80,         # Leading
    AIReadinessCategory.MEDIUM_HIGH: 60,  # Operational
    AIReadinessCategory.MEDIUM_LOW: 30,   # Trailing
    AIReadinessCategory.LOW: 0,           # Lagging
}


# Signal normalization caps (for converting raw counts to 0-100 scale)
SIGNAL_CAPS = {
    "ai_keywords": 30,      # 30+ keywords = 100 score
    "agentic_signals": 15,  # 15+ signals = 100 score
    "tool_stack": 5,        # 5+ tools = 100 score
    "non_eng_ai_roles": 5,  # 5+ non-eng AI roles = 100 score
    "ai_platform_team": 1,  # 1+ platform team role = 100 score
}


# Known AI/ML tools for detection
KNOWN_TOOLS = [
    # Cloud ML Platforms
    "sagemaker", "vertex ai", "bedrock", "azure ml",
    # Frameworks
    "pytorch", "tensorflow", "jax", "keras",
    # LLM Tools
    "openai", "anthropic", "langchain", "llamaindex",
    "huggingface", "transformers",
    # MLOps
    "mlflow", "kubeflow", "wandb", "neptune",
    # Other
    "databricks", "snowflake ml", "copilot",
]


def get_category(score: float) -> AIReadinessCategory:
    """Determine category from score."""
    if score >= CATEGORY_THRESHOLDS[AIReadinessCategory.TRANSFORMATIONAL]:
        return AIReadinessCategory.TRANSFORMATIONAL
    elif score >= CATEGORY_THRESHOLDS[AIReadinessCategory.HIGH]:
        return AIReadinessCategory.HIGH
    elif score >= CATEGORY_THRESHOLDS[AIReadinessCategory.MEDIUM_HIGH]:
        return AIReadinessCategory.MEDIUM_HIGH
    elif score >= CATEGORY_THRESHOLDS[AIReadinessCategory.MEDIUM_LOW]:
        return AIReadinessCategory.MEDIUM_LOW
    else:
        return AIReadinessCategory.LOW


def get_category_label(category: AIReadinessCategory) -> str:
    """Human-readable category label."""
    labels = {
        AIReadinessCategory.TRANSFORMATIONAL: "Transformational",
        AIReadinessCategory.HIGH: "Leading",
        AIReadinessCategory.MEDIUM_HIGH: "On Par/Operational",
        AIReadinessCategory.MEDIUM_LOW: "Trailing",
        AIReadinessCategory.LOW: "Lagging",
        AIReadinessCategory.NO_SIGNAL: "No Signal",
    }
    return labels.get(category, "Unknown")
