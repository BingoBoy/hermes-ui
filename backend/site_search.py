"""Generic public website search adapter for Bob/Hermes."""

from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

MAX_RESULTS = 20
SEARCH_TIMEOUT_MS = 15000
LOAD_SETTLE_TIMEOUT_MS = 5000

SEARCH_FIELD_SELECTORS = (
    'input[type="search"]',
    'input[name*="search" i]',
    'input[placeholder*="search" i]',
    'input[name*="q" i]',
    'input[type="text"]',
    "textarea",
)

LOCAL_HOSTNAMES = frozenset({"localhost", "127.0.0.1", "0.0.0.0", "::1"})
RESTRICTED_METADATA_HOSTS = frozenset(
    {
        "1337x.to",
        "www.1337x.to",
    }
)
DISALLOWED_RESULT_SCHEMES = frozenset({"magnet"})
DISALLOWED_RESULT_PATH_TERMS = (
    "/torrent/",
    "/torrentdownload/",
    "/download/",
    "/magnet/",
)


class SiteSearchError(Exception):
    """Raised when public website search cannot be completed safely."""

    def __init__(self, error: str, detail: str, status_code: int = 400) -> None:
        self.error = error
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


@dataclass(frozen=True)
class SiteSearchInput:
    site_url: str
    query: str


@dataclass(frozen=True)
class SiteSearchResult:
    title: str
    url: str
    snippet: str | None
    raw_text: str | None
    score: int


def normalize_search_text(value: str) -> str:
    """Normalize title/search text across common media filename separators."""
    import unicodedata

    without_diacritics = "".join(
        char
        for char in unicodedata.normalize("NFKD", value)
        if not unicodedata.combining(char)
    )
    normalized_separators = re.sub(r"[._\-]+", " ", without_diacritics.lower())
    return re.sub(r"\s+", " ", normalized_separators).strip()


def build_flexible_search_regex(query: str) -> re.Pattern[str]:
    """Build a regex matching terms separated by spaces, dots, underscores or dashes."""
    terms = [term for term in normalize_search_text(query).split(" ") if term]
    pattern = r"[\s._-]+".join(re.escape(term) for term in terms)
    if not pattern:
        raise SiteSearchError("invalid_query", "query is required")
    return re.compile(pattern, re.IGNORECASE)


def score_site_search_result(query: str, text: str) -> int:
    """Score visible result text against a normalized/flexible query."""
    normalized_query = normalize_search_text(query)
    normalized_text = normalize_search_text(text)
    if not normalized_query or not normalized_text:
        return 0
    if normalized_query == normalized_text:
        return 100
    if build_flexible_search_regex(query).search(text):
        return 80

    terms = normalized_query.split()
    matched_terms = [term for term in terms if term in normalized_text]
    if len(matched_terms) == len(terms):
        return 60
    if matched_terms:
        return 40
    return 0


def validate_public_site_url(site_url: str) -> str:
    """Validate that the target looks like a public http(s) page."""
    normalized = site_url.strip()
    parsed = urlparse(normalized)
    if parsed.scheme not in {"http", "https"}:
        raise SiteSearchError(
            "invalid_url",
            "siteUrl must be an http or https URL",
        )
    if not parsed.hostname:
        raise SiteSearchError("invalid_url", "siteUrl must include a hostname")

    host = parsed.hostname.strip().lower()
    if host in LOCAL_HOSTNAMES or host.endswith(".local"):
        raise SiteSearchError(
            "private_url",
            "siteUrl must point to a public website, not a local host",
        )

    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return normalized

    if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
        raise SiteSearchError(
            "private_url",
            "siteUrl must point to a public website, not a private address",
        )
    return normalized


def site_safety_payload(site_url: str) -> dict[str, Any]:
    host = (urlparse(site_url).hostname or "").lower()
    restricted = host in RESTRICTED_METADATA_HOSTS
    return {
        "restrictedMetadataMode": restricted,
        "classification": "torrent_index" if restricted else "public_website",
        "allowedActions": [
            "open_public_page",
            "submit_visible_search_field",
            "read_visible_result_metadata",
        ],
        "blockedActions": [
            "login",
            "use_private_cookies",
            "bypass_paywalls_or_captcha",
            "follow_magnet_links",
            "download_files",
            "extract_torrent_files",
        ],
    }


