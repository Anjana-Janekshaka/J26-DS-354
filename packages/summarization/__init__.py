"""Component 2: Hierarchical Summarization (structured L1/L2/L3, contradiction merge, live loss score)."""

from .engine import HierarchicalSummarizer, SummarizationConfig
from .generators import AssistedGenerator, LLMGenerator, RuleBasedGenerator, TierGenerator
from .loss import LossWorker, anchor_loss, anchors, current_signatures, symbol_retention_rate
from .merge import SummaryState
from .naive import NaiveSummarizer
from .records import Fact, L1Record, L2Record, L3Record

# TODO: v2 - one-shot repair re-prompt (feed dropped anchors back into generation before falling
# back to RAG) and Method 2 (dual Q&A consistency) loss scoring. Not implemented; see README.

__all__ = [
    "Fact",
    "HierarchicalSummarizer",
    "L1Record",
    "L2Record",
    "L3Record",
    "AssistedGenerator",
    "LLMGenerator",
    "LossWorker",
    "NaiveSummarizer",
    "RuleBasedGenerator",
    "SummarizationConfig",
    "SummaryState",
    "TierGenerator",
    "anchor_loss",
    "anchors",
    "current_signatures",
    "symbol_retention_rate",
]
