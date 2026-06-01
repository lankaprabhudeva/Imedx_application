from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from playwright.sync_api import sync_playwright

from pages.filters_search.Coderworkspace_filter import UnassignedEpisodesFilterPage
from pages.unassignepisode_page import UnassignedEpisodePage


class AuditorWorkspaceFilterPage(UnassignedEpisodesFilterPage):
    """Filter automation for Auditor Workspace."""

    AUDITOR_WORKSPACE_LINKS = [
        'a:has-text("Auditor Workspace")',
        'button:has-text("Auditor Workspace")',
        '[role="link"]:has-text("Auditor Workspace")',
        '[role="button"]:has-text("Auditor Workspace")',
        'div.sidebar-navigation-container >> text="Auditor Workspace"',
        'text=Auditor Workspace',
    ]

    DEFAULT_FILTERS = [
        "episode_identifier",
        "mrn",
        "admission_date_range",
        "separation_date_range",
        "specialty",
        "user_specific",
        "queue",
        "status",
        "health_fund_contract",
        "los_operator",
        "los",
        "provisional_drg",
    ]

    def open_auditor_workspace(self, base_url: str | None = None) -> bool:
        nav = UnassignedEpisodePage(self.page)

        if base_url:
            try:
                self.page.goto(base_url, wait_until="domcontentloaded")
                try:
                    self.page.wait_for_load_state("networkidle", timeout=5000)
                except Exception:
                    pass
            except Exception:
                pass

        opened_workflow = nav.open_code_workflow()
        if not opened_workflow:
            try:
                if base_url:
                    self.page.goto(base_url.rstrip("/") + "/Code-Workflow", wait_until="domcontentloaded")
                    try:
                        self.page.wait_for_load_state("networkidle", timeout=5000)
                    except Exception:
                        pass
                    opened_workflow = True
            except Exception:
                opened_workflow = False

        if not opened_workflow:
            return False

        if self._click_auditor_workspace():
            return True

        return self._auditor_workspace_filter_available()

    def clear_all_filters(self) -> None:
        self.open_filter_panel()
        clear_button = self._visible_first(self.CLEAR_ALL)
        if clear_button:
            clear_button.click()
            self.wait_for_results()
            return

        if self._auditor_filters_are_already_clear():
            return

        self.capture_debug_artifacts("auditor_workspace_clear_filters_not_found")
        raise AssertionError("Clear All/Reset button not found")

    def _enable_dependent_filter(self, label: str) -> None:
        super()._enable_dependent_filter(label)

    def _click_auditor_workspace(self) -> bool:
        for _ in range(3):
            for selector in self.AUDITOR_WORKSPACE_LINKS:
                try:
                    items = self.page.locator(selector)
                    for index in range(items.count()):
                        item = items.nth(index)
                        if not item.is_visible():
                            continue
                        item.scroll_into_view_if_needed()
                        item.click(force=True)
                        try:
                            self.page.wait_for_load_state("networkidle", timeout=8000)
                        except Exception:
                            pass
                        self.page.wait_for_timeout(1000)
                        if self._auditor_workspace_filter_available():
                            return True
                except Exception:
                    continue
            self.page.wait_for_timeout(700)
        return False

    def _auditor_workspace_filter_available(self) -> bool:
        checks = [
            self.page.get_by_text(re.compile(r"Auditor Workspace", re.I)).first,
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

    def _auditor_filters_are_already_clear(self) -> bool:
        try:
            header = self.page.locator('text="Auditor Workspace Filters"').first.locator(
                'xpath=ancestor::*[contains(@class, "modal") or @role="dialog" or contains(@class, "MuiBox-root")][1]'
            )
            text = header.inner_text(timeout=1000) if header.count() > 0 else self.page.inner_text("body", timeout=1000)
        except Exception:
            return False

        active_filter_patterns = [
            r"Episode Identifier\s*:",
            r"MRN/UR\s*:",
            r"Admission Date\s*:",
            r"Separation Date\s*:",
            r"Speciali[at]y\s*:",
            r"Queue\s*:",
            r"Coders\s*:",
            r"Auditors\s*:",
            r"Priority\s*:",
            r"Status\s*:",
            r"Health Fund Contract\s*:",
            r"LOS\s*:",
            r"Provisional DRG\s*:",
        ]
        return not any(re.search(pattern, text, re.I) for pattern in active_filter_patterns)


def run_auditor_workspace_filter_search(
    username: str, password: str, filter_name: str | None = None
) -> None:
    from config.settings import Settings
    from pages.login_page import LoginPage

    settings = Settings(env=os.getenv("ENV", "dev"))
    headless = settings.headless
    headless_env = os.getenv("HEADLESS")
    if headless_env is not None:
        headless = headless_env.lower() in ("1", "true", "yes")

    filters_to_run = [filter_name] if filter_name else AuditorWorkspaceFilterPage.DEFAULT_FILTERS
    known_filters = set(AuditorWorkspaceFilterPage.FILTERS) | set(AuditorWorkspaceFilterPage.FILTER_GROUPS)
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
            filters_page = AuditorWorkspaceFilterPage(page)

            print("Navigating to login page...")
            login_page.open_login_page(settings.base_url)
            login_page.wait_for_page_load()

            print("Performing login...")
            _login_with_retry(login_page, username, password)

            print("Opening Auditor Workspace...")
            if not filters_page.open_auditor_workspace(settings.base_url):
                filters_page.capture_debug_artifacts("auditor_workspace_filter_navigation_failure")
                raise AssertionError("Could not open Auditor Workspace page")

            filters_page.open_filter_panel()

            for current_filter in filters_to_run:
                print(f"Applying {current_filter} filter...")
                filters_page.apply_named_filter(current_filter)
                print(f"[OK] {current_filter} filter applied")
                try:
                    filters_page.clear_all_filters()
                except Exception as exc:
                    print(f"Could not clear filters after {current_filter}: {exc}")

            print("Completed Auditor Workspace filter search run")
        finally:
            context.close()
            browser.close()


def _login_with_retry(login_page, username: str, password: str) -> None:
    for attempt in range(2):
        login_page.login(username, password)
        login_page.page.wait_for_timeout(3000)
        if not _login_form_visible(login_page.page):
            return
        if attempt == 0:
            print("Login form still visible; retrying login...")

    raise AssertionError("Login did not complete; login form is still visible")


def _login_form_visible(page) -> bool:
    try:
        form = page.locator("form.login-form").first
        return form.count() > 0 and form.is_visible()
    except Exception:
        return False


if __name__ == "__main__":
    username = os.getenv("IMEDX_USERNAME", "Sai")
    password = os.getenv("IMEDX_PASSWORD", "Imedx@123")
    selected_filter = os.getenv("IMEDX_FILTER_NAME")
    run_auditor_workspace_filter_search(username, password, selected_filter)
