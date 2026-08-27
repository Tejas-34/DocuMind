import logging
from typing import AsyncGenerator
from src.core.config import settings
from src.services.rag_service import STRICT_REFERENCE_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize google-genai client: {e}")

    async def stream_response(
        self,
        prompt: str,
        system_instruction: str = STRICT_REFERENCE_SYSTEM_PROMPT
    ) -> AsyncGenerator[str, None]:
        if not self.client or not self.api_key:
            # Fallback for dev/offline testing if no API key provided
            logger.warning("GEMINI_API_KEY not configured. Yielding local reference response.")
            fallback_text = "I cannot find this information in your uploaded documents. Please configure a valid GEMINI_API_KEY to enable full AI responses."
            for word in fallback_text.split():
                yield word + " "
            return

        try:
            from google.genai import types
            response_stream = await self.client.aio.models.generate_content_stream(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    system_instruction=system_instruction,
                )
            )
            async for chunk in response_stream:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.exception(f"Gemini API streaming error: {e}")
            yield f"\n[Error generating response: {str(e)}]"
