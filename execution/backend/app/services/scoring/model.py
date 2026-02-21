"""
AI Readiness Signal Weights and Category Thresholds.

Based on validation sprint findings:
- Nordstrom: 68 (Operational) - 23 AI keywords, SageMaker/Vertex AI
- Target: 62 (Operational) - 12 AI keywords, OpenAI, strong agentic signals
- Shopify: 58 (Lagging) - 17 AI keywords, culture mentions
- Macy's: 8 (No Signal) - 0 signals despite AI Strategy role
- Stellantis: 5 (No Signal) - 0 AI keywords across all domains
"""

from dataclasses import dataclass
from typing import List, Optional

from app.models.enums import AIReadinessCategory


@dataclass
class SignalWeights:
    """Weights for each signal category (must sum to 1.0)."""
    ai_keywords: float = 0.15
    agentic_signals: float = 0.20
    tool_stack: float = 0.20
    non_eng_ai: float = 0.20
    ai_in_it: float = 0.25
    
    def validate(self) -> bool:
        """Ensure weights sum to 1.0."""
        total = (
            self.ai_keywords +
            self.agentic_signals +
            self.tool_stack +
            self.non_eng_ai +
            self.ai_in_it
        )
        return abs(total - 1.0) < 0.001


# Default weights based on validation findings
DEFAULT_WEIGHTS = SignalWeights()


# Category thresholds (0-100 scale)
CATEGORY_THRESHOLDS = {
    AIReadinessCategory.TRANSFORMATIONAL: 95,
    AIReadinessCategory.LEADING: 80,
    AIReadinessCategory.OPERATIONAL: 50,
    AIReadinessCategory.LAGGING: 30,
    AIReadinessCategory.NO_SIGNAL: 0,
}


# Signal normalization caps (for converting raw counts to 0-100 scale)
SIGNAL_CAPS = {
    "ai_keywords": 40,      # 40+ tiered keyword points = 100 score
    "agentic_signals": 15,  # 15+ signals = 100 score
    "tool_stack": 5,        # 5+ tools = 100 score
    "non_eng_ai_roles": 5,  # 5+ non-eng AI roles = 100 score
    "ai_in_it": 15,         # 15+ engineering AI keywords = 100 score
}


# Known AI/ML tools for detection (reference list — detection logic in scoring_service.py)
KNOWN_TOOLS = [
    # Cloud ML Platforms
    "sagemaker", "vertex ai", "bedrock", "azure ml", "azure openai",
    "azure cognitive", "google cloud ai", "amazon q",
    # Frameworks & Libraries
    "pytorch", "tensorflow", "jax", "keras", "scikit-learn",
    "xgboost", "lightgbm", "catboost", "onnx", "triton inference",
    # LLM Providers & APIs
    "openai", "anthropic", "cohere", "mistral", "groq",
    "together ai", "fireworks ai", "replicate", "ollama", "perplexity",
    # LLM Frameworks & Orchestration
    "langchain", "langgraph", "langsmith", "llamaindex",
    "semantic kernel", "haystack", "dspy", "crewai", "autogen",
    # Model Hubs & Pretrained
    "huggingface", "transformers",
    # MLOps & Experiment Tracking
    "mlflow", "kubeflow", "wandb", "neptune", "metaflow",
    "prefect", "airflow", "ray",
    # Vector / AI Databases
    "pinecone", "weaviate", "milvus", "qdrant", "chroma", "pgvector", "faiss",
    # Infrastructure & Cloud
    "kubernetes", "aws", "gcp", "azure", "databricks", "snowflake", "spark",
    # AI Dev Tools & Coding Assistants
    "copilot", "cursor", "v0", "replit", "tabnine", "codeium", "windsurf",
    # Specific Models & Products
    "claude", "gemini", "llama", "stable diffusion", "dall-e", "whisper",
    # Observability & Evaluation
    "langfuse", "helicone", "arize", "whylabs", "deepchecks",
    # Code & Repo Hosting
    "github",
]


def get_category(score: float) -> AIReadinessCategory:
    """Determine category from score."""
    if score >= CATEGORY_THRESHOLDS[AIReadinessCategory.TRANSFORMATIONAL]:
        return AIReadinessCategory.TRANSFORMATIONAL
    elif score >= CATEGORY_THRESHOLDS[AIReadinessCategory.LEADING]:
        return AIReadinessCategory.LEADING
    elif score >= CATEGORY_THRESHOLDS[AIReadinessCategory.OPERATIONAL]:
        return AIReadinessCategory.OPERATIONAL
    elif score >= CATEGORY_THRESHOLDS[AIReadinessCategory.LAGGING]:
        return AIReadinessCategory.LAGGING
    else:
        return AIReadinessCategory.NO_SIGNAL


def get_category_label(category: AIReadinessCategory) -> str:
    """Human-readable category label."""
    labels = {
        AIReadinessCategory.TRANSFORMATIONAL: "Transformational",
        AIReadinessCategory.LEADING: "Leading",
        AIReadinessCategory.OPERATIONAL: "Operational",
        AIReadinessCategory.LAGGING: "Lagging",
        AIReadinessCategory.NO_SIGNAL: "No Signal",
    }
    return labels.get(category, "Unknown")
