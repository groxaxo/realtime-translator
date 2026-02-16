# AGENTS.md

This is a LiveKit Agents project for realtime voice translation between English and Spanish.

## Project Structure

This Python project uses `uv` for package management. The agent entrypoint is `src/agent.py`.

```
translator_agent/
├── src/
│   ├── agent.py       # Main agent entrypoint
│   └── translator.py  # Translation utilities
├── pyproject.toml     # Dependencies
└── Dockerfile
```

## How It Works

1. **Audio Input** → User speaks in English or Spanish
2. **STT (Parakeet)** → Transcribes audio to text with auto language detection
3. **Translation (LLM)** → Translates text to target language
4. **TTS (Auralis/Kokoro)** → Synthesizes translated speech
5. **Audio Output** → User hears translation

## Commands

```bash
# Development mode
uv run python src/agent.py dev

# Production mode  
uv run python src/agent.py start

# Format code
uv run ruff format

# Lint code
uv run ruff check
```

## Configuration

Copy `.env.example` to `.env.local` for local development.

Key environment variables:
- `TTS_MODE` - `gpu` (Auralis) or `cpu` (Kokoro)
- `PARAKEET_BASE_URL` - STT service URL
- `LLAMA_BASE_URL` - Translation LLM URL
