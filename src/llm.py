from __future__ import annotations

import os

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_ollama import ChatOllama


def get_llm() -> BaseChatModel:
    """Instancie le LLM Ollama local."""
    model = os.getenv("LLM_MODEL", "phi3")
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    temperature = float(os.getenv("LLM_TEMPERATURE", "0.0"))
    return ChatOllama(model=model, base_url=base_url, temperature=temperature)
