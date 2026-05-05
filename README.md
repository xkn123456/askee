# askee

Ask EE questions, get answers in your terminal.

I built this because I kept switching between the terminal and browser
every time I got stuck on a circuit problem. It saves Q&A for later
review and can write notes straight into an Obsidian vault.

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-..."
askee ask "What's the gain of a non-inverting op-amp?"
```

## Commands

```
askee ask "question"           Ask a question
askee session                  Interactive multi-turn session
askee history                  Show recent questions
askee providers                List supported providers
```

### ask

```bash
askee ask "Derive the transfer function of a low-pass RC filter"

# Save to history for later review
askee ask "Explain how a buck converter works" --save

# Write a markdown note directly to your vault
askee ask "Miller effect in amplifiers" --note --vault ~/obsidian/EE-Notes
```

### session

Multi-turn interactive mode. Good for working through a problem step by step.

```
askee session
q> Design a two-stage CE amplifier
a> [answer...]
q> What's the input impedance?
a> [answer...]
q> save
(session saved)
q> exit
```

### history

```bash
askee history          # last 10
askee history -n 20    # last 20
```

## Providers

| Provider | Env Key | Default Model |
|---|---|---|
| anthropic | ANTHROPIC_API_KEY | claude-sonnet-4-20250514 |
| openai | OPENAI_API_KEY | gpt-4o |
| xiaomi | XIAOMI_API_KEY | mimo-v2.5-pro |
| deepseek | DEEPSEEK_API_KEY | deepseek-chat |
| google | GOOGLE_API_KEY | gemini-2.0-flash |
| groq | GROQ_API_KEY | llama-3.3-70b-versatile |
| ollama | (none) | llama3 |
| openrouter | OPENROUTER_API_KEY | anthropic/claude-sonnet-4 |

Switch with `--provider` or `ASKEE_PROVIDER` env:

```bash
export ASKEE_PROVIDER=deepseek
askee ask "Explain feedback in op-amps"

askee --provider groq ask "Class AB amplifier biasing"

askee --provider ollama ask "Q-point analysis" --model llama3
```

### Ollama (local, no key needed)

```bash
# start a model
ollama pull llama3

# use it
askee --provider ollama ask "What's Thevenin's theorem?"
```

## Save notes to Obsidian

Set your vault path once:

```bash
export ASKEE_VAULT="~/obsidian/EE-Notes"
```

Then `askee ask "question" --note` saves a `.md` file there.

## Config reference

| Env | Default | Description |
|---|---|---|
| ASKEE_PROVIDER | anthropic | Default LLM provider |
| ASKEE_VAULT | (none) | Vault path for --note |
| PROVIDER_API_KEY | (none) | e.g. ANTHROPIC_API_KEY |

## Why

I was copy-pasting circuit questions between Obsidian and Claude over and
over. Wanted something faster. That's it.
