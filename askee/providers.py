"""LLM provider support. Add new providers here."""

import os
import sys
from dataclasses import dataclass


@dataclass
class ProviderInfo:
    name: str
    env_key: str
    default_model: str
    base_url: str | None = None
    notes: str = ""


PROVIDERS: dict[str, ProviderInfo] = {
    "anthropic": ProviderInfo(
        name="anthropic", env_key="ANTHROPIC_API_KEY",
        default_model="claude-sonnet-4-20250514",
    ),
    "openai": ProviderInfo(
        name="openai", env_key="OPENAI_API_KEY",
        default_model="gpt-4o",
    ),
    "xiaomi": ProviderInfo(
        name="xiaomi", env_key="XIAOMI_API_KEY",
        default_model="mimo-v2.5-pro",
        base_url="https://api.xiaomimimo.com/v1",
    ),
    "deepseek": ProviderInfo(
        name="deepseek", env_key="DEEPSEEK_API_KEY",
        default_model="deepseek-chat",
        base_url="https://api.deepseek.com/v1",
    ),
    "google": ProviderInfo(
        name="google", env_key="GOOGLE_API_KEY",
        default_model="gemini-2.0-flash",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    ),
    "groq": ProviderInfo(
        name="groq", env_key="GROQ_API_KEY",
        default_model="llama-3.3-70b-versatile",
        base_url="https://api.groq.com/openai/v1",
    ),
    "ollama": ProviderInfo(
        name="ollama", env_key="",
        default_model="llama3",
        base_url="http://localhost:11434/v1",
        notes="no API key needed",
    ),
    "openrouter": ProviderInfo(
        name="openrouter", env_key="OPENROUTER_API_KEY",
        default_model="anthropic/claude-sonnet-4",
        base_url="https://openrouter.ai/api/v1",
    ),
}


def resolve_api_key(provider: str) -> str:
    info = PROVIDERS.get(provider)
    if not info:
        sys.exit(f"unknown provider: {provider}")
    if not info.env_key:
        return ""
    key = os.getenv(info.env_key)
    if not key:
        sys.exit(f"missing {info.env_key} (set it or switch provider)")
    return key


def build_client(provider: str, model: str | None):
    info = PROVIDERS.get(provider)
    if not info:
        sys.exit(f"unknown provider: {provider}")

    api_key = resolve_api_key(provider)
    model = model or info.default_model

    if provider == "anthropic":
        return _anthropic_client(api_key, model)
    return _openai_compat_client(api_key, model, info.base_url)


def _anthropic_client(api_key, model):
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)

    def ask(question, system):
        resp = client.messages.create(
            model=model, system=system,
            messages=[{"role": "user", "content": question}],
            max_tokens=4096, temperature=0.3,
        )
        return resp.content[0].text if resp.content else ""
    return type("Client", (), {"ask": ask, "model": model})()


def _openai_compat_client(api_key, model, base_url):
    from openai import OpenAI
    client = OpenAI(api_key=api_key, base_url=base_url)

    def ask(question, system):
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": question}],
            max_tokens=4096, temperature=0.3,
        )
        return resp.choices[0].message.content or ""

    return type("Client", (), {"ask": ask, "model": model})()


def list_providers() -> str:
    lines = [f"  \033[1mSupported providers\033[0m\n"]
    for name, info in PROVIDERS.items():
        key = info.env_key or "(none)"
        note = f"  \033[90m{info.notes}\033[0m" if info.notes else ""
        lines.append(f"  {name:<12} {info.default_model:<30} {key}{note}")
    return "\n".join(lines)
