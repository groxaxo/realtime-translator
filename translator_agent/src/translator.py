"""
Translation utilities for the Realtime Translator.

Provides language detection and translation services.
"""

import re
from typing import Literal

# Common Spanish words and patterns for language detection
SPANISH_INDICATORS = {
    # Common words
    "el", "la", "los", "las", "un", "una", "unos", "unas",
    "de", "del", "al", "en", "con", "por", "para", "sin",
    "que", "qué", "como", "cómo", "donde", "dónde", "cuando", "cuándo",
    "es", "está", "son", "están", "ser", "estar", "hay",
    "yo", "tú", "él", "ella", "nosotros", "ellos", "ellas",
    "mi", "tu", "su", "nuestro", "vuestro",
    "hola", "gracias", "buenos", "buenas", "días", "noches",
    "sí", "no", "también", "pero", "porque", "aunque",
    "muy", "más", "menos", "mucho", "poco",
    "hacer", "tener", "poder", "querer", "saber", "ir", "venir",
    "hoy", "mañana", "ayer", "ahora", "después", "antes",
}

# Spanish character patterns
SPANISH_CHARS = set("áéíóúüñ¿¡")


def detect_language(text: str) -> Literal["en", "es"]:
    """Detect whether text is English or Spanish.
    
    Uses a simple heuristic based on common words and Spanish-specific characters.
    
    Args:
        text: Input text to analyze
        
    Returns:
        'en' for English, 'es' for Spanish
    """
    text_lower = text.lower()
    words = re.findall(r"\b\w+\b", text_lower)
    
    # Check for Spanish-specific characters
    if any(char in text_lower for char in SPANISH_CHARS):
        return "es"
    
    # Check for Spanish words
    spanish_word_count = sum(1 for word in words if word in SPANISH_INDICATORS)
    spanish_ratio = spanish_word_count / max(len(words), 1)
    
    # If more than 20% of words are Spanish indicators, classify as Spanish
    if spanish_ratio > 0.2:
        return "es"
    
    return "en"


def format_for_tts(text: str, language: str) -> str:
    """Format translated text for TTS output.
    
    Cleans up the text and prepares it for natural speech synthesis.
    
    Args:
        text: Translated text
        language: Target language code
        
    Returns:
        Cleaned text ready for TTS
    """
    # Remove any markdown or formatting
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'_+', '', text)
    text = re.sub(r'`+', '', text)
    
    # Remove quotes that the LLM might add
    text = text.strip('"\'')
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    return text


class TranslationService:
    """Async translation service using LLM."""
    
    def __init__(self, llm_client):
        """Initialize with an LLM client.
        
        Args:
            llm_client: OpenAI-compatible LLM client
        """
        self.llm = llm_client
        self._system_prompt = """You are a professional translator specializing in English-Spanish translation.
Your translations are natural, conversational, and preserve the original meaning and tone.
You ONLY output the translation - no explanations, no commentary, no quotes around the text."""
    
    async def translate(
        self, 
        text: str, 
        source_lang: Literal["en", "es"], 
        target_lang: Literal["en", "es"]
    ) -> str:
        """Translate text between English and Spanish.
        
        Args:
            text: Text to translate
            source_lang: Source language ('en' or 'es')
            target_lang: Target language ('en' or 'es')
            
        Returns:
            Translated text
        """
        if source_lang == target_lang:
            return text
            
        lang_names = {"en": "English", "es": "Spanish"}
        
        user_prompt = f"""Translate this {lang_names[source_lang]} text to {lang_names[target_lang]}:

{text}"""

        response = await self.llm.chat(
            messages=[
                {"role": "system", "content": self._system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        translated = (response.choices[0].message.content or "").strip()
        return format_for_tts(translated, target_lang)
