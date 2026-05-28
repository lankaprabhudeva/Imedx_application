import os
import pytest
from playwright.sync_api import sync_playwright
from config.settings import Settings


@pytest.fixture(scope="session")
def app_settings():
    # Allow overriding environment via ENV and headless via HEADLESS env vars
    env = os.getenv("ENV", "dev")
    settings = Settings(env=env)

    # Optional HEADLESS override ("true"/"false")
    headless_env = os.getenv("HEADLESS")
    if headless_env is not None:
        settings._headless_override = headless_env.lower() in ("1", "true", "yes")

    return settings


@pytest.fixture(scope="function")
def page(app_settings):
    with sync_playwright() as playwright:
        browser_name = app_settings.browser
        browser_type = getattr(playwright, browser_name)

        # Prefer explicit override if provided
        headless = getattr(app_settings, "_headless_override", None)
        if headless is None:
            headless = app_settings.headless

        browser = browser_type.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()

        yield page

        context.close()
        browser.close()
