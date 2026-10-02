"""Answer-generation ports and the safe local fallback."""

from .extractive import ExtractiveAnswerGenerator
from .models import AnswerGenerator, GeneratedAnswer, GenerationRequest
from .openai_compatible import OpenAICompatibleGenerator
from .prompting import build_grounded_prompt

__all__ = [
    "ExtractiveAnswerGenerator",
    "AnswerGenerator",
    "GeneratedAnswer",
    "GenerationRequest",
    "OpenAICompatibleGenerator",
    "build_grounded_prompt",
]
