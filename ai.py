import os
import json
import asyncio
from typing import Optional
from dotenv import load_dotenv
import httpx
from loguru import logger

from observability import init_observability, get_tracer

load_dotenv()

init_observability("ai-workflow-app")
tracer = get_tracer()

BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "34c16f5c-70e4-4bb6-9c51-89a41a653efd"
APPLICATION_TOKEN = os.getenv("LANGFLOW_TOKEN")

logger.add("logs/ai_workflow.log", rotation="10 MB", retention="10 days", level="INFO")


def dict_to_string(obj, level=0):
    strings = []
    indent = "  " * level  # Indentation for nested levels

    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, (dict, list)):
                nested_string = dict_to_string(value, level + 1)
                strings.append(f"{indent}{key}: {nested_string}")
            else:
                strings.append(f"{indent}{key}: {value}")
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            nested_string = dict_to_string(item, level + 1)
            strings.append(f"{indent}Item {idx + 1}: {nested_string}")
    else:
        strings.append(f"{indent}{obj}")

    return ", ".join(strings)


def _try_langflow_import():
    """Attempt to import langflow's run_flow_from_json. Returns None if unavailable."""
    try:
        from langflow.load import run_flow_from_json
        return run_flow_from_json
    except ImportError:
        logger.warning("langflow not installed. Local flow execution unavailable.")
        return None
    except Exception as e:
        logger.warning(f"langflow import failed: {e}. Local flow execution unavailable.")
        return None


def _ask_ai_via_openrouter(profile, question):
    """Fallback: call OpenRouter directly when Langflow is unavailable."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return "Error: No OPENROUTER_API_KEY configured. Please set it in your .env file."

    profile_str = dict_to_string(profile)
    system_prompt = (
        "You are an expert AI fitness coach. You provide personalized workout, "
        "nutrition, and health advice based on the user's profile data.\n\n"
        f"User Profile:\n{profile_str}"
    )

    models = ["z-ai/glm-4.5-air:free", "deepseek/deepseek-chat", "openai/gpt-4o-mini"]

    for model in models:
        try:
            logger.info(f"Attempting AI query via OpenRouter with model: {model}")
            response = httpx.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": question},
                    ],
                },
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            logger.success(f"Successfully generated AI response via OpenRouter ({model}).")
            return content
        except Exception as e:
            logger.error(f"OpenRouter model {model} failed: {e}")
            continue

    return "Error: All AI models failed. Please try again later."


def ask_ai(profile, question):
    logger.info(f"Asking AI a question: {question[:50]}...")

    run_flow_from_json = _try_langflow_import()

    if run_flow_from_json:
        TWEAKS = {
            "TextInput-XjIKI": {
                "input_value": question
            },
            "TextInput-176Ns": {
                "input_value": dict_to_string(profile)
            },
            "AstraDB-0mf3v": {
                "api_endpoint": os.getenv("ASTRA_ENDPOINT"),
                "token": os.getenv("ASTRA_DB_APPLICATION_TOKEN"),
            },
        }

        try:
            if tracer:
                with tracer.start_as_current_span("run_flow_local"):
                    result = run_flow_from_json(flow="flows/AskAIV2.json",
                                                input_value="message",
                                                fallback_to_env_vars=True,
                                                tweaks=TWEAKS)
            else:
                result = run_flow_from_json(flow="flows/AskAIV2.json",
                                            input_value="message",
                                            fallback_to_env_vars=True,
                                            tweaks=TWEAKS)

            output_text = result[0].outputs[0].results["text"].data["text"]
            logger.success("Successfully generated AI response via Langflow.")
            return output_text
        except Exception as e:
            logger.warning(f"Langflow flow failed: {e}. Falling back to direct OpenRouter call.")

    # Fallback to direct OpenRouter API
    return _ask_ai_via_openrouter(profile, question)


def _get_macros_via_openrouter(profile, goals):
    """Fallback: generate macros via OpenRouter directly."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return {"error": "No OPENROUTER_API_KEY configured. Please set it in your .env file."}

    profile_str = dict_to_string(profile)
    goals_str = ", ".join(goals) if goals else "General fitness"

    prompt = (
        "You are a nutrition expert. Based on the following user profile and goals, "
        "generate daily macro targets. Respond ONLY with a valid JSON object with exactly "
        'these keys: "calories" (integer), "protein" (integer grams), "fat" (integer grams), '
        '"carbs" (integer grams). No explanation, no markdown, just the JSON object.\n\n'
        f"User Profile:\n{profile_str}\n\n"
        f"Goals: {goals_str}"
    )

    models = ["z-ai/glm-4.5-air:free", "deepseek/deepseek-chat", "openai/gpt-4o-mini"]

    for model in models:
        try:
            logger.info(f"Attempting macro generation via OpenRouter with model: {model}")
            response = httpx.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]

            # Try to extract JSON from the response
            content = content.strip()
            if content.startswith("```"):
                # Strip markdown code fences
                lines = content.split("\n")
                content = "\n".join(
                    line for line in lines
                    if not line.strip().startswith("```")
                )

            macros = json.loads(content.strip())
            # Validate expected keys
            for key in ("calories", "protein", "fat", "carbs"):
                macros[key] = int(macros[key])

            logger.success(f"Successfully generated macros via OpenRouter ({model}).")
            return macros
        except Exception as e:
            logger.error(f"OpenRouter macro generation with {model} failed: {e}")
            continue

    return {"error": "Failed to generate macros. Please try again later."}


