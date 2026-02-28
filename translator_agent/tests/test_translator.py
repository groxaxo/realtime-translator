import asyncio
from types import SimpleNamespace

from src.translator import TranslationService, detect_language


def test_detect_language_uses_word_frequency_not_unique_words():
    assert detect_language("hello hello hello hello hola") == "en"


def test_detect_language_spanish_with_indicators():
    assert detect_language("hola gracias por venir") == "es"


def test_translate_handles_empty_llm_content():
    class DummyLLM:
        async def chat(self, messages):
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content=None))]
            )

    service = TranslationService(DummyLLM())
    result = asyncio.run(service.translate("hello", "en", "es"))
    assert result == ""
