import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
from typing import Any, Tuple, List, Dict, Union

import streamlit as st


def get_api_base_url() -> str:
    """Fetch the API base URL from Streamlit secrets or environment variables."""
    secret_base_url = None
    if hasattr(st, "secrets"):
        try:
            secret_base_url = st.secrets.get("MODULE44_API_BASE_URL")
        except Exception:
            secret_base_url = None

    base_url = secret_base_url or os.getenv("MODULE44_API_BASE_URL", "http://127.0.0.1:8000")
    return base_url.rstrip("/")


@st.cache_data(ttl=30)
def fetch_json(path: str) -> Tuple[Union[List[Dict[str, Any]], Dict[str, Any], None], Union[str, None]]:
    """Fetch JSON data from the backend API, with basic error handling."""
    url = f"{get_api_base_url()}{path}"
    try:
        with urlopen(url, timeout=6) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return payload, None
    except HTTPError as exc:
        try:
            detail = exc.read().decode("utf-8")
        except Exception:
            detail = str(exc)
        return None, f"{exc.code}: {detail}"
    except URLError as exc:
        return None, f"Backend unreachable at {get_api_base_url()} ({exc.reason})"
    except Exception as exc:
        return None, str(exc)


def get_overview_stats() -> Tuple[Dict[str, str], Union[str, None]]:
    """Fetch overview statistics for the Module 44 Dashboard."""
    rules, err_rules = fetch_json("/rules/")
    patterns, err_patterns = fetch_json("/patterns/")
    results, err_results = fetch_json("/lab-results/")
    recommendations, err_recommendations = fetch_json("/recommendations/")

    errors = [err for err in [err_rules, err_patterns, err_results, err_recommendations] if err]

    stats = {
        "rules": str(len(rules)) if isinstance(rules, list) else "—",
        "patterns": str(len(patterns)) if isinstance(patterns, list) else "—",
        "results": str(len(results)) if isinstance(results, list) else "—",
        "recommendations": str(len(recommendations)) if isinstance(recommendations, list) else "—",
    }

    return stats, " | ".join(errors) if errors else None
