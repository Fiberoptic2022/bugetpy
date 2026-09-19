"""Client for calling Claude (Anthropic API).

Configure via environment variable or an `env.ini` [ANTHROPIC] section:

    [ANTHROPIC]
    API_KEY = sk-ant-...

ANTHROPIC_API_KEY env var takes precedence over env.ini when set.
"""

import configparser
import os

import anthropic

DEFAULT_MODEL = "claude-sonnet-5"


def _load_config():
    config = configparser.ConfigParser()
    config.read("env.ini")
    return config


def get_api_key():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        config = _load_config()
        if config.has_option("ANTHROPIC", "API_KEY"):
            api_key = config["ANTHROPIC"]["API_KEY"]
    if not api_key:
        raise RuntimeError(
            "Anthropic API key not configured. Set the ANTHROPIC_API_KEY "
            "environment variable or [ANTHROPIC] API_KEY in env.ini."
        )
    return api_key


def generate_response(prompt, model=DEFAULT_MODEL, messages=None, max_tokens=1024):
    """Send a message to Claude and return the reply text."""
    client = anthropic.Anthropic(api_key=get_api_key())
    payload_messages = messages or [{"role": "user", "content": prompt}]

    try:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=payload_messages,
        )
        return "".join(block.text for block in response.content if block.type == "text")
    except anthropic.APIError as e:
        print(f"An error occurred while calling Claude: {e}")
        return None
