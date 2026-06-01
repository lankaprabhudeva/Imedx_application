from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from playwright.sync_api import expect, sync_playwright

from pages.filters_search.Coderworkspace_filter import UnassignedEpisodesFilterPage
from pages.unassignepisode_page import UnassignedEpisodePage


class CodingSupportAwaitingCDQFilterPage(UnassignedEpisodesFilterPage):
    """Filter automation for Coding Support > Awaiting CDQ."""

    CODING_SUPPORT_LINKS = [
        'a:has-text("Coding Support")',
        'button:has-text("Coding Support")',
        '[role="link"]:has-text("Coding Support")',
        '[role="button"]:has-text("Coding Support")',
        'div.sidebar-navigation-container >> text="Coding Support"',
        'text=Coding Support',
    ]
    TARGET_LINKS = [
        'a:has-text("Awaiting CDQ")',
        'button:has-text("Awaiting CDQ")',
        'p:has-text("Awaiting CDQ")',
        'span:has-text("Awaiting CDQ")',
        'div:has-text("Awaiting CDQ Response")',
        'div:has-text("Awaiting CDQ")',
        'text=Awaiting CDQ Response',
        'text=Awaiting CDQ',
    ]
    DEFAULT_FILTERS = [
        "episode_identifier",
        "mrn",
        "admission_date_range",
        "separation_date_range",
        "specialty",
        "queue",
        "priority",
        "status",
        "health_fund_contract",
        "los_operator",
        "los",
        "provisional_drg",
    ]

    def _filter_card(self, label: str):
        if label == "LOS Operator":
            los_card = self.page.locator('.cs-los-operator')
            for index in range(los_card.count()):
                card = los_card.nth(index)
                try:
                    if card.is_visible():
                        return card
                except Exception:
                    continue
        return super()._filter_card(label)

    def _collect_select_options(self, label: str, seed: str | None = None) -> list[str]:
        if label == "LOS Operator":
            self.open_filter_panel()
            card = self._filter_card(label)
            control = self._select_control(card)
            if not control:
                self.capture_debug_artifacts(f"coding_support_awaiting_cdq_los_operator_select_not_found")
                raise AssertionError(f"LOS Operator select control not found")

            control.click(force=True)
            self.page.wait_for_timeout(500)

            if seed:
                editable_input = self._select_input(card)
                if editable_input:
                    try:
                        editable_input.fill(seed)
                    except Exception:
                        self.page.keyboard.type(seed)
                    self.page.wait_for_timeout(500)

            options = self._visible_dropdown_option_texts()
            self._close_open_dropdown()
            if not options:
                self.capture_debug_artifacts(f"coding_support_awaiting_cdq_los_operator_options_not_found")
                raise AssertionError("No LOS Operator dropdown options available")
            return options

        return super()._collect_select_options(label, seed)

    def open_coding_support_target(self, base_url: str | None = None) -> bool:
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

        if not self._click_first_visible(self.CODING_SUPPORT_LINKS, verify=False):
            return False

        if self._click_first_visible(self.TARGET_LINKS, verify=True):
            return True

        return self._coding_support_filter_available()

    def clear_all_filters(self) -> None:
        self.open_filter_panel()
        clear_button = self._visible_first(self.CLEAR_ALL)
        if clear_button:
            clear_button.click()
            self.wait_for_results()
            return
        if self._filters_are_already_clear():
            return
        self.capture_debug_artifacts("coding_support_awaiting_cdq_clear_filters_not_found")
        raise AssertionError("Clear All/Reset button not found")

    def _enable_dependent_filter(self, label: str) -> None:
        if label == "Queue":
            self._wait_for_filter_enabled("Queue", timeout=8000)
            return
        if label == "Length of Stay (LOS)":
            self._select_los_operator("=")
            return
        super()._enable_dependent_filter(label)

    def _select_los_operator(self, operator: str) -> None:
        card = self._filter_card("Length of Stay (LOS)")
        operator_card = card.locator('.cs-los-operator')
        if operator_card.count() == 0:
            self.capture_debug_artifacts("coding_support_awaiting_cdq_los_operator_not_found")
            raise AssertionError("LOS operator control not found")

        control = self._select_control(operator_card)
        if not control:
            self.capture_debug_artifacts("coding_support_awaiting_cdq_los_operator_control_not_found")
            raise AssertionError("LOS operator control not found")

        control.click(force=True)
        self.page.wait_for_timeout(300)

        editable_input = self._select_input(operator_card)
        if editable_input:
            try:
                editable_input.fill(operator)
            except Exception:
                self.page.keyboard.type(operator)
            self.page.wait_for_timeout(300)

        self._click_dropdown_option(operator, fallback_to_first=False, fallback_to_enter=False)
        self.page.wait_for_timeout(500)

        los_input = card.locator('.cs-los-input-container input[type="number"]').first
        expect(los_input).to_be_visible(timeout=10000)
        if not los_input.is_enabled():
            self.capture_debug_artifacts("coding_support_awaiting_cdq_los_input_disabled")
            raise AssertionError("LOS number input did not enable after selecting operator")

    def _fill_filter_field(self, label: str, value: str) -> None:
        if label == "Length of Stay (LOS)":
            card = self._filter_card(label)
            los_input = card.locator('.cs-los-input-container input[type="number"]').first
            expect(los_input).to_be_visible(timeout=10000)
            if not los_input.is_enabled():
                self.capture_debug_artifacts("coding_support_awaiting_cdq_los_number_disabled")
                raise AssertionError(f"Filter field is disabled for label: {label}")
            los_input.fill(value)
            return
        super()._fill_filter_field(label, value)

    def _click_first_visible(self, selectors: list[str], verify: bool) -> bool:
        for _ in range(3):
            for selector in selectors:
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
                        if not verify or self._coding_support_filter_available():
                            return True
                except Exception:
                    continue
            self.page.wait_for_timeout(700)
        return False

    def _coding_support_filter_available(self) -> bool:
        checks = [
            self.page.get_by_text(re.compile(r"Coding Support", re.I)).first,
            self.page.get_by_text(re.compile(r"Awaiting CDQ", re.I)).first,
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

    def _filters_are_already_clear(self) -> bool:
        try:
            text = self.page.inner_text("body", timeout=1000)
        except Exception:
            return False
        active_filter_patterns = [
            r"Episode Identifier\s*:",
            r"MRN/UR\s*:",
            r"Admission Date\s*:",
            r"Separation Date\s*:",
            r"Speciali[at]y\s*:",
            r"Queue\s*:",
            r"Priority\s*:",
            r"Status\s*:",
            r"Health Fund Contract\s*:",
            r"LOS\s*:",
            r"Provisional DRG\s*:",
        ]
        return not any(re.search(pattern, text, re.I) for pattern in active_filter_patterns)


def run_coding_support_awaiting_cdq_filter_search(
    username: str, password: str, filter_name: str | None = None
) -> None:
    from config.settings import Settings
    from pages.login_page import LoginPage

    settings = Settings(env=os.getenv("ENV", "dev"))
    headless = settings.headless
    headless_env = os.getenv("HEADLESS")
    if headless_env is not None:
        headless = headless_env.lower() in ("1", "true", "yes")

    filters_to_run = [filter_name] if filter_name else CodingSupportAwaitingCDQFilterPage.DEFAULT_FILTERS
    known_filters = set(CodingSupportAwaitingCDQFilterPage.FILTERS) | set(CodingSupportAwaitingCDQFilterPage.FILTER_GROUPS)
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
            filters_page = CodingSupportAwaitingCDQFilterPage(page)

            print("Navigating to login page...")
            login_page.open_login_page(settings.base_url)
            login_page.wait_for_page_load()

            print("Performing login...")
            _login_with_retry(login_page, username, password)

            print("Opening Coding Support > Awaiting CDQ...")
            if not filters_page.open_coding_support_target(settings.base_url):
                filters_page.capture_debug_artifacts("coding_support_awaiting_cdq_filter_navigation_failure")
                raise AssertionError("Could not open Coding Support > Awaiting CDQ page")

            filters_page.open_filter_panel()

            for current_filter in filters_to_run:
                print(f"Applying {current_filter} filter...")
                filters_page.apply_named_filter(current_filter)
                print(f"[OK] {current_filter} filter applied")
                try:
                    filters_page.clear_all_filters()
                except Exception as exc:
                    print(f"Could not clear filters after {current_filter}: {exc}")

            print("Completed Coding Support > Awaiting CDQ filter search run")
        finally:
            context.close()
            browser.close()


def _login_with_retry(login_page, username: str, password: str) -> None:
    for attempt in range(2):
        try:
            # Before retry attempt, wait for form to be fully stable
            if attempt > 0:
                login_page.page.wait_for_timeout(3000)
                # Clear any text that might be in the inputs
                try:
                    all_inputs = login_page.page.locator('input')
                    for i in range(all_inputs.count()):
                        try:
                            input_elem = all_inputs.nth(i)
                            if input_elem.is_visible():
                                input_elem.clear()
                        except Exception:
                            pass
                except Exception:
                    pass
            
            login_page.login(username, password)
            login_page.page.wait_for_timeout(3000)
            if not _login_form_visible(login_page.page):
                return
            if attempt == 0:
                print("Login form still visible; retrying login...")
                # Wait longer before retrying and try to ensure form is in a good state
                login_page.page.wait_for_timeout(2000)
        except Exception as exc:
            if attempt == 0:
                print(f"Login attempt {attempt + 1} failed: {exc}. Retrying...")
                login_page.page.wait_for_timeout(2000)
            else:
                raise
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
    run_coding_support_awaiting_cdq_filter_search(username, password, selected_filter)
