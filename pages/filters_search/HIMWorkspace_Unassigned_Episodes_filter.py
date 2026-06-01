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


class HIMWorkspaceUnassignedEpisodesFilterPage(UnassignedEpisodesFilterPage):
    """Filter automation for HIM Workspace > Unassigned Episodes."""

    DEFAULT_FILTERS = [
        "episode_identifier",
        "mrn",
        "admission_date_range",
        "separation_date_range",
        "specialty",
        "queue",
        "coders",
        "priority",
        "status",
        "health_fund_contract",
        "los_operator",
        "los",
        "provisional_drg",
    ]

    def open_unassigned_episodes(self, base_url: str | None = None) -> bool:
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

        if nav.open_unassigned_episodes():
            return True

        return self._him_unassigned_filter_available()

    def clear_all_filters(self) -> None:
        self.open_filter_panel()
        clear_button = self._visible_first(self.CLEAR_ALL)
        if clear_button:
            clear_button.click()
            self.wait_for_results()
            return

        if self._him_filters_are_already_clear():
            return

        self.capture_debug_artifacts("him_unassigned_episodes_clear_filters_not_found")
        raise AssertionError("Clear All/Reset button not found")

    def _enable_dependent_filter(self, label: str) -> None:
        if label == "Queue":
            self._wait_for_filter_enabled("Queue", timeout=8000)
            return

        super()._enable_dependent_filter(label)

    def _him_unassigned_filter_available(self) -> bool:
        checks = [
            self.page.get_by_text(re.compile(r"HIM Workspace", re.I)).first,
            self.page.get_by_text(re.compile(r"Unassigned Episodes", re.I)).first,
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

    def _him_filters_are_already_clear(self) -> bool:
        try:
            header = self.page.locator('text="HIM Workspace Filters"').first.locator(
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


def run_him_unassigned_episodes_filter_search(
    username: str, password: str, filter_name: str | None = None
) -> None:
    from config.settings import Settings
    from pages.login_page import LoginPage

    settings = Settings(env=os.getenv("ENV", "dev"))
    headless = settings.headless
    headless_env = os.getenv("HEADLESS")
    if headless_env is not None:
        headless = headless_env.lower() in ("1", "true", "yes")

    filters_to_run = [filter_name] if filter_name else HIMWorkspaceUnassignedEpisodesFilterPage.DEFAULT_FILTERS
    known_filters = (
        set(HIMWorkspaceUnassignedEpisodesFilterPage.FILTERS)
        | set(HIMWorkspaceUnassignedEpisodesFilterPage.FILTER_GROUPS)
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
            filters_page = HIMWorkspaceUnassignedEpisodesFilterPage(page)

            print("Navigating to login page...")
            login_page.open_login_page(settings.base_url)
            login_page.wait_for_page_load()

            print("Performing login...")
            login_page.login(username, password)
            page.wait_for_timeout(3000)

            print("Opening HIM Workspace > Unassigned Episodes...")
            if not filters_page.open_unassigned_episodes(settings.base_url):
                filters_page.capture_debug_artifacts("him_unassigned_episodes_filter_navigation_failure")
                raise AssertionError("Could not open HIM Workspace > Unassigned Episodes page")

            filters_page.open_filter_panel()

            for current_filter in filters_to_run:
                print(f"Applying {current_filter} filter...")
                filters_page.apply_named_filter(current_filter)
                print(f"[OK] {current_filter} filter applied")
                try:
                    filters_page.clear_all_filters()
                except Exception as exc:
                    print(f"Could not clear filters after {current_filter}: {exc}")

            print("Completed HIM Workspace > Unassigned Episodes filter search run")
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    username = os.getenv("IMEDX_USERNAME", "Sai")
    password = os.getenv("IMEDX_PASSWORD", "Imedx@123")
    selected_filter = os.getenv("IMEDX_FILTER_NAME")
    run_him_unassigned_episodes_filter_search(username, password, selected_filter)
