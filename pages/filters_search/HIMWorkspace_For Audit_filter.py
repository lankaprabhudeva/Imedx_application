from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from playwright.sync_api import sync_playwright

from pages.filters_search.HIMWorkspace_Unassigned_Episodes_filter import (
    HIMWorkspaceUnassignedEpisodesFilterPage,
)
from pages.unassignepisode_page import UnassignedEpisodePage


class HIMWorkspaceForAuditFilterPage(HIMWorkspaceUnassignedEpisodesFilterPage):
    """Filter automation for HIM Workspace > For Audit."""

    FOR_AUDIT_LINKS = [
        'a:has-text("For Audit")',
        'button:has-text("For Audit")',
        'p:has-text("For Audit")',
        'span:has-text("For Audit")',
        'div.coding-allocation-section:has-text("For Audit")',
        'text=For Audit',
    ]

    def open_for_audit(self, base_url: str | None = None) -> bool:
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

        if not nav.open_him_workspace():
            return False

        if self._click_for_audit():
            return True

        return self._for_audit_filter_available()

    def _click_for_audit(self) -> bool:
        for _ in range(3):
            for selector in self.FOR_AUDIT_LINKS:
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
                        self.page.wait_for_timeout(800)
                        if self._for_audit_filter_available():
                            return True
                except Exception:
                    continue
            self.page.wait_for_timeout(700)
        return False

    def _for_audit_filter_available(self) -> bool:
        checks = [
            self.page.get_by_text(re.compile(r"HIM Workspace", re.I)).first,
            self.page.get_by_text(re.compile(r"For Audit", re.I)).first,
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


def run_him_for_audit_filter_search(
    username: str, password: str, filter_name: str | None = None
) -> None:
    from config.settings import Settings
    from pages.login_page import LoginPage

    settings = Settings(env=os.getenv("ENV", "dev"))
    headless = settings.headless
    headless_env = os.getenv("HEADLESS")
    if headless_env is not None:
        headless = headless_env.lower() in ("1", "true", "yes")

    filters_to_run = [filter_name] if filter_name else HIMWorkspaceForAuditFilterPage.DEFAULT_FILTERS
    known_filters = (
        set(HIMWorkspaceForAuditFilterPage.FILTERS)
        | set(HIMWorkspaceForAuditFilterPage.FILTER_GROUPS)
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
            filters_page = HIMWorkspaceForAuditFilterPage(page)

            print("Navigating to login page...")
            login_page.open_login_page(settings.base_url)
            login_page.wait_for_page_load()

            print("Performing login...")
            login_page.login(username, password)
            page.wait_for_timeout(3000)

            print("Opening HIM Workspace > For Audit...")
            if not filters_page.open_for_audit(settings.base_url):
                filters_page.capture_debug_artifacts("him_for_audit_filter_navigation_failure")
                raise AssertionError("Could not open HIM Workspace > For Audit page")

            filters_page.open_filter_panel()

            for current_filter in filters_to_run:
                print(f"Applying {current_filter} filter...")
                filters_page.apply_named_filter(current_filter)
                print(f"[OK] {current_filter} filter applied")
                try:
                    filters_page.clear_all_filters()
                except Exception as exc:
                    print(f"Could not clear filters after {current_filter}: {exc}")

            print("Completed HIM Workspace > For Audit filter search run")
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    username = os.getenv("IMEDX_USERNAME", "Sai")
    password = os.getenv("IMEDX_PASSWORD", "Imedx@123")
    selected_filter = os.getenv("IMEDX_FILTER_NAME")
    run_him_for_audit_filter_search(username, password, selected_filter)
