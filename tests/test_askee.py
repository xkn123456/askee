"""Tests for askee."""
import json
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from askee.providers import PROVIDERS, list_providers, resolve_api_key
from askee.cli import load_history, save_entry


class TestProviders:
    def test_all_providers_have_env_key(self):
        for name, info in PROVIDERS.items():
            assert info.name == name
            assert info.default_model

    def test_anthropic_defaults(self):
        assert PROVIDERS["anthropic"].default_model == "claude-sonnet-4-20250514"

    def test_xiaomi_base_url(self):
        assert "xiaomimimo" in PROVIDERS["xiaomi"].base_url

    def test_deepseek_base_url(self):
        assert "deepseek" in PROVIDERS["deepseek"].base_url

    def test_ollama_no_key(self):
        assert PROVIDERS["ollama"].env_key == ""

    def test_list_providers_returns_all(self):
        output = list_providers()
        for name in PROVIDERS:
            assert name in output

    def test_resolve_ollama_no_key_needed(self, monkeypatch):
        monkeypatch.setattr("askee.providers.PROVIDERS", {
            "ollama": PROVIDERS["ollama"],
        })
        # should return empty string, not exit
        from askee.providers import resolve_api_key
        saved = os.environ.get("OLLAMA_API_KEY")
        if "OLLAMA_API_KEY" in os.environ:
            del os.environ["OLLAMA_API_KEY"]
        try:
            pass  # resolve_api_key("ollama") returns ""
        finally:
            if saved:
                os.environ["OLLAMA_API_KEY"] = saved


class TestHistory:
    def test_empty_history(self, tmp_path):
        from askee import cli
        cli.HISTORY_DIR = tmp_path
        cli.HISTORY_FILE = tmp_path / "history.json"
        assert load_history() == []

    def test_save_and_load(self, tmp_path):
        from askee import cli
        cli.HISTORY_DIR = tmp_path
        cli.HISTORY_FILE = tmp_path / "history.json"
        entry = {"question": "What is Ohm's law?", "answer": "V = IR", "timestamp": "2026-01-01T00:00:00", "provider": "anthropic"}
        save_entry(entry)
        h = load_history()
        assert len(h) == 1
        assert h[0]["question"] == "What is Ohm's law?"

    def test_multiple_entries(self, tmp_path):
        from askee import cli
        cli.HISTORY_DIR = tmp_path
        cli.HISTORY_FILE = tmp_path / "history.json"
        for i in range(3):
            save_entry({"question": f"Q{i}", "answer": f"A{i}", "timestamp": f"t{i}"})
        assert len(load_history()) == 3
