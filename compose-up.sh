#!/bin/bash
# Realtime Translator - Smart Startup Script
# Automatically detects GPU and prompts for mode selection

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║          🌐 Realtime Translator - Startup                  ║"
echo "║     English ↔ Spanish Voice Translation                    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not available. Please install Docker Compose.${NC}"
    exit 1
fi

# Create .env from example if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}📝 Creating .env from .env.example...${NC}"
    cp .env.example .env
fi

# Detect NVIDIA GPU
GPU_AVAILABLE=false
if command -v nvidia-smi &> /dev/null; then
    if nvidia-smi &> /dev/null; then
        GPU_AVAILABLE=true
        GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)
        GPU_MEMORY=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader | head -1)
        echo -e "${GREEN}✅ NVIDIA GPU detected: ${GPU_NAME} (${GPU_MEMORY})${NC}"
    fi
fi

if [ "$GPU_AVAILABLE" = false ]; then
    echo -e "${YELLOW}ℹ️  No NVIDIA GPU detected. CPU mode will be used.${NC}"
fi

# Mode selection
echo ""
echo -e "${BLUE}Select deployment mode:${NC}"
echo ""

if [ "$GPU_AVAILABLE" = true ]; then
    echo "  1) 🚀 GPU Mode (Auralis TTS - Premium 48kHz quality)"
    echo "  2) 💻 CPU Mode (Kokoro TTS - Good 24kHz quality)"
    echo ""
    read -p "Enter choice [1-2, default=1]: " MODE_CHOICE
    MODE_CHOICE=${MODE_CHOICE:-1}
else
    echo "  1) 💻 CPU Mode (Kokoro TTS - Only option without GPU)"
    echo ""
    MODE_CHOICE=1
    echo -e "${YELLOW}Automatically selecting CPU mode...${NC}"
fi

# Set compose files based on choice
if [ "$MODE_CHOICE" = "1" ] && [ "$GPU_AVAILABLE" = true ]; then
    echo ""
    echo -e "${GREEN}🚀 Starting in GPU mode with Auralis TTS...${NC}"
    COMPOSE_CMD="docker compose -f docker-compose.yml -f docker-compose.gpu.yml"
    # Update .env for GPU mode
    sed -i 's/TTS_MODE=.*/TTS_MODE=gpu/' .env 2>/dev/null || true
else
    echo ""
    echo -e "${BLUE}💻 Starting in CPU mode with Kokoro TTS...${NC}"
    COMPOSE_CMD="docker compose"
    # Update .env for CPU mode
    sed -i 's/TTS_MODE=.*/TTS_MODE=cpu/' .env 2>/dev/null || true
fi

echo ""
echo -e "${YELLOW}📦 Pulling and building images (this may take a while on first run)...${NC}"
echo ""

# Pull/build and start
$COMPOSE_CMD pull --ignore-pull-failures 2>/dev/null || true
$COMPOSE_CMD up --build -d

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Realtime Translator is starting!${NC}"
echo ""
echo -e "   🌐 Web Interface:  ${CYAN}http://localhost:3000${NC}"
echo -e "   📡 LiveKit:        ${CYAN}ws://localhost:7880${NC}"
echo ""
echo -e "${YELLOW}   ⏳ First startup downloads models (~10-20GB). Please wait...${NC}"
echo ""
echo -e "   View logs:         ${BLUE}docker compose logs -f${NC}"
echo -e "   Stop services:     ${BLUE}docker compose down${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