def get_macros(profile, goals):
    logger.info("Requesting macro generation from AI...")

    run_flow_from_json = _try_langflow_import()

    if run_flow_from_json:
        tweaks = {
            "TextInput-PR5Jb": {
                "input_value": ", ".join(goals)
            },
            "TextInput-PrfY9": {
                "input_value": dict_to_string(profile)
            }
        }

        try:
            result = run_flow_from_json(
                flow="flows/Macro Flow.json",
                input_value="message",
                fallback_to_env_vars=True,
                tweaks=tweaks,
            )
            output_text = result[0].outputs[0].results["text"].data["text"]
            return json.loads(output_text)
        except Exception as e:
            logger.warning(f"Langflow macro flow failed: {e}. Falling back to OpenRouter.")

    # Fallback to direct OpenRouter API
    return _get_macros_via_openrouter(profile, goals)


def _run_async(coro):
    """Run an async coroutine from synchronous code safely, even inside
    an existing event loop (e.g. Streamlit). Spins up a dedicated thread
    with its own event loop so we never conflict with the host loop."""
    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(asyncio.run, coro)
        return future.result()


async def run_flow_async(message: str,
  output_type: str = "chat",
  input_type: str = "chat",
  tweaks: Optional[dict] = None,
  application_token: Optional[str] = None) -> dict:

    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/macros"

    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
    }
    headers = {}
    if tweaks:
        payload["tweaks"] = tweaks
    if application_token:
        headers = {
            "Authorization": "Bearer " + application_token,
            "Content-Type": "application/json"
        }

    try:
        logger.debug(f"Sending async request to Langflow API: {api_url}")
        async with httpx.AsyncClient(timeout=60.0) as client:
            if tracer:
                with tracer.start_as_current_span("run_flow_api"):
                    response = await client.post(api_url, json=payload, headers=headers)
            else:
                response = await client.post(api_url, json=payload, headers=headers)

            response.raise_for_status()
            logger.success("Successfully retrieved macros from API")

            data = response.json()
            return json.loads(data["outputs"][0]["outputs"][0]["results"]["text"]["data"]["text"])
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
        return {"error": "Failed to fetch macros"}
    except Exception as e:
        logger.exception(f"An unexpected error occurred during async flow execution: {e}")
        return {"error": str(e)}
