"""Playwright E2E smoke tests — assumes app is running."""

import os
import sys
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

DEFAULT_STREAMLIT_URL = os.getenv("STREAMLIT_URL", "http://localhost:8501")
DEFAULT_WIDGET_URL = os.getenv("WIDGET_URL", "http://localhost:8001")


@pytest.fixture
def app_url(request) -> str:
    base = request.config.getoption("--base-url", default=None)
    return base or DEFAULT_STREAMLIT_URL


@pytest.fixture
def widget_url() -> str:
    return os.getenv("WIDGET_URL", DEFAULT_WIDGET_URL)


class TestAppSmoke:
    def test_app_loads(self, page: Page, app_url: str):
        """Smoke: app loads and shows header."""
        page.goto(app_url)
        expect(page.get_by_role("heading", name="LinguaChat")).to_be_visible()

    def test_sidebar_has_settings(self, page: Page, app_url: str):
        """Sidebar settings section is visible."""
        page.goto(app_url)
        expect(page.get_by_role("heading", name="Settings")).to_be_visible()

    def test_all_four_modes_rendered(self, page: Page, app_url: str):
        """All 4 mode radio buttons are present."""
        page.goto(app_url)
        radiogroup = page.get_by_role("radiogroup", name="Learning Mode")
        expect(radiogroup).to_be_visible()
        expect(page.get_by_text("💬 Conversation", exact=True)).to_be_visible()
        expect(page.get_by_text("📝 Grammar Check", exact=True)).to_be_visible()
        expect(page.get_by_text("📚 Vocabulary", exact=True)).to_be_visible()
        expect(page.get_by_text("🎯 Quiz", exact=True)).to_be_visible()

    def test_chat_input_exists(self, page: Page, app_url: str):
        """Chat input textbox is rendered."""
        page.goto(app_url)
        expect(page.get_by_placeholder("Type your message here...")).to_be_visible()

    def test_language_combobox(self, page: Page, app_url: str):
        """Target language combobox is present."""
        page.goto(app_url)
        expect(page.get_by_role("combobox", name="Target Language")).to_be_visible()

    def test_clear_chat_button(self, page: Page, app_url: str):
        """Clear Chat History button is visible."""
        page.goto(app_url)
        expect(page.get_by_role("button", name="Clear Chat History")).to_be_visible()


class TestWidgetEmbed:
    def test_widget_health(self, widget_url: str):
        """Widget API health endpoint responds."""
        import httpx

        resp = httpx.get(f"{widget_url}/api/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_widget_page_loads(self, page: Page, widget_url: str):
        """Widget page loads with chat bubble."""
        page.goto(widget_url)
        expect(page.get_by_label("Open chat")).to_be_visible()

    def test_example_page_has_embed(self, page: Page, widget_url: str):
        """Example embed page loads with iframe."""
        page.goto(f"{widget_url}/example/index.html")
        expect(page.get_by_role("heading", name="My Website")).to_be_visible()
        iframes = page.locator("iframe")
        expect(iframes.first).to_be_visible()
