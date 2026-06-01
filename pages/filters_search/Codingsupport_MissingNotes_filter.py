from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from playwright.sync_api import sync_playwright

from pages.filters_search.Codingsupport_Awaiting_CDQ_filter import (
    CodingSupportAwaitingCDQFilterPage,
    _login_form_visible,
    _login_with_retry,
)


class CodingSupportMissingNotesFilterPage(CodingSupportAwaitingCDQFilterPage):
    """Filter automation for Coding Support > Missing Notes."""

    TARGET_LINKS = [
        'a:has-text("Missing Notes")',
        'button:has-text("Missing Notes")',
        'p:has-text("Missing Notes")',
        'span:has-text("Missing Notes")',
        'div:has-text("Missing Notes")',
        'text=Missing Notes',
    ]

    def _coding_support_filter_available(self) -> bool:
        checks = [
            self.page.get_by_text(re.compile(r"Coding Support", re.I)).first,
            self.page.get_by_text(re.compile(r"Missing Notes", re.I)).first,
            self.page.get_by_placeholder(re.compile(r"Search by Episode ID", re.I)).first,
            self.page.get_by_text(re.compile(r"Episode Identifier|Total Episodes", re.I)).first,
        ]
        for check in checks:
            try:
                if check.count() > 0 and check.is_visible():
                    return self._visible_filter_toggle() is not None
            except Exception:
                continue
        return False


def run_coding_support_missing_notes_filter_search(
    username: str, password: str, filter_name: str | None = None
) -> None:
    from config.settings import Settings
    from pages.login_page import LoginPage

    settings = Settings(env=os.getenv("ENV", "dev"))
    headless = settings.headless
    headless_env = os.getenv("HEADLESS")
    if headless_env is not None:
        headless = headless_env.lower() in ("1", "true", "yes")

    filters_to_run = [filter_name] if filter_name else CodingSupportMissingNotesFilterPage.DEFAULT_FILTERS
    known_filters = set(CodingSupportMissingNotesFilterPage.FILTERS) | set(
        CodingSupportMissingNotesFilterPage.FILTER_GROUPS
    )
    unknown_filters = [name for name in filters_to_run if name not in known_filters]
    if unknown_filters:
        available = ", ".join(sorted(known_filters))
        raise ValueError(f"Unknown filter name: {unknown_filters[0]}. Available filters: {available}")

    with sync_playwright() as playwright:
        browser_type = getattr(playwright, settings.browser)
        browser = browser_type.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()
        try:
            login_page = LoginPage(page)
            filters_page = CodingSupportMissingNotesFilterPage(page)

            print("Navigating to login page...")
            login_page.open_login_page(settings.base_url)
            login_page.wait_for_page_load()

            print("Performing login...")
            _login_with_retry(login_page, username, password)

            print("Opening Coding Support > Missing Notes...")
            if not filters_page.open_coding_support_target(settings.base_url):
                filters_page.capture_debug_artifacts("coding_support_missing_notes_filter_navigation_failure")
                raise AssertionError("Could not open Coding Support > Missing Notes page")

            filters_page.open_filter_panel()

            for current_filter in filters_to_run:
                print(f"Applying {current_filter} filter...")
                filters_page.apply_named_filter(current_filter)
                print(f"[OK] {current_filter} filter applied")
                try:
                    filters_page.clear_all_filters()
                except Exception as exc:
                    print(f"Could not clear filters after {current_filter}: {exc}")

            print("Completed Coding Support > Missing Notes filter search run")
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    username = os.getenv("IMEDX_USERNAME", "Sai")
    password = os.getenv("IMEDX_PASSWORD", "Imedx@123")
    selected_filter = os.getenv("IMEDX_FILTER_NAME")
    run_coding_support_missing_notes_filter_search(username, password, selected_filter)
