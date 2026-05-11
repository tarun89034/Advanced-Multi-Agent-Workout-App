import os
import json
import asyncio
from typing import Optional
from dotenv import load_dotenv
import httpx
from langflow.load import run_flow_from_json
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


def ask_ai(profile, question):
    logger.info(f"Asking AI a question: {question[:50]}...")
    TWEAKS = {
        "TextInput-XjIKI": {
            "input_value": question
        },
        "TextInput-176Ns": {
            "input_value": dict_to_string(profile)
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
        logger.success("Successfully generated AI response locally.")
        return output_text
    except Exception as e:
        logger.error(f"Error in ask_ai: {e}")
        return f"Error: {e}"


def _run_async(coro):
    """Run an async coroutine from synchronous code safely, even inside
    an existing event loop (e.g. Streamlit). Spins up a dedicated thread
    with its own event loop so we never conflict with the host loop."""
    import concurrent.futures
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(asyncio.run, coro)
        return future.result()


def get_macros(profile, goals):
    logger.info("Requesting macro generation from AI...")
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
        logger.error(f"Error in get_macros: {e}")
        return {"error": "Failed to fetch macros"}


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

