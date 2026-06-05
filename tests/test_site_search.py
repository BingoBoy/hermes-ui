from __future__ import annotations

import asyncio

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.site_search import (
    SiteSearchError,
    SiteSearchInput,
    build_flexible_search_regex,
    normalize_search_text,
    site_safety_payload,
    score_site_search_result,
    search_public_website,
    validate_public_site_url,
)


class FakeSearchField:
    def __init__(self) -> None:
        self.filled = ""
        self.pressed = ""

    async def count(self) -> int:
        return 1

    async def is_visible(self) -> bool:
        return True

    async def fill(self, value: str) -> None:
        self.filled = value

    async def press(self, value: str) -> None:
        self.pressed = value


class FakeLocator:
    def __init__(
        self,
        *,
        search_field: FakeSearchField,
        links: list[dict[str, str]],
    ) -> None:
        self.search_field = search_field
        self.links = links

    @property
    def first(self) -> FakeSearchField:
        return self.search_field

    async def evaluate_all(self, script: str) -> list[dict[str, str]]:
        return self.links


class FakePage:
    def __init__(self) -> None:
        self.search_field = FakeSearchField()
        self.visited_url = ""
        self.links = [
            {
                "title": "Star.Wars.1977",
                "url": "https://example.com/star-wars",
                "rawText": "Star.Wars.1977 movie",
            },
            {
                "title": "Star.Wars.Script",
                "url": "javascript:alert(1)",
                "rawText": "Star.Wars.Script",
            },
            {
                "title": "Star.Wars.Magnet",
                "url": "magnet:?xt=urn:btih:abc",
                "rawText": "Star.Wars.Magnet",
            },
            {
                "title": "Star.Wars.Download",
                "url": "https://example.com/download/star-wars",
                "rawText": "Star.Wars.Download",
            },
            {
                "title": "Star.Wars.Detail",
                "url": "https://example.com/torrent/star-wars",
                "rawText": "Star.Wars.Detail",
            },
            {
                "title": "Completely unrelated",
                "url": "https://example.com/other",
                "rawText": "Nothing to see",
            },
        ]

    async def goto(self, url: str, *, wait_until: str, timeout: int) -> None:
        self.visited_url = url

    def locator(self, selector: str) -> FakeLocator:
        return FakeLocator(search_field=self.search_field, links=self.links)

    async def wait_for_load_state(self, state: str, *, timeout: int) -> None:
        return None


class FakeBrowser:
    def __init__(self) -> None:
        self.page = FakePage()
        self.closed = False

    async def new_page(self) -> FakePage:
        return self.page

    async def close(self) -> None:
        self.closed = True


class FakeChromium:
    def __init__(self) -> None:
        self.browser = FakeBrowser()

    async def launch(self, *, headless: bool) -> FakeBrowser:
        return self.browser


class FakePlaywright:
    def __init__(self) -> None:
        self.chromium = FakeChromium()


class FakePlaywrightContext:
    def __init__(self) -> None:
        self.playwright = FakePlaywright()

    async def __aenter__(self) -> FakePlaywright:
        return self.playwright

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None


def test_normalize_search_text_handles_media_separators() -> None:
    assert normalize_search_text("The.Matrix.1999") == "the matrix 1999"
    assert normalize_search_text("the_matrix-1999") == "the matrix 1999"
    assert normalize_search_text("  Café.Society  ") == "cafe society"


def test_flexible_regex_matches_common_separators() -> None:
    regex = build_flexible_search_regex("star wars")

    assert regex.search("star wars")
    assert regex.search("star.wars")
    assert regex.search("star_wars")
    assert regex.search("star-wars")
    assert regex.search("Star.Wars.1977")


def test_score_site_search_result_uses_expected_tiers() -> None:
    assert score_site_search_result("star wars", "star wars") == 100
    assert score_site_search_result("star wars", "Star.Wars.1977") == 80
    assert score_site_search_result("star wars", "wars then star") == 60
    assert score_site_search_result("star wars", "star trek") == 40
    assert score_site_search_result("star wars", "blade runner") == 0


def test_validate_public_site_url_rejects_non_public_targets() -> None:
    with pytest.raises(SiteSearchError) as invalid_scheme:
        validate_public_site_url("file:///tmp/test.html")
    assert invalid_scheme.value.error == "invalid_url"

    with pytest.raises(SiteSearchError) as localhost:
        validate_public_site_url("http://localhost:8000")
    assert localhost.value.error == "private_url"

    with pytest.raises(SiteSearchError) as private_ip:
        validate_public_site_url("http://192.168.1.10")
    assert private_ip.value.error == "private_url"


def test_site_safety_payload_marks_1337x_as_restricted_metadata() -> None:
    payload = site_safety_payload("https://1337x.to/home/")

    assert payload["restrictedMetadataMode"] is True
    assert payload["classification"] == "torrent_index"
    assert "read_visible_result_metadata" in payload["allowedActions"]
    assert "follow_magnet_links" in payload["blockedActions"]
    assert "download_files" in payload["blockedActions"]


def test_site_safety_payload_keeps_regular_sites_unrestricted() -> None:
    payload = site_safety_payload("https://www.wikipedia.org/")

    assert payload["restrictedMetadataMode"] is False
    assert payload["classification"] == "public_website"


def test_search_public_website_returns_ranked_structured_results() -> None:
    fake_context = FakePlaywrightContext()

    payload = asyncio.run(
        search_public_website(
            SiteSearchInput(site_url="https://example.com/search", query="star wars"),
            playwright_context_manager=fake_context,
        )
    )

    assert payload["sourceUrl"] == "https://example.com/search"
    assert payload["query"] == "star wars"
    assert payload["normalizedQuery"] == "star wars"
    assert payload["safety"]["restrictedMetadataMode"] is False
    assert payload["results"] == [
        {
            "title": "Star.Wars.1977",
            "url": "https://example.com/star-wars",
            "snippet": "Star.Wars.1977 movie",
            "rawText": "Star.Wars.1977 movie",
            "score": 80,
        }
    ]
    browser = fake_context.playwright.chromium.browser
    assert browser.page.visited_url == "https://example.com/search"
    assert browser.page.search_field.filled == "star wars"
    assert browser.page.search_field.pressed == "Enter"
    assert browser.closed is True


def test_site_search_api_rejects_private_url() -> None:
    client = TestClient(app)

    response = client.get(
        "/api/site-search",
        params={"siteUrl": "http://localhost:8000", "query": "star wars"},
    )

    assert response.status_code == 400
    assert response.json()["detail"]["error"] == "private_url"


def test_site_search_api_error_includes_restricted_safety_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_search(input_data: SiteSearchInput) -> dict[str, object]:
        raise SiteSearchError(
            "search_field_not_found",
            "No visible search field was found on the public website",
            status_code=422,
        )

    monkeypatch.setattr("backend.main.search_public_website", fake_search)
    client = TestClient(app)

    response = client.get(
        "/api/site-search",
        params={"siteUrl": "https://1337x.to/home/", "query": "ubuntu"},
    )

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["error"] == "search_field_not_found"
    assert detail["safety"]["restrictedMetadataMode"] is True
    assert detail["safety"]["classification"] == "torrent_index"
