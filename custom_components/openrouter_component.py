from typing import Any, Dict, List
import os
import httpx
import json
import time
import asyncio
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langflow.custom import Component
from langflow.io import MessageTextInput, Output, BoolInput, IntInput, DictInput, DropdownInput, SecretStrInput
from langflow.schema import Data
from loguru import logger

# Cache for OpenRouter models
_MODEL_CACHE: Dict[str, Any] = {"models": [], "timestamp": 0}
CACHE_TTL = 300  # 5 minutes

class OpenRouterComponent(Component):
    display_name = "OpenRouter Model"
    description = "Production-grade OpenRouter integration with fallback routing and high availability."
    icon = "OpenRouter"
    name = "OpenRouterComponent"
    
    inputs = [
        MessageTextInput(
            name="input_message",
            display_name="Input Message",
            info="The message to send to the model.",
        ),
        SecretStrInput(
            name="openrouter_api_key",
            display_name="OpenRouter API Key",
            info="Your OpenRouter API Key. If empty, falls back to OPENROUTER_API_KEY environment variable.",
        ),
        DropdownInput(
            name="primary_model",
            display_name="Primary Model",
            options=["z-ai/glm-4.5-air:free", "deepseek/deepseek-chat", "openai/gpt-oss-120b:free", "anthropic/claude-3-haiku"],
            value="z-ai/glm-4.5-air:free",
            info="Primary model for inference.",
        ),
        BoolInput(
            name="enable_fallbacks",
            display_name="Enable Fallbacks",
            value=True,
            info="If primary model fails, automatically route to fallback models.",
        ),
        BoolInput(
            name="streaming",
            display_name="Streaming",
            value=True,
            advanced=True,
            info="Enable token streaming for reduced perceived latency.",
        ),
        IntInput(
            name="timeout",
            display_name="Timeout (s)",
            value=60,
            advanced=True,
            info="Request timeout in seconds.",
        ),
        IntInput(
            name="max_retries",
            display_name="Max Retries",
            value=3,
            advanced=True,
            info="Number of retries before failing or falling back.",
        ),
        DictInput(
            name="model_kwargs",
            display_name="Model Kwargs",
            advanced=True,
            info="Additional model parameters like top_p, temperature, etc.",
        ),
    ]

    outputs = [
        Output(display_name="Output Message", name="output_message", method="run_model"),
        Output(display_name="Language Model", name="model_output", method="build_model"),
    ]

    def _run_async(self, coro):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(asyncio.run, coro)
                return future.result()

        return asyncio.run(coro)

    def _get_api_key(self) -> str:
        key = self.openrouter_api_key or os.getenv("OPENROUTER_API_KEY")
        if not key:
            raise ValueError("OpenRouter API Key is missing. Please set it in the component or via environment variables.")
        return key

    def fetch_models(self) -> List[str]:
        """Fetch models from OpenRouter with caching to reduce API load."""
        global _MODEL_CACHE
        current_time = time.time()
        
        if _MODEL_CACHE["models"] and (current_time - _MODEL_CACHE["timestamp"] < CACHE_TTL):
            logger.debug("Using cached OpenRouter models")
            return _MODEL_CACHE["models"]

        async def _fetch_models_async() -> List[str]:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("https://openrouter.ai/api/v1/models")
                response.raise_for_status()
                data = response.json()
                return [model["id"] for model in data.get("data", [])]

        try:
            logger.info("Fetching OpenRouter models")
            models = self._run_async(_fetch_models_async())
            _MODEL_CACHE["models"] = models
            _MODEL_CACHE["timestamp"] = current_time
            return models
        except Exception as e:
            logger.warning(f"Failed to fetch models: {e}. Using default options.")
            return ["z-ai/glm-4.5-air:free", "deepseek/deepseek-chat", "openai/gpt-4o-mini"]

    def _create_model_instance(self, model_name: str) -> ChatOpenAI:
        if model_name.startswith("gemini-"):
            gemini_key = os.getenv("GEMINI_API_KEY")
            if not gemini_key:
                raise ValueError("Gemini API Key is missing. Please set GEMINI_API_KEY in the environment.")

            kwargs = {
                "model": model_name,
                "google_api_key": gemini_key,
                "streaming": self.streaming,
            }
            if self.model_kwargs:
                kwargs["model_kwargs"] = self.model_kwargs

            try:
                return ChatGoogleGenerativeAI(**kwargs)
            except Exception as e:
                raise ValueError(f"Gemini model error: {str(e)}")

        kwargs = {
            "model": model_name,
            "api_key": self._get_api_key(),
            "base_url": "https://openrouter.ai/api/v1",
            "max_retries": self.max_retries,
            "request_timeout": self.timeout,
            "streaming": self.streaming,
        }
        
        if self.model_kwargs:
            kwargs["model_kwargs"] = self.model_kwargs

        try:
            # We use ChatOpenAI from langchain-openai as OpenRouter is OpenAI compatible
            return ChatOpenAI(**kwargs)
        except Exception as e:
            raise ValueError(f"OpenRouter model error: {str(e)}")

    def build_model(self) -> ChatOpenAI:
        return self._create_model_instance(self.primary_model)

    def model_output(self) -> ChatOpenAI:
        return self.build_model()

    def run_model(self) -> Data:
        fallback_chain = [
            self.primary_model,
            "openai/gpt-oss-120b:free",
            "gemini-1.5-flash"
        ] if self.enable_fallbacks else [self.primary_model]

        last_error = None
        for model_name in fallback_chain:
            try:
                logger.info(f"Attempting inference with OpenRouter model: {model_name}")
                llm = self._create_model_instance(model_name)
                
                # In Langflow Custom Components, returning a string or Data is standard
                response = llm.invoke(self.input_message)
                
                # Check for rate limits or other OpenRouter specific errors that Langchain might not catch immediately
                if "error" in str(response.content).lower() and "rate limit" in str(response.content).lower():
                    raise Exception("Rate limit exceeded")
                    
                logger.success(f"Successfully generated response using {model_name}")
                return Data(text=response.content, source_model=model_name)
                
            except Exception as e:
                logger.error(f"Inference failed for {model_name}: {str(e)}")
                last_error = e
                continue
                
        raise ValueError(f"All fallback models failed. Last error: {str(last_error)}")
