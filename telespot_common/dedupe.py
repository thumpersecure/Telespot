from __future__ import annotations

from typing import Any, Dict, List


def _normalize_url(url: str) -> str:
    return url.rstrip("/").lower().strip()


def deduplicate_results_list(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate results by URL from a flat result list."""

    seen_urls = set()
    unique: List[Dict[str, Any]] = []

    for result in results:
        url = _normalize_url(result.get("url", ""))
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique.append(result)
        elif not url:
            unique.append(result)

    return unique


def deduplicate_results_dict(all_results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
    """Remove duplicate results across format groups by URL."""

    seen_urls = set()
    deduped: Dict[str, List[Dict[str, Any]]] = {}

    for fmt, results in all_results.items():
        unique_results: List[Dict[str, Any]] = []
        for result in results:
            url = _normalize_url(result.get("url", ""))
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
            elif not url:
                unique_results.append(result)
        deduped[fmt] = unique_results

    return deduped

