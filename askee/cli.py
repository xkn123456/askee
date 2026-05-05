"""askee CLI - ask EE questions, get answers in your terminal."""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime

from . import __version__
from .providers import build_client, list_providers, PROVIDERS

HISTORY_DIR = Path.home() / ".askee"
HISTORY_FILE = HISTORY_DIR / "history.json"

SYSTEM_PROMPT = (
    "You are an electrical engineering tutor. "
    "Answer clearly with step-by-step reasoning. "
    "Include formulas and calculations where relevant. "
    "Use plain text (no markdown formatting for math - use V=IR style notation)."
)


# --- history ---

def load_history():
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return []
    return []


def save_entry(entry):
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    history = load_history()
    history.append(entry)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


# --- ask ---

def cmd_ask(args):
    provider = args.provider or os.getenv("ASKEE_PROVIDER", "anthropic")
    client = build_client(provider, args.model)
    model_name = getattr(client, "model", provider)

    print(f"\n  \033[36mQ:\033[0m {args.question}")
    print(f"  \033[90m[{provider} / {model_name}]\033[0m\n")

    try:
        answer = client.ask(args.question, SYSTEM_PROMPT)
    except Exception as e:
        sys.exit(f"  \033[31mError:\033[0m {e}")

    print(f"  \033[32mA:\033[0m")
    for line in answer.strip().split("\n"):
        print(f"    {line}")
    print()

    if args.save:
        entry = {
            "question": args.question,
            "answer": answer,
            "timestamp": datetime.now().isoformat(),
            "provider": provider,
            "model": model_name,
        }
        save_entry(entry)
        print(f"  \033[90m(session saved)\033[0m")

    if args.note and args.vault:
        vault = Path(args.vault).expanduser()
        if vault.is_dir():
            slug = "".join(c if c.isalnum() or c in "-_ " else "" for c in args.question)[:60]
            slug = slug.strip().replace(" ", "-").lower()
            note_path = vault / f"askee-{slug}.md"
            with open(note_path, "w") as f:
                f.write(f"# {args.question}\n\n{answer}\n\n---\n*via askee on {datetime.now():%Y-%m-%d %H:%M}* [{provider}]\n")
            print(f"  \033[90m(note saved: {note_path.name})\033[0m")
        else:
            print(f"  \033[33mwarning: vault not found at {args.vault}\033[0m")


# --- session (multi-turn) ---

def cmd_session(args):
    provider = args.provider or os.getenv("ASKEE_PROVIDER", "anthropic")
    client = build_client(provider, args.model)
    model_name = getattr(client, "model", provider)
    history = []

    print(f"\n  \033[36mEE session [/{model_name}]\033[0m")
    print(f"  \033[90mtype 'exit' to quit, 'save' to save session\033[0m\n")

    while True:
        try:
            q = input("  \033[36mq>\033[0m ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not q:
            continue
        if q.lower() in ("exit", "quit"):
            break
        if q.lower() == "save":
            _save_session(history, provider, model_name)
            continue

        print()
        try:
            answer = client.ask(q, SYSTEM_PROMPT)
        except Exception as e:
            print(f"  \033[31mError:\033[0m {e}")
            continue

        print(f"  \033[32ma>\033[0m {answer.strip()}\n")
        history.append({"q": q, "a": answer})


def _save_session(history, provider, model_name):
    if not history:
        print("  \033[33m(no questions yet)\033[0m\n")
        return
    entry = {
        "questions": len(history),
        "conversation": history,
        "timestamp": datetime.now().isoformat(),
        "provider": provider,
        "model": model_name,
    }
    save_entry(entry)
    print(f"  \033[90m(session with {len(history)} Q&A saved)\033[0m\n")


# --- history ---

def cmd_history(args):
    history = load_history()
    if not history:
        print("  (no questions yet)")
        return

    n = args.n or len(history)
    for entry in history[-n:]:
        q = entry.get("question", entry.get("conversation", [{}])[0].get("q", "(session)"))
        ts = entry.get("timestamp", "?")[:19]
        p = entry.get("provider", "?")
        n_q = entry.get("questions", 1)
        label = f"[{p}]" if n_q == 1 else f"[{p} x{n_q}]"
        print(f"  {ts} {label:<12} {q[:90]}")


# --- providers list ---

def cmd_providers(args):
    print(list_providers())


# --- main ---

def main():
    p = argparse.ArgumentParser(prog="askee", description="EE study companion - ask questions, get answers.")
    p.add_argument("--version", action="version", version=f"askee {__version__}")
    p.add_argument("--provider", "-p", help=f"Provider (default: $ASKEE_PROVIDER or anthropic)")
    p.add_argument("--model", "-m", help="Model override (e.g. claude-opus-4-7, gpt-4o, deepseek-chat)")

    sub = p.add_subparsers(dest="command", required=True)

    # ask
    ak = sub.add_parser("ask", help="Ask a question")
    ak.add_argument("question", help="Your question")
    ak.add_argument("--save", "-s", action="store_true", help="Save to history")
    ak.add_argument("--note", "-n", action="store_true", help="Save as markdown note")
    ak.add_argument("--vault", default=os.getenv("ASKEE_VAULT", ""), help="Obsidian vault path")

    # session
    ss = sub.add_parser("session", help="Interactive Q&A session")
    ss.add_argument("--save", "-s", action="store_true", help="Auto-save session on exit")

    # history
    hi = sub.add_parser("history", help="Show recent questions")
    hi.add_argument("-n", type=int, default=10, help="Number of entries (default 10)")

    # providers
    sub.add_parser("providers", help="List supported providers")

    args = p.parse_args()

    if args.command == "ask":
        cmd_ask(args)
    elif args.command == "session":
        cmd_session(args)
    elif args.command == "history":
        cmd_history(args)
    elif args.command == "providers":
        cmd_providers(args)


if __name__ == "__main__":
    main()
