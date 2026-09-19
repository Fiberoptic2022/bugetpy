"""Client for talking to a self-hosted Open WebUI instance (e.g. http://192.168.30.22:3000).

Open WebUI exposes an OpenAI-compatible chat completions endpoint that proxies
whatever model backend it's configured with (Ollama, etc). Configure the
connection via environment variables or an `env.ini` [OPEN_WEBUI] section:

    [OPEN_WEBUI]
    BASE_URL = http://192.168.30.22:3000
    API_KEY = <generated in Open WebUI under Settings > Account > API Keys>

Environment variables OPEN_WEBUI_BASE_URL / OPEN_WEBUI_API_KEY take precedence
over env.ini when set.
"""

import configparser
import os

import requests


def _load_config():
    config = configparser.ConfigParser()
    config.read("env.ini")
    return config


def get_client_settings():
    config = _load_config()
    base_url = os.environ.get("OPEN_WEBUI_BASE_URL")
    api_key = os.environ.get("OPEN_WEBUI_API_KEY")

    if not base_url and config.has_option("OPEN_WEBUI", "BASE_URL"):
        base_url = config["OPEN_WEBUI"]["BASE_URL"]
    if not api_key and config.has_option("OPEN_WEBUI", "API_KEY"):
        api_key = config["OPEN_WEBUI"]["API_KEY"]

    if not base_url:
        raise RuntimeError(
            "Open WebUI base URL not configured. Set the OPEN_WEBUI_BASE_URL "
            "environment variable or [OPEN_WEBUI] BASE_URL in env.ini."
        )
    if not api_key:
        raise RuntimeError(
            "Open WebUI API key not configured. Set the OPEN_WEBUI_API_KEY "
            "environment variable or [OPEN_WEBUI] API_KEY in env.ini "
            "(generate one in Open WebUI under Settings > Account > API Keys)."
        )

    return base_url.rstrip("/"), api_key


def generate_response(model, prompt, messages=None, timeout=120, connect_timeout=5):
    """Send a chat completion request to Open WebUI and return the reply text.

    connect_timeout bounds how long we wait to establish the connection (fails
    fast if the host is unreachable); timeout bounds how long we wait for the
    model to finish generating once connected (can legitimately be slow).
    """
    base_url, api_key = get_client_settings()
    payload_messages = messages or [{"role": "user", "content": prompt}]

    try:
        response = requests.post(
            f"{base_url}/api/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={"model": model, "messages": payload_messages},
            timeout=(connect_timeout, timeout),
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while calling Open WebUI: {e}")
        return None
