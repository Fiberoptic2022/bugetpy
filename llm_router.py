"""Unified interface over the local/self-hosted model (Open WebUI) and Claude.

    from llm_router import generate_response, collaborate

    generate_response("Summarize my spending this month.", provider="claude")
    generate_response("Summarize my spending this month.", provider="open_webui")

    # Have the two providers actually work together: one drafts, the other
    # reviews and refines that draft into the final answer.
    collaborate("Summarize my spending this month.", lead="open_webui")

`generate_response` also falls back from one provider to the other on
request, so a single call site can degrade gracefully if one is unavailable.
"""

import anthropic_client
import open_webui_client


def generate_response(prompt, provider="claude", model=None, fallback=None):
    """Generate a response from the given provider.

    provider: "claude" or "open_webui"
    fallback: optional provider name to try if the primary call fails/errors.
    """
    if provider == "claude":
        result = anthropic_client.generate_response(prompt, model=model or anthropic_client.DEFAULT_MODEL)
    elif provider == "open_webui":
        result = open_webui_client.generate_response(model or open_webui_client.get_default_model(), prompt)
    else:
        raise ValueError(f"Unknown provider: {provider!r}. Use 'claude' or 'open_webui'.")

    if result is None and fallback:
        print(f"Provider '{provider}' failed, falling back to '{fallback}'.")
        # model names aren't portable across providers (e.g. "llama3.1" isn't
        # a Claude model), so let the fallback provider use its own default.
        return generate_response(prompt, provider=fallback)

    return result


def collaborate(prompt, lead="open_webui", model=None):
    """Get a draft answer from `lead`, then have the other provider review it.

    This is real two-way use, not just failover: the second provider sees
    the first provider's actual answer and is asked to correct, fill gaps
    in, or improve it. Returns the reviewer's final answer, plus the lead's
    original draft for reference.

    lead: "open_webui" or "claude" - which provider drafts first.
    Returns a dict: {"draft": <lead's answer>, "draft_provider": lead,
                      "final": <reviewer's answer>, "final_provider": <reviewer>}
    """
    other = "claude" if lead == "open_webui" else "open_webui"

    draft = generate_response(prompt, provider=lead, model=model, fallback=other)
    if draft is None:
        return {"draft": None, "draft_provider": lead, "final": None, "final_provider": None}

    review_prompt = (
        f'Another AI model was asked: "{prompt}"\n\n'
        f"It answered:\n{draft}\n\n"
        "Review that answer: correct any mistakes, fill in anything important "
        "it missed, and tighten it up. Give the improved final answer only."
    )
    final = generate_response(review_prompt, provider=other, fallback=lead)

    return {"draft": draft, "draft_provider": lead, "final": final, "final_provider": other}
