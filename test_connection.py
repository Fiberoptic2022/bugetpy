"""Standalone connectivity check for the configured Open WebUI server.

Run this locally (on a machine that can actually reach the server, e.g. the
same LAN as 192.168.30.22) before running private_agent.py, to confirm the
host is reachable and the API key is valid:

    python test_connection.py
"""

import sys

import requests

from open_webui_client import get_client_settings


def main():
    try:
        base_url, api_key = get_client_settings()
    except RuntimeError as e:
        print(f"Config error: {e}")
        sys.exit(1)

    print(f"Checking {base_url} ...")

    # 1. Basic reachability, no auth required.
    try:
        health = requests.get(f"{base_url}/health", timeout=10)
        print(f"  /health -> HTTP {health.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"  /health -> FAILED: {e}")
        print("  Could not reach the server at all. Check the host/port, "
              "that Open WebUI is running, and that this machine is on the "
              "same network (or has VPN/port-forward access).")
        sys.exit(1)

    # 2. Authenticated call, confirms the API key works.
    try:
        models = requests.get(
            f"{base_url}/api/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10,
        )
        if models.status_code == 200:
            names = [m.get("id") or m.get("name") for m in models.json().get("data", [])]
            print(f"  /api/models -> HTTP 200, {len(names)} model(s) available: {names}")
            print("Connection OK.")
        elif models.status_code == 401:
            print("  /api/models -> HTTP 401 Unauthorized. Check OPEN_WEBUI API_KEY.")
            sys.exit(1)
        else:
            print(f"  /api/models -> HTTP {models.status_code}: {models.text[:200]}")
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"  /api/models -> FAILED: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
