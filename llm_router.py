"""Unified interface over the local/self-hosted model (Open WebUI) and Claude.

    from llm_router import generate_response

    generate_response("Summarize my spending this month.", provider="claude")
    generate_response("Summarize my spending this month.", provider="open_webui")

Falls back from Claude to Open WebUI (or vice versa) on request, so a single
call site can degrade gracefully if one provider is unavailable.
"""

import anthropic_client
import open_webui_client

DEFAULT_OPEN_WEBUI_MODEL = "llama3.1"


def generate_response(prompt, provider="claude", model=None, fallback=None):
    """Generate a response from the given provider.

    provider: "claude" or "open_webui"
    fallback: optional provider name to try if the primary call fails/errors.
    """
    if provider == "claude":
        result = anthropic_client.generate_response(prompt, model=model or anthropic_client.DEFAULT_MODEL)
    elif provider == "open_webui":
        result = open_webui_client.generate_response(model or DEFAULT_OPEN_WEBUI_MODEL, prompt)
    else:
        raise ValueError(f"Unknown provider: {provider!r}. Use 'claude' or 'open_webui'.")

    if result is None and fallback:
        print(f"Provider '{provider}' failed, falling back to '{fallback}'.")
        # model names aren't portable across providers (e.g. "llama3.1" isn't
        # a Claude model), so let the fallback provider use its own default.
        return generate_response(prompt, provider=fallback)

    return result
