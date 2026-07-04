"""Provider-agnostic LLM client.

One interface (`LLMClient.complete`) with three implementations:
Anthropic, OpenAI, and a scripted client for deterministic tests.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol

from .config import Settings


@dataclass
class LLMResponse:
    text: str
    input_tokens: int = 0
    output_tokens: int = 0


class LLMClient(Protocol):
    def complete(self, system: str, user: str, max_tokens: int = 1500) -> LLMResponse: ...


class AnthropicClient:
    def __init__(self, model: str):
        import anthropic

        self.model = model
        self._client = anthropic.Anthropic()

    def complete(self, system: str, user: str, max_tokens: int = 1500) -> LLMResponse:
        msg = self._client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return LLMResponse(
            text="".join(b.text for b in msg.content if b.type == "text"),
            input_tokens=msg.usage.input_tokens,
            output_tokens=msg.usage.output_tokens,
        )


class OpenAIClient:
    """Also serves any OpenAI-compatible endpoint (e.g. Ollama at localhost:11434/v1)."""

    def __init__(self, model: str, base_url: str | None = None, api_key: str | None = None):
        import openai

        self.model = model
        self._client = openai.OpenAI(base_url=base_url, api_key=api_key) if base_url else openai.OpenAI()

    def complete(self, system: str, user: str, max_tokens: int = 1500) -> LLMResponse:
        resp = self._client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        usage = resp.usage
        return LLMResponse(
            text=resp.choices[0].message.content or "",
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
        )


class ScriptedClient:
    """Returns queued responses in order. Used by the test suite."""

    def __init__(self, responses: list[str]):
        self._responses = list(responses)
        self.calls: list[tuple[str, str]] = []

    def complete(self, system: str, user: str, max_tokens: int = 1500) -> LLMResponse:
        self.calls.append((system, user))
        if not self._responses:
            raise RuntimeError("ScriptedClient ran out of responses")
        return LLMResponse(text=self._responses.pop(0))


def get_client(settings: Settings | None = None) -> LLMClient:
    settings = settings or Settings()
    provider = settings.resolved_provider()
    if provider == "anthropic":
        return AnthropicClient(settings.anthropic_model)
    if provider == "openai":
        return OpenAIClient(settings.openai_model)
    if provider == "ollama":  # free local models — install from ollama.com, then e.g. `ollama pull qwen2.5-coder:7b`
        return OpenAIClient(settings.ollama_model, base_url="http://localhost:11434/v1", api_key="ollama")
    if provider == "gemini":  # free-tier key from aistudio.google.com; OpenAI-compatible endpoint
        return OpenAIClient(
            settings.gemini_model,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key=os.getenv("GEMINI_API_KEY"),
        )
    if provider == "groq":  # free-tier key from console.groq.com; open-weights models
        return OpenAIClient(
            settings.groq_model,
            base_url="https://api.groq.com/openai/v1",
            api_key=os.getenv("GROQ_API_KEY"),
        )
    raise ValueError(f"Unknown provider: {provider!r}")
