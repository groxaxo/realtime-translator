"""
Realtime Translator Agent

A LiveKit agent that provides bidirectional English ↔ Spanish voice translation.
Uses Parakeet TDT for STT, LLM for translation, and Auralis/Kokoro for TTS.
"""

import logging
import os

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
)
from livekit.plugins import silero, openai

logger = logging.getLogger("translator-agent")

load_dotenv(".env.local")


# =============================================================================
# AGENT CONFIGURATION
# =============================================================================

TRANSLATOR_INSTRUCTIONS = """You are a real-time voice translator. Your ONLY job is to translate speech between English and Spanish.

CRITICAL RULES:
1. When you receive English text, translate it to Spanish
2. When you receive Spanish text, translate it to English  
3. ONLY output the translation - nothing else
4. Do NOT add explanations, greetings, or commentary
5. Preserve the tone and meaning of the original speech
6. Keep translations natural and conversational
7. If the input is a greeting like "hello" or "hola", just translate it - do not engage in conversation

Examples:
- Input: "Hello, how are you?" → Output: "Hola, ¿cómo estás?"
- Input: "Buenos días" → Output: "Good morning"
- Input: "Where is the restaurant?" → Output: "¿Dónde está el restaurante?"

You are invisible - the speakers should feel like they understand each other directly."""


class TranslatorAgent(Agent):
    """Voice translation agent for English ↔ Spanish communication."""

    def __init__(self) -> None:
        super().__init__(instructions=TRANSLATOR_INSTRUCTIONS)

    async def on_enter(self):
        """Called when a participant joins the room - brief greeting to verify WebRTC works."""
        logger.info(f"=== PARTICIPANT JOINED ===")
        await self.session.say(
            "Translator ready. Speak in English or Spanish.",
            allow_interruptions=True,
        )
        logger.info(f"=== GREETING SENT ===")


# =============================================================================
# AGENT SERVER SETUP
# =============================================================================


def prewarm(proc: JobProcess):
    """Prewarm the agent process with VAD model."""
    proc.userdata["vad"] = silero.VAD.load()


def get_tts_client() -> openai.TTS:
    """Get TTS client based on TTS_MODE environment variable."""
    tts_mode = os.getenv("TTS_MODE", "cpu").lower()

    if tts_mode == "gpu":
        # Auralis TTS (GPU mode - premium quality)
        base_url = os.getenv("AURALIS_BASE_URL", "http://auralis:9950/v1")
        logger.info(f"Using Auralis TTS (GPU mode) at {base_url}")
        return openai.TTS(
            base_url=base_url, model="auralis", voice="default", api_key="no-key-needed"
        )
    else:
        # Kokoro TTS (CPU mode - fallback)
        base_url = os.getenv("KOKORO_BASE_URL", "http://kokoro:8880/v1")
        logger.info(f"Using Kokoro TTS (CPU mode) at {base_url}")
        return openai.TTS(
            base_url=base_url, model="kokoro", voice="af_nova", api_key="no-key-needed"
        )


async def entrypoint(ctx: JobContext):
    """Main translation session handler."""

    # Get configuration from environment
    parakeet_url = os.getenv("PARAKEET_BASE_URL", "http://parakeet:5092/v1")
    llama_url = os.getenv("LLAMA_BASE_URL", "http://llama_cpp:11434/v1")
    llama_model = os.getenv("LLAMA_MODEL", "qwen3-4b")

    logger.info(f"Parakeet STT: {parakeet_url}")
    logger.info(f"LLaMA Translation: {llama_url} ({llama_model})")

    logger.info(f"=== JOB RECEIVED ===")
    logger.info(f"Job ID: {ctx.job.id}")
    logger.info(f"Room Name: {ctx.room.name}")
    agent_name = getattr(ctx.job, "agent_name", None)
    logger.info(f"Agent Name: {agent_name or 'translator'}")

    await ctx.connect()

    logger.info(f"=== CONNECTED TO ROOM ===")
    logger.info(f"Room: {ctx.room.name}")

    # Initialize LLM client for translation
    llm_client = openai.LLM(base_url=llama_url, model=llama_model, api_key="no-key-needed")

    # Create agent session
    session = AgentSession(
        stt=openai.STT(
            base_url=parakeet_url, model="parakeet-tdt-0.6b-v3", api_key="no-key-needed"
        ),
        llm=llm_client,
        tts=get_tts_client(),
        vad=ctx.proc.userdata["vad"],
    )

    logger.info(f"=== STARTING AGENT SESSION ===")

    # Start the session with our translator agent
    await session.start(
        agent=TranslatorAgent(),
        room=ctx.room,
    )

    logger.info(f"=== AGENT SESSION STARTED ===")


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
            agent_name="translator",
        )
    )
