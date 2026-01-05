import json
import logging
import os
import random
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import requests

DEFAULT_BASE_URL = os.getenv("UNIPILE_BASE_URL", "https://api26.unipile.com:15609")
SEARCH_ENDPOINT = "/api/v1/linkedin/search"
RETRY_STATUS_CODES = {401, 403, 429, 503, 504}

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def _compute_backoff(attempt: int, base: float = 1.5, cap: float = 60.0) -> float:
    exp = min(cap, base * (2 ** (attempt - 1)))
    jitter = random.uniform(0, exp * 0.2)
    return exp + jitter


def _atomic_write_json(path: str, payload: Dict[str, Any]) -> None:
    tmp_path = f"{path}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
    os.replace(tmp_path, path)


def _load_checkpoint(path: str) -> Optional[Dict[str, Any]]:
    if not path or not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception as exc:
        logger.warning("Failed to load checkpoint: %s", exc)
        return None


def _request_with_retries(
    session: requests.Session,
    url: str,
    *,
    headers: Dict[str, str],
    params: Dict[str, Any],
    payload: Dict[str, Any],
    timeout: int,
    max_retries: int,
) -> Tuple[int, Dict[str, Any]]:
    for attempt in range(1, max_retries + 1):
        try:
            response = session.post(
                url,
                headers=headers,
                params=params,
                json=payload,
                timeout=timeout,
            )
            status = response.status_code
            if status in RETRY_STATUS_CODES:
                if attempt >= max_retries:
                    response.raise_for_status()
                wait = _compute_backoff(attempt)
                logger.warning(
                    "Retryable status %s (attempt %s/%s). Waiting %.1fs",
                    status,
                    attempt,
                    max_retries,
                    wait,
                )
                time.sleep(wait)
                continue
            response.raise_for_status()
            return status, response.json()
        except requests.RequestException as exc:
            if attempt >= max_retries:
                raise
            wait = _compute_backoff(attempt)
            logger.warning(
                "Request error: %s (attempt %s/%s). Waiting %.1fs",
                exc,
                attempt,
                max_retries,
                wait,
            )
            time.sleep(wait)
    raise RuntimeError("Max retries exceeded")


def fetch_salesnav_people(
    search_params: Dict[str, Any],
    *,
    account_id: str,
    token: str,
    base_url: str = DEFAULT_BASE_URL,
    limit: int = 100,
    max_results: Optional[int] = None,
    min_delay: float = 1.0,
    max_delay: float = 2.0,
    checkpoint_path: str = "salesnav_checkpoint.json",
    checkpoint_every: int = 1,
    resume: bool = True,
    timeout: int = 30,
    max_retries: int = 5,
) -> List[Dict[str, Any]]:
    """
    Fetch all possible Sales Navigator results using cursor pagination.

    Requirements:
    - POST {base_url}/api/v1/linkedin/search
    - Headers: accept, content-type, and token in "Header"
    - Query params: account_id, limit (<=100), cursor (optional)
    - Body: {"api": "sales_navigator", "category": "people", ...filters}
    """
    if limit > 100:
        limit = 100

    session = requests.Session()
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Header": token,
    }

    results: List[Dict[str, Any]] = []
    seen_ids: set[str] = set()
    cursor: Optional[str] = None
    seen_cursors: set[str] = set()
    page = 0

    if resume and checkpoint_path:
        checkpoint = _load_checkpoint(checkpoint_path)
        if checkpoint:
            cursor = checkpoint.get("cursor")
            results = checkpoint.get("items", [])
            for item in results:
                key = item.get("public_identifier") or item.get("id") or item.get("provider_id")
                if key:
                    seen_ids.add(str(key))
            page = checkpoint.get("page", 0)
            logger.info(
                "Resuming from checkpoint: page=%s count=%s cursor=%s",
                page,
                len(results),
                bool(cursor),
            )

    url = f"{base_url.rstrip('/')}{SEARCH_ENDPOINT}"
    payload = {
        "api": "sales_navigator",
        "category": "people",
        **search_params,
    }

    while True:
        if max_results and len(results) >= max_results:
            logger.info("Reached max_results=%s. Stopping.", max_results)
            break

        params = {"account_id": account_id, "limit": limit}
        if cursor:
            params["cursor"] = cursor

        status, data = _request_with_retries(
            session,
            url,
            headers=headers,
            params=params,
            payload=payload,
            timeout=timeout,
            max_retries=max_retries,
        )

        items = data.get("items", []) or []
        paging = data.get("paging", {}) or {}
        next_cursor = data.get("cursor") or paging.get("cursor")
        total_count = paging.get("total_count")

        new_items = 0
        for item in items:
            key = item.get("public_identifier") or item.get("id") or item.get("provider_id")
            if key:
                key = str(key)
            if key and key in seen_ids:
                continue
            if key:
                seen_ids.add(key)
            results.append(item)
            new_items += 1
            if max_results and len(results) >= max_results:
                break

        page += 1
        logger.info(
            "Page %s | status=%s | new=%s | total=%s | cursor=%s | api_total=%s",
            page,
            status,
            new_items,
            len(results),
            bool(next_cursor),
            total_count,
        )

        if checkpoint_path and checkpoint_every and page % checkpoint_every == 0:
            _atomic_write_json(
                checkpoint_path,
                {
                    "cursor": next_cursor,
                    "page": page,
                    "count": len(results),
                    "items": results,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                },
            )

        if not next_cursor:
            logger.info("No cursor returned. Pagination finished.")
            break

        if next_cursor in seen_cursors:
            logger.warning("Cursor repeated. Stopping to avoid loop.")
            break

        cursor = next_cursor
        seen_cursors.add(next_cursor)

        if max_results and len(results) >= max_results:
            logger.info("Reached max_results=%s. Stopping.", max_results)
            break

        if max_delay and max_delay > 0:
            time.sleep(random.uniform(min_delay, max_delay))

    if checkpoint_path:
        _atomic_write_json(
            checkpoint_path,
            {
                "cursor": None,
                "page": page,
                "count": len(results),
                "items": results,
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "finished": True,
            },
        )

    return results


def _env_or_raise(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise RuntimeError(f"Missing required env var: {key}")
    return value


if __name__ == "__main__":
    # Adjust base_url by setting UNIPILE_BASE_URL (example: https://api26.unipile.com:15609)
    # Adjust filters in search_params as needed (keywords, location/industry include IDs, role/company, etc).
    token = _env_or_raise("UNIPILE_TOKEN")
    account_id = _env_or_raise("UNIPILE_ACCOUNT_ID")
    base_url = os.getenv("UNIPILE_BASE_URL", DEFAULT_BASE_URL)

    search_params = {
        "keywords": "rh - brasil",
        "location": {"include": ["103658898"]},
        "industry": {"include": ["48"]},
    }

    results = fetch_salesnav_people(
        search_params,
        account_id=account_id,
        token=token,
        base_url=base_url,
        limit=100,
        max_results=None,
        min_delay=1.0,
        max_delay=2.0,
        checkpoint_path="salesnav_checkpoint.json",
        checkpoint_every=1,
        resume=True,
        timeout=30,
        max_retries=5,
    )

    output_path = "salesnav_results.json"
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(results, handle, ensure_ascii=False, indent=2)
    logger.info("Saved %s results to %s", len(results), output_path)
