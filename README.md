# Realtime Translator

<div align="center">

<img src="./assets/translator-logo.png" alt="Realtime Translator" width="120" />

### 🌐 Realtime Bidirectional Voice Translation

**Break language barriers instantly** — English ↔ Spanish voice translation powered by AI

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CUDA](https://img.shields.io/badge/CUDA-Optional-green.svg)](https://developer.nvidia.com/cuda-downloads)

[Quick Start](#-quick-start) • [Features](#-features) • [Architecture](#-architecture) • [Configuration](#-configuration) • [Development](#-development)

</div>

---

## ✨ Features

| Feature                       | Description                                              |
| ----------------------------- | -------------------------------------------------------- |
| 🎙️ **Realtime Translation**    | Speak naturally and hear translations in under 2 seconds |
| 🌍 **Bidirectional**           | English → Spanish and Spanish → English simultaneously   |
| 🎯 **Auto Language Detection** | No need to specify your language—just speak!             |
| 🚀 **GPU Accelerated**         | Premium quality with NVIDIA CUDA (optional)              |
| 💻 **CPU Fallback**            | Works on any machine without GPU                         |
| 🎤 **Voice Cloning**           | Preserve speaker identity in translations (GPU mode)     |
| 🔒 **100% Local**              | Complete privacy—no cloud services required              |
| 🐳 **Docker Ready**            | One-command deployment                                   |

---

## 🚀 Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & Docker Compose
- 12GB+ RAM recommended
- NVIDIA GPU + CUDA (optional, for premium TTS)

### 🐳 Docker (Recommended)

```bash
git clone https://github.com/groxaxo/realtime-translator.git
cd realtime-translator
./compose-up.sh
```

The script will:
1. Detect your hardware (CPU/GPU)
2. Prompt you to select a mode
3. Start all services

**Access the app:** [http://localhost:3000](http://localhost:3000)

### 🐍 Conda (Development)

```bash
# Create environment
conda env create -f environment.yml
conda activate translator

# Start services manually
docker compose up parakeet kokoro livekit llama_cpp -d

# Run the agent
cd translator_agent
uv run python src/agent.py dev
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Web Browser (Frontend)                    │
│                    https://YOUR_IP:8445                          │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTPS/WSS
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    NGINX SSL Proxy (:8445-8448)                  │
│   8445 → Frontend  │  8448 → LiveKit (WSS)                       │
└──────────────────────────┬──────────────────────────────────────┘
                           │ WebRTC
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     LiveKit Server (:7880)                       │
│              Real-time audio/video signaling                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Translation Agent (Python)                     │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │   Parakeet  │───▶│  LLM Trans  │───▶│ Auralis/Kokoro TTS  │  │
│  │  STT (:5092)│    │   (:11434)  │    │  (:9950/:8880)      │  │
│  └─────────────┘    └─────────────┘    └─────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Components

| Component        | Port  | SSL Port | Description                     |
| ---------------- | ----- | -------- | ------------------------------- |
| **Frontend**     | 3000  | 8445     | Next.js web interface           |
| **LiveKit**      | 7880  | 8448     | WebRTC signaling server         |
| **Parakeet TDT** | 5092  | -        | Multilingual STT (25 languages) |
| **LLaMA.cpp**    | 11434 | -        | Translation LLM                 |
| **Auralis**      | 9950  | -        | Premium TTS with voice cloning  |
| **Kokoro**       | 8880  | -        | Fast TTS (CPU fallback)         |

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file from the template:

```bash
cp .env.example .env
```

| Variable             | Default                               | Description             |
| -------------------- | ------------------------------------- | ----------------------- |
| `TTS_MODE`           | `auto`                                | `auto`, `gpu`, or `cpu` |
| `LLAMA_HF_REPO`      | `unsloth/Qwen3-4B-Instruct-2507-GGUF` | Translation LLM         |
| `LLAMA_CTX_SIZE`     | `8192`                                | LLM context window      |
| `LIVEKIT_API_KEY`    | `devkey`                              | LiveKit API key         |
| `LIVEKIT_API_SECRET` | `secret`                              | LiveKit API secret      |

### Hardware Modes

| Mode    | TTS Engine       | Quality       | VRAM Required |
| ------- | ---------------- | ------------- | ------------- |
| **GPU** | Auralis-Enhanced | Premium 48kHz | ~5GB          |
| **CPU** | Kokoro           | Good 24kHz    | None          |

### SSL Proxy (HTTPS Access)

For secure remote access, an nginx SSL proxy is available:

```bash
# Create SSL certificates
mkdir -p nginx-ssl/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx-ssl/ssl/key.pem \
  -out nginx-ssl/ssl/cert.pem

# Start SSL proxy
cd nginx-ssl && docker compose up -d
```

Set `NEXT_PUBLIC_LIVEKIT_URL=wss://YOUR_IP:8448` in `.env` and rebuild the frontend:

```bash
docker compose build frontend && docker compose up -d frontend
```

Access: `https://YOUR_IP:8445/`

---

## 🛠️ Development

### Project Structure

```
realtime-translator/
├── translator_agent/      # Python LiveKit agent
│   ├── src/
│   │   ├── agent.py       # Main agent entrypoint
│   │   └── translator.py  # Translation utilities
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/              # Next.js web UI
├── inference/             # Service configurations
│   ├── auralis/          # GPU TTS
│   └── parakeet/         # STT
├── docker-compose.yml     # CPU stack
├── docker-compose.gpu.yml # GPU overlay
├── environment.yml        # Conda environment
└── compose-up.sh          # Smart startup script
```

### Running Tests

```bash
cd translator_agent
uv run pytest
```

### Local Development

```bash
# Terminal 1: Start infrastructure
docker compose up parakeet kokoro livekit llama_cpp -d

# Terminal 2: Run agent in dev mode
cd translator_agent
uv run python src/agent.py dev
```

---

## 📊 Performance

| Metric            | GPU Mode | CPU Mode |
| ----------------- | -------- | -------- |
| **STT Latency**   | ~100ms   | ~100ms   |
| **Translation**   | ~200ms   | ~200ms   |
| **TTS Latency**   | ~150ms   | ~300ms   |
| **Total E2E**     | ~450ms   | ~600ms   |
| **Audio Quality** | 48kHz    | 24kHz    |

---

## 🙏 Acknowledgments

This project builds on amazing open-source work:

- **[Parakeet TDT](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3)** — NVIDIA's multilingual STT
- **[Auralis-Enhanced](https://github.com/groxaxo/Auralis-Enhanced)** — Production-ready TTS with FlashSR
- **[Kokoro](https://github.com/remsky/kokoro)** — Fast CPU-friendly TTS
- **[LiveKit](https://livekit.io/)** — Real-time communication platform
- **[LLaMA.cpp](https://github.com/ggml-org/llama.cpp)** — Efficient LLM inference

---

## 📄 License

MIT License — See [LICENSE](LICENSE) for details.

---

<div align="center">

**Made with ❤️ for breaking language barriers**

[⬆ Back to top](#realtime-translator)

</div>
