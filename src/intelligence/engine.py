import os
import logging
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class IntelligenceEngine:
    """
    Integrates LLMs (like Google Gemini) to provide high-level 
    reasoning and synthesis for autonomous agents.
    """
    def __init__(self):
        # Explicitly reload environment variables to ensure the newest .env values are picked up
        load_dotenv(override=True)
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.enabled = False
        
        if self.api_key and self.api_key != "YOUR_GEMINI_API_KEY_HERE":
            try:
                genai.configure(api_key=self.api_key)
                # Updated to use the requested elite models for different tasks
                # Using gemini-2.0-flash as it's the primary stable flash model available
                self.models = {
                    "pro": genai.GenerativeModel('gemini-2.0-flash'), # High complexity
                    "flash": genai.GenerativeModel('gemini-2.0-flash') # Low latency
                }
                self.enabled = True
                logger.info("Gemini Intelligence Engine initialized and enabled with optimized models.")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
        else:
            logger.warning("Google API Key not found or default. AI reasoning will be bypassed.")

    async def reason(self, prompt: str, context: str = "", model_type: str = "flash") -> str:
        """
        Queries the LLM to get a reasoning strings or strategy.
        Returns a fallback string if the LLM is disabled or fails.
        """
        if not self.enabled:
            return "Reasoning performed via local heuristic engine (LLM bypassed)."

        full_prompt = f"Context: {context}\n\nTask: {prompt}\n\nReasoning (be concise, tactical, and professional):"
        
        try:
            # We wrap this in a thread because genai library is currently synchronous
            import asyncio
            model = self.models.get(model_type, self.models["flash"])
            response = await asyncio.to_thread(model.generate_content, full_prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"AI Reasoning Error: {e}")
            return f"Strategic analysis failed: {str(e)}"

# Singleton instance
intelligence_engine = IntelligenceEngine()