async def search_public_website(
    input_data: SiteSearchInput,
    *,
    playwright_context_manager: Any | None = None,
) -> dict[str, Any]:
    """Search a public website through its visible search field."""
    site_url = validate_public_site_url(input_data.site_url)
    query = input_data.query.strip()
    if not query:
        raise SiteSearchError("invalid_query", "query is required")

    context_manager = playwright_context_manager
    if context_manager is None:
        try:
            from playwright.async_api import async_playwright
        except ImportError as exc:
            raise SiteSearchError(
                "search_runtime_unavailable",
                "Playwright is not installed; install the browser runtime before public website search can run",
                status_code=503,
            ) from exc
        context_manager = async_playwright()

    async with context_manager as playwright:
        try:
            browser = await playwright.chromium.launch(headless=True)
        except Exception as exc:
            raise SiteSearchError(
                "browser_launch_failed",
                "Could not start the headless browser runtime",
                status_code=503,
            ) from exc
        try:
            page = await browser.new_page()
            try:
                await page.goto(
                    site_url,
                    wait_until="domcontentloaded",
                    timeout=SEARCH_TIMEOUT_MS,
                )
            except Exception as exc:
                raise SiteSearchError(
                    "navigation_failed",
                    "The public website could not be opened within the search timeout",
                    status_code=422,
                ) from exc
            search_field = await _find_search_field(page)
            if search_field is None:
                raise SiteSearchError(
                    "search_field_not_found",
                    "No visible search field was found on the public website",
                    status_code=422,
                )

            try:
                await search_field.fill(query)
                await search_field.press("Enter")
            except Exception as exc:
                raise SiteSearchError(
                    "search_submit_failed",
                    "The search field was found, but the query could not be submitted",
                    status_code=422,
                ) from exc
            try:
                await page.wait_for_load_state(
                    "networkidle",
                    timeout=LOAD_SETTLE_TIMEOUT_MS,
                )
            except Exception:
                pass

            try:
                raw_results = await _extract_visible_links(page)
            except Exception as exc:
                raise SiteSearchError(
                    "result_extraction_failed",
                    "Search ran, but visible result links could not be read",
                    status_code=422,
                ) from exc
        finally:
            await browser.close()

    results = _rank_results(query, raw_results)
    return {
        "sourceUrl": site_url,
        "query": query,
        "normalizedQuery": normalize_search_text(query),
        "safety": site_safety_payload(site_url),
        "results": [result_to_payload(result) for result in results],
    }


async def _find_search_field(page: Any) -> Any | None:
    for selector in SEARCH_FIELD_SELECTORS:
        locator = page.locator(selector).first
        try:
            if await locator.count() > 0 and await locator.is_visible():
                return locator
        except Exception:
            continue
    return None


async def _extract_visible_links(page: Any) -> list[dict[str, str]]:
    return await page.locator("a[href]").evaluate_all(
        """(links) => links
          .filter((link) => {
            const rect = link.getBoundingClientRect();
            const style = window.getComputedStyle(link);
            return rect.width > 0 && rect.height > 0 && style.visibility !== "hidden";
          })
          .slice(0, 200)
          .map((link) => ({
            title: (link.innerText || link.getAttribute("aria-label") || link.title || "").trim(),
            url: link.href,
            rawText: (link.innerText || "").trim()
          }))"""
    )


def _rank_results(query: str, raw_results: list[dict[str, str]]) -> list[SiteSearchResult]:
    seen_urls: set[str] = set()
    results: list[SiteSearchResult] = []
    for raw in raw_results:
        url = (raw.get("url") or "").strip()
        title = (raw.get("title") or "").strip()
        raw_text = (raw.get("rawText") or title).strip()
        if not url or not title or url in seen_urls:
            continue
        if not _is_allowed_result_url(url):
            continue

        score = score_site_search_result(query, f"{title} {raw_text}")
        if score <= 0:
            continue

        seen_urls.add(url)
        snippet = raw_text[:240] if raw_text else None
        results.append(
            SiteSearchResult(
                title=title,
                url=url,
                snippet=snippet,
                raw_text=raw_text or None,
                score=score,
            )
        )

    return sorted(results, key=lambda result: result.score, reverse=True)[:MAX_RESULTS]


def _is_allowed_result_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme in DISALLOWED_RESULT_SCHEMES:
        return False
    if parsed.scheme not in {"http", "https"}:
        return False
    path = parsed.path.lower()
    return not any(term in path for term in DISALLOWED_RESULT_PATH_TERMS)


def result_to_payload(result: SiteSearchResult) -> dict[str, Any]:
    return {
        "title": result.title,
        "url": result.url,
        "snippet": result.snippet,
        "rawText": result.raw_text,
        "score": result.score,
    }
