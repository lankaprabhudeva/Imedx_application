import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CWD = Path.cwd()
for path in (ROOT, CWD):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from pages.base_page import BasePage


class CodingCompletePage(BasePage):
    """Page object for the Coding Complete workflow in Coder Workspace."""

    completed_episode_identifier = ''

    FILTER_TOGGLE_BUTTONS = [
        'svg:has(path[d^="M440-120"])',
        'path[d^="M440-120"]',
        '.workflow-coder-table-header span:has(svg)',
        '.workflow-coder-table-header button:has(svg)',
        'button:has-text("Filter")',
        '[aria-label*="Filter"]',
        '[title*="Filter"]',
    ]

    STATUS_FILTER_CARD = '.workflow-him-filter-card:has(label.workflow-him-filter-label:has-text("Status"))'
    STATUS_FILTER_CARD_ALTERNATES = [
        STATUS_FILTER_CARD,
        '.workflow-him-filter-card:has-text("Status")',
        '.workflow-filter-card:has-text("Status")',
        '.filter-card:has-text("Status")',
        'div:has(label:has-text("Status"))',
        'div:has-text("Status"):has(.react-select__control)',
        'div:has-text("Status"):has(input)',
    ]

    APPLY_FILTER_BUTTON = 'role=button[name="Apply"]'
    OUTSTANDING_EPISODE_ROW = (
        'tr:has-text("Outstanding"):not(:has-text("On Hold")), '
        'div:has-text("Outstanding"):not(:has-text("On Hold")), '
        '[role="row"]:has-text("Outstanding"):not(:has-text("On Hold"))'
    )

    CODE_ASSIST_BUTTON = 'button:has-text("Code Assist"), text=Code Assist'
    CODE_ASSIST_ICON = 'img[aria-label="Code Assist"], [aria-label="Code Assist"]'
    CANCEL_BUTTON = 'button:has-text("Cancel"), text=Cancel'
    PRINCIPAL_INPUT = 'input[name="principal"], input[placeholder*="principal"], [aria-label*="principal"]'
    ADDITIONAL_INPUT = 'input[name="additional"], input[placeholder*="additional"], [aria-label*="additional"]'
    PROCEDURE_INPUT = 'input[name="procedure"], input[placeholder*="procedure"], [aria-label*="procedure"]'
    CONFIRM_DRG_BUTTON = 'button:has-text("Confirm DRG"), button:has-text("Confirm DRGconfirm")'
    CODING_COMPLETE_BUTTON = 'button:has-text("Coding Complete"), text=Coding Complete'

    EPISODE_LIST_SELECTORS = [
        'tr[data-episode-id]',
        '.episode-row',
        'table tbody tr',
        '[data-testid*="episode-row"]',
        'div[role="row"]',
        '[role="row"]',
        'tbody tr',
        '.k-grid .k-grid-content tr',
        '.ag-center-cols-container .ag-row',
        '.rt-tr-group',
    ]

    def apply_outstanding_filter(self) -> bool:
        """Open filters, select Outstanding in Status dropdown, and apply."""
        for attempt in range(3):
            try:
                self.wait_for_loading_overlay(5000)

                if not self._open_filter_panel():
                    print('  ! Filter toggle not found')
                    continue

                self.page.wait_for_timeout(500)

                if not self._open_status_filter_dropdown():
                    print('  ! Status filter dropdown not found')
                    continue

                self.page.wait_for_timeout(300)

                if not self._select_status_outstanding_value():
                    print('  ! Outstanding option not found in Status dropdown')
                    continue

                self.page.wait_for_timeout(300)

                if not self._click_locator(self.APPLY_FILTER_BUTTON):
                    print('  ! Apply button not found')
                    continue

                self.page.wait_for_load_state('networkidle')
                self.page.wait_for_timeout(500)

                if self.wait_for_outstanding_episode_list(10000, require_outstanding=True):
                    print('  [OK] Outstanding Status filter applied')
                    return True

                print('  ! Outstanding episodes not visible after filter apply')
            except Exception as e:
                print(f'  ! Exception applying Outstanding Status filter: {e}')
                self._safe_wait(500)

        return False

    def _open_filter_panel(self) -> bool:
        """Click the table filter toggle before selecting Status."""
        if self._get_status_filter_card():
            return True

        for selector in self.FILTER_TOGGLE_BUTTONS:
            try:
                locator = self.page.locator(selector)
                for index in range(locator.count()):
                    target = locator.nth(index)
                    try:
                        if not target.is_visible():
                            continue

                        target.scroll_into_view_if_needed()
                        target.click(force=True)
                        self.page.wait_for_timeout(700)

                        if self._get_status_filter_card():
                            print('  [OK] Filter panel opened')
                            return True
                    except Exception:
                        continue
            except Exception:
                continue

        return False

    def _get_status_filter_card(self):
        """Return only the Status filter card, never Episode Identifier."""
        for selector in self.STATUS_FILTER_CARD_ALTERNATES:
            try:
                cards = self.page.locator(selector)
                for index in range(cards.count()):
                    card = cards.nth(index)
                    if not card.is_visible():
                        continue

                    text = card.inner_text(timeout=1000)
                    if 'Status' not in text:
                        continue
                    if 'Episode Identifier' in text and text.index('Episode Identifier') < text.index('Status'):
                        continue

                    return card
            except Exception:
                continue

        return None

    def _open_status_filter_dropdown(self) -> bool:
        """Open the Status dropdown only."""
        card = self._get_status_filter_card()
        if not card:
            print('  ! Status filter card not visible')
            return False

        selectors = [
            '.react-select__control',
            '.react-select__value-container',
            '.react-select__input-container',
            '[role="combobox"]',
            'input',
            'svg',
            'path',
            'button',
        ]

        for selector in selectors:
            try:
                target = card.locator(selector).first
                if target and target.is_visible():
                    target.scroll_into_view_if_needed()
                    target.click(force=True)
                    self.page.wait_for_timeout(400)
                    print('  [OK] Status dropdown opened')
                    return True
            except Exception:
                continue

        return False

    def _select_status_outstanding_value(self) -> bool:
        """Type/select Outstanding only from the opened Status dropdown."""
        card = self._get_status_filter_card()
        if not card:
            return False

        try:
            input_el = card.locator('input').first
            if input_el and input_el.is_visible():
                input_el.click(force=True)
                try:
                    input_el.fill('Outstanding')
                except Exception:
                    self.page.keyboard.type('Outstanding')
                self.page.wait_for_timeout(400)
        except Exception:
            pass

        option_selectors = [
            '[role="option"]:has-text("Outstanding")',
            '.react-select__option:has-text("Outstanding")',
            '.css-10wo9uf-option:has-text("Outstanding")',
            '.css-d7l1ni-option:has-text("Outstanding")',
            'div[id*="option"]:has-text("Outstanding")',
        ]

        for selector in option_selectors:
            try:
                options = self.page.locator(selector)
                for index in range(options.count()):
                    option = options.nth(index)
                    if option.is_visible():
                        option.scroll_into_view_if_needed()
                        option.click(force=True)
                        self.page.wait_for_timeout(300)
                        print('  [OK] Outstanding selected in Status dropdown')
                        return True
            except Exception:
                continue

        try:
            input_el = card.locator('input').first
            if input_el and input_el.is_visible():
                input_el.press('Enter')
                self.page.wait_for_timeout(300)
                print('  [OK] Outstanding selected by Enter in Status dropdown')
                return True
        except Exception:
            pass

        return False

    def wait_for_outstanding_episode_list(
        self,
        timeout: int = 15000,
        require_outstanding: bool = False,
    ) -> bool:
        """Wait for the episode list to load after filter is applied."""
        start = time.time()

        while time.time() - start < timeout / 1000:
            for selector in self.EPISODE_LIST_SELECTORS:
                try:
                    rows = self.page.locator(selector)
                    count = rows.count()
                    if count > 0:
                        if require_outstanding and not self._visible_rows_are_outstanding(rows):
                            continue
                        print(f'  [OK] Found {count} rows with selector: {selector}')
                        return True
                except Exception:
                    continue

            self._safe_wait(300)

        print('  ! Timeout waiting for episode list')
        return False

    def _visible_rows_are_outstanding(self, rows) -> bool:
        """Confirm at least one visible row has Outstanding status and no row has another status."""
        visible_count = 0
        outstanding_count = 0
        non_outstanding_statuses = [
            'On Hold',
            'For Review',
            'AI codes awaiting validation',
            'Completed',
            'Coding Completed',
        ]

        try:
            for index in range(rows.count()):
                row = rows.nth(index)
                if not row.is_visible():
                    continue

                visible_count += 1
                row_text = row.inner_text(timeout=1000)

                if 'Outstanding' in row_text:
                    outstanding_count += 1
                    continue

                if any(status in row_text for status in non_outstanding_statuses):
                    print(f'  ! Non-Outstanding row still visible: {row_text[:120]}')
                    return False

            return visible_count > 0 and outstanding_count > 0
        except Exception:
            return False

    def open_first_outstanding_episode(self) -> bool:
        """Open the first episode in the list after Outstanding filter is applied."""
        if not self.wait_for_outstanding_episode_list(require_outstanding=True):
            print('  ! No episode list found after filter')
            return False

        outstanding_selectors = [
            'tbody tr:has-text("Outstanding"):not(:has-text("On Hold"))',
            '[role="row"]:has-text("Outstanding"):not(:has-text("On Hold"))',
            'tr:has-text("Outstanding"):not(:has-text("On Hold"))',
        ]

        for selector in outstanding_selectors:
            try:
                rows = self.page.locator(selector)
                if rows.count() > 0:
                    row = rows.first
                    if row and row.is_visible():
                        self.completed_episode_identifier = self._get_episode_identifier_from_row(row)
                        if self._open_episode_row(row):
                            print(
                                '  [OK] Opened first Outstanding episode '
                                f'{self.completed_episode_identifier} using selector: {selector}'
                            )
                            return True
            except Exception as e:
                print(f'  ! Outstanding selector {selector} failed: {e}')

        return False

    def _open_episode_row(self, row) -> bool:
        """Open a row and verify the episode/module chooser is actually visible."""
        before_url = self.page.url
        click_targets = [
            row.locator('td').nth(1),
            row.locator('td').first,
            row,
        ]

        for target in click_targets:
            try:
                if target.count() == 0 or not target.is_visible():
                    continue

                target.scroll_into_view_if_needed()
                target.dblclick(force=True)
                if self._wait_for_episode_context(before_url):
                    return True
            except Exception:
                pass

            try:
                target.click(force=True)
                self._safe_wait(200)
                target.press('Enter')
                if self._wait_for_episode_context(before_url):
                    return True
            except Exception:
                pass

        print('  ! Outstanding episode row did not open after click')
        return False

    def _wait_for_episode_context(self, before_url: str, timeout: int = 10000) -> bool:
        """Wait until the grid click opens an episode detail or coding-module chooser."""
        start = time.time()
        selectors = [
            '.modal button:has-text("Code Assist")',
            '.modal button:has-text("Code Accelerate")',
            '[role="dialog"] button:has-text("Code Assist")',
            '[role="dialog"] button:has-text("Code Accelerate")',
            'div:has-text("Kindly select your desired coding module") button:has-text("Code Assist")',
            'div:has-text("Kindly select your desired coding module") button:has-text("Code Accelerate")',
            self.PRINCIPAL_INPUT,
            self.CONFIRM_DRG_BUTTON,
        ]

        while time.time() - start < timeout / 1000:
            try:
                self.wait_for_loading_overlay(1000)
            except Exception:
                pass

            for selector in selectors:
                try:
                    item = self.page.locator(selector).first
                    if item and item.is_visible():
                        return True
                except Exception:
                    continue

            if self.page.url != before_url:
                return True

            self._safe_wait(300)

        return False

    def _get_episode_identifier_from_row(self, row) -> str:
        """Read the Episode Identifier value from a table row before opening it."""
        try:
            cells = row.locator('td')
            if cells.count() > 1:
                episode_identifier = cells.nth(1).inner_text(timeout=1000).strip()
                if episode_identifier:
                    return episode_identifier
        except Exception:
            pass

        try:
            row_text = row.inner_text(timeout=1000).strip()
            if row_text:
                return row_text.splitlines()[0].strip()
        except Exception:
            pass

        return 'Unknown Episode'

    def open_code_assist(self) -> bool:
        self.wait_for_loading_overlay(8000)

        if self._coding_panel_is_ready('Code Assist'):
            return True

        candidates = [
            '.modal button:has-text("Code Assist")',
            '[role="dialog"] button:has-text("Code Assist")',
            'button:has-text("Code Assist")',
            '[aria-label="Code Assist"]',
            'button:has-text("Open Code Assist")',
            'a:has-text("Code Assist")',
            'role=button[name="Code Assist"]',
        ]

        for attempt in range(3):
            for selector in candidates:
                try:
                    if not self._click_locator(selector):
                        continue

                    self._safe_wait(800)

                    if self._coding_panel_is_ready('Code Assist'):
                        return True

                    self.close_popup_if_visible()
                except Exception:
                    continue

            self._safe_wait(500)

        return False

    def open_code_accelerate_panel(self) -> bool:
        """Select Code Accelerate from the coding-module popup after opening an episode."""
        self.wait_for_loading_overlay(8000)

        if self._coding_panel_is_ready('Code Accelerate'):
            return True

        candidates = [
            '.modal button:has-text("Code Accelerate")',
            '[role="dialog"] button:has-text("Code Accelerate")',
            'div:has-text("Kindly select your desired coding module") button:has-text("Code Accelerate")',
            'button:has-text("Code Accelerate")',
            '[aria-label="Code Accelerate"]',
            'role=button[name="Code Accelerate"]',
        ]

        for attempt in range(3):
            for selector in candidates:
                try:
                    if not self._click_locator(selector):
                        continue

                    self._safe_wait(800)

                    if self._coding_panel_is_ready('Code Accelerate'):
                        return True

                    self.close_popup_if_visible()
                except Exception:
                    continue

            self._safe_wait(500)

        return False

    def _coding_panel_is_ready(self, module_name: str | None = None, timeout: int = 3000) -> bool:
        """Detect the coding workspace even when code-entry rows are not input elements."""
        end_time = time.time() + timeout / 1000
        module_selectors = []
        if module_name:
            module_selectors = [
                f'.episode-header:has-text("{module_name}")',
                f'p:has-text("{module_name}")',
                f'nav:has-text("{module_name}")',
                f'text={module_name}',
            ]

        coding_surface_selectors = [
            self.PRINCIPAL_INPUT,
            self.CONFIRM_DRG_BUTTON,
            'text=Principal diagnosis',
            'text=Additional diagnoses',
            'text=Procedure codes',
            'text=Type code or drag and drop from Codebook',
        ]

        while time.time() < end_time:
            module_visible = True
            if module_selectors:
                module_visible = False
                for selector in module_selectors:
                    try:
                        item = self.page.locator(selector).first
                        if item and item.is_visible():
                            module_visible = True
                            break
                    except Exception:
                        continue

            if module_visible:
                for selector in coding_surface_selectors:
                    try:
                        item = self.page.locator(selector).first
                        if item and item.is_visible():
                            return True
                    except Exception:
                        continue

            self._safe_wait(250)

        return False

    def close_popup_if_visible(self) -> bool:
        for selector in [
            'button:has-text("Cancel")',
            'button[aria-label="close"]',
            '[aria-label="close"]',
            'button:has-text("Close")',
        ]:
            try:
                button = self.page.locator(selector).first
                if button and button.is_visible():
                    button.scroll_into_view_if_needed()
                    button.click(force=True)
                    self._safe_wait(500)
                    return True
            except Exception:
                continue

        try:
            button = self.page.get_by_role('button', name=re.compile(r'Cancel', re.I)).first
            if button.is_visible():
                button.scroll_into_view_if_needed()
                button.click()
                self._safe_wait(500)
                return True
        except Exception:
            pass

        return False

    def wait_for_loading_overlay(self, timeout: int = 10000) -> None:
        for selector in [
            'text=Loading preferences...',
            '.modal.show',
            '.modal-backdrop.show',
            '.MuiCircularProgress-root',
            '.spinner-border',
            '[role="progressbar"]',
        ]:
            try:
                self.page.wait_for_selector(selector, state='hidden', timeout=timeout)
            except Exception:
                pass

    def enter_principal_diagnosis(self, code: str) -> bool:
        return self._enter_code(self.PRINCIPAL_INPUT, code, 'Principal diagnosis')

    def enter_additional_diagnosis(self, code: str) -> bool:
        return self._enter_code(self.ADDITIONAL_INPUT, code, 'Additional diagnosis')

    def enter_procedure_code(self, code: str) -> bool:
        return self._enter_code(self.PROCEDURE_INPUT, code, 'Procedure code')

    def enter_coding_codes(
        self,
        principal_code: str,
        additional_codes: list[str],
        procedure_codes: list[str],
    ) -> bool:
        """Enter principal, additional diagnosis, and procedure codes."""
        if not self.enter_principal_diagnosis(principal_code):
            return False

        for code in additional_codes:
            if not self.enter_additional_diagnosis(code):
                print(f'  ! Failed to enter additional diagnosis: {code}')
                return False

        for code in procedure_codes:
            if not self.enter_procedure_code(code):
                print(f'  ! Failed to enter procedure code: {code}')
                return False

        return True

    def _enter_code(self, selector: str, code: str, label: str) -> bool:
        if not code:
            return False

        input_el = self._wait_for_enabled_input(selector, label)
        if not input_el:
            print(f'  ! {label} input was not enabled for code: {code}')
            return False

        for attempt in range(3):
            try:
                input_el.scroll_into_view_if_needed()
                input_el.click(force=True)
                input_el.fill(code)
                self._safe_wait(400)
                input_el.press('Enter')
                self._safe_wait(700)
                self.close_popup_if_visible()
                print(f'  [OK] {label} entered: {code}')
                return True
            except Exception:
                self._safe_wait(500)

        return False

    def _wait_for_enabled_input(self, selector: str, label: str, timeout: int = 60000):
        """Wait until a coding input is visible and enabled before typing."""
        start = time.time()

        while time.time() - start < timeout / 1000:
            self.wait_for_loading_overlay(1000)

            try:
                input_el = self.page.locator(selector).first
                if input_el and input_el.is_visible():
                    try:
                        if input_el.is_enabled():
                            return input_el
                    except Exception:
                        disabled = input_el.get_attribute('disabled', timeout=1000)
                        aria_disabled = input_el.get_attribute('aria-disabled', timeout=1000)
                        if disabled is None and aria_disabled != 'true':
                            return input_el
            except Exception:
                pass

            # The app often enables these fields only after Codebook finishes loading.
            self._safe_wait(1000)

        print(f'  ! Timeout waiting for {label} input to become enabled')
        return None

    def confirm_drg(self) -> bool:
        try:
            button = self.page.locator(self.CONFIRM_DRG_BUTTON).first
            if button and button.is_visible():
                button.scroll_into_view_if_needed()
                button.click()
                self.page.wait_for_load_state('networkidle')
                return self.wait_for_coding_complete_ready()
        except Exception:
            pass

        return False

    def wait_for_coding_complete_ready(self, timeout: int = 60000) -> bool:
        """Wait after Confirm DRG until Coding Complete is visible."""
        start = time.time()
        selectors = [
            'button:has-text("Coding Complete")',
            'text=Coding Complete',
            self.CODING_COMPLETE_BUTTON,
        ]

        while time.time() - start < timeout / 1000:
            self.wait_for_loading_overlay(1000)

            for selector in selectors:
                try:
                    buttons = self.page.locator(selector)
                    for index in range(buttons.count()):
                        button = buttons.nth(index)
                        if button.is_visible():
                            print('  [OK] Coding Complete button is ready')
                            return True
                except Exception:
                    continue

            self._safe_wait(1000)

        print('  ! Coding Complete button was not ready after Confirm DRG')
        return False

    def complete_coding(self) -> bool:
        if not self.wait_for_coding_complete_ready():
            return False

        if self._click_locator(self.CODING_COMPLETE_BUTTON, wait_for_load=True):
            if self.wait_for_coding_completed_status():
                self._print_coding_complete_status()
                return True

        try:
            my_actions = self.page.locator(
                'button:has-text("My Actions"), button[aria-label="My Actions"]'
            ).first

            if my_actions and my_actions.is_visible():
                my_actions.click()

                try:
                    self.page.wait_for_selector(
                        '.dropdown-menu, [role="menu"], .menu, .ant-dropdown',
                        timeout=2000,
                    )
                except Exception:
                    pass

                for selector in [
                    'text=Mark as Coding Complete',
                    'text=Coding Complete',
                    'text=Complete Coding',
                    'text=Complete',
                    'text=Finish Coding',
                    'text=Mark as Complete',
                ]:
                    try:
                        item = self.page.locator(selector).first
                        if item and item.is_visible():
                            item.click()
                            if self.wait_for_coding_completed_status():
                                self._print_coding_complete_status()
                                return True
                    except Exception:
                        continue
        except Exception:
            pass

        return False

    def wait_for_coding_completed_status(self, timeout: int = 90000) -> bool:
        """Wait after Coding Complete click until the UI shows completed status."""
        start = time.time()
        selectors = [
            'text=Coding Completed',
            'text=Coding Complete',
            'text=Completed',
            '[aria-label*="Coding Completed"]',
            '[aria-label*="Completed"]',
        ]

        while time.time() - start < timeout / 1000:
            self.wait_for_loading_overlay(1000)

            for selector in selectors:
                try:
                    items = self.page.locator(selector)
                    for index in range(items.count()):
                        item = items.nth(index)
                        if item.is_visible():
                            print('  [OK] Coding Complete status is visible')
                            return True
                except Exception:
                    continue

            try:
                confirm_button = self.page.locator(self.CONFIRM_DRG_BUTTON).first
                coding_button = self.page.locator(self.CODING_COMPLETE_BUTTON).first
                confirm_visible = confirm_button.is_visible() if confirm_button else False
                coding_visible = coding_button.is_visible() if coding_button else False

                if not confirm_visible and not coding_visible:
                    print('  [OK] Coding buttons disappeared after completion')
                    return True
            except Exception:
                pass

            self._safe_wait(1500)

        print('  ! Coding Complete status did not appear within timeout')
        return False

    def _print_coding_complete_status(self) -> None:
        episode_identifier = self.completed_episode_identifier or 'Unknown Episode'
        print(f'  [OK] Coding Complete status updated for Episode Identifier: {episode_identifier}')

    def _click_locator(self, selector: str, wait_for_load: bool = False) -> bool:
        try:
            locator = self.page.locator(selector)
            if locator.count() == 0:
                return False

            for index in range(locator.count()):
                target = locator.nth(index)
                try:
                    if target.is_visible():
                        target.scroll_into_view_if_needed()
                        target.click()
                        if wait_for_load:
                            self.page.wait_for_load_state('networkidle')
                        return True
                except Exception:
                    continue

            target = locator.first
            target.scroll_into_view_if_needed()
            target.click(force=True)

            if wait_for_load:
                self.page.wait_for_load_state('networkidle')

            return True
        except Exception:
            pass

        return False

    def _safe_wait(self, milliseconds: int) -> None:
        try:
            self.page.wait_for_timeout(milliseconds)
        except Exception:
            time.sleep(milliseconds / 1000)


if __name__ == '__main__':
    import traceback
    from playwright.sync_api import sync_playwright
    from pages.login_page import LoginPage
    from pages.unassignepisode_page import UnassignedEpisodePage
    from config.settings import Settings

    settings = Settings(env=os.getenv('ENV', 'dev'))
    base_url = settings.base_url
    headless = settings.headless
    headless_env = os.getenv('HEADLESS')
    if headless_env is not None:
        headless = headless_env.lower() in ('1', 'true', 'yes')

    exit_code = [0]

    with sync_playwright() as playwright:
        browser_type = getattr(playwright, settings.browser)
        browser = browser_type.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()

        try:
            login = LoginPage(page)
            nav = UnassignedEpisodePage(page)
            coding = CodingCompletePage(page)

            def fail_step(msg: str, exc: Exception | None = None):
                print(f'ERROR: {msg}')
                if exc:
                    traceback.print_exception(type(exc), exc, exc.__traceback__)

                ts = int(time.time())
                debug_dir = Path('reports/e2e/debug')
                debug_dir.mkdir(parents=True, exist_ok=True)
                screenshot_path = debug_dir / f'codingcomplete_failure_{ts}.png'
                html_path = debug_dir / f'codingcomplete_failure_{ts}.html'

                try:
                    page.screenshot(path=str(screenshot_path), full_page=True)
                    html_path.write_text(page.content(), encoding='utf-8')
                    print(f'Wrote debug files: {screenshot_path} {html_path}')
                except Exception:
                    pass

                exit_code[0] = 2

            print('Navigating to base URL...')
            page.goto(base_url)

            print('Performing login...')
            try:
                login.login(
                    os.getenv('IMEDX_USERNAME', 'Sai'),
                    os.getenv('IMEDX_PASSWORD', 'Imedx@123'),
                )
                login.verify_login_success()
                print('  [OK] Login successful')
            except Exception as e:
                fail_step('Login failed', e)
                raise

            def open_coder_workspace_from_base(reason: str):
                print(reason)
                try:
                    page.goto(base_url, wait_until='domcontentloaded')
                    try:
                        page.wait_for_load_state('networkidle', timeout=5000)
                    except Exception:
                        pass
                    opened = nav.open_code_workflow() or nav.open_him_workspace()
                    if not opened:
                        raise AssertionError('Could not open Code Workflow or HIM Workspace')
                    if not nav.open_coder_workspace():
                        raise AssertionError('Could not open Coder Workspace')
                    print('  [OK] Coder Workspace opened')
                except Exception as e:
                    fail_step('Navigation to Coder Workspace failed', e)
                    raise

            open_coder_workspace_from_base('Opening Code Workflow/Coder Workspace...')

            def run_coding_scenario(name: str, open_coding_panel=None):
                print(f'\nStarting {name} scenario...')

                print('Applying Outstanding Status filter...')
                try:
                    if not coding.apply_outstanding_filter():
                        raise AssertionError(
                            'Outstanding Status filter was not applied. '
                            'Stopping to avoid opening an unfiltered or wrong-status episode.'
                        )
                    print('  [OK] Outstanding Status filter applied')
                except Exception as e:
                    fail_step(f'Applying Outstanding Status filter failed for {name}', e)
                    raise

                print('Opening first outstanding episode...')
                try:
                    if not coding.open_first_outstanding_episode():
                        raise AssertionError('open_first_outstanding_episode returned False')
                    print('  [OK] Outstanding episode opened')
                except Exception as e:
                    fail_step(f'Opening outstanding episode failed for {name}', e)
                    raise

                if open_coding_panel:
                    print(f'Opening {name} coding panel...')
                    try:
                        if not open_coding_panel():
                            raise AssertionError(f'Opening {name} coding panel returned False')
                        coding.close_popup_if_visible()
                        print(f'  [OK] {name} coding panel opened')
                    except Exception as e:
                        fail_step(f'Opening {name} coding panel failed', e)
                        raise

                print('Entering principal, additional diagnosis, and procedure codes...')
                try:
                    if not coding.enter_coding_codes(
                        principal_code='Z51.1',
                        additional_codes=[
                            'M8010/3',
                            'J18.2',
                            'F44.4',
                            'F99',
                            'R10.4',
                            'R68.8',
                        ],
                        procedure_codes=[
                            '96199-00',
                        ],
                    ):
                        raise AssertionError('enter_coding_codes returned False')
                    print('  [OK] All requested diagnosis and procedure codes entered')
                except Exception as e:
                    fail_step(f'Entering diagnosis/procedure codes failed for {name}', e)
                    raise

                print('Confirming DRG...')
                try:
                    if not coding.confirm_drg():
                        raise AssertionError('confirm_drg returned False')
                    print('  [OK] DRG confirmed')
                except Exception as e:
                    fail_step(f'Confirm DRG failed for {name}', e)
                    raise

                print('Clicking Coding Complete...')
                try:
                    if not coding.complete_coding():
                        raise AssertionError('complete_coding returned False')
                    print('  [OK] Coding Complete clicked')
                except Exception as e:
                    fail_step(f'Clicking Coding Complete failed for {name}', e)
                    raise

                print(f'  [OK] {name} scenario completed')

            run_coding_scenario('Code Assist', coding.open_code_assist)

            open_coder_workspace_from_base(
                '\nReopening Code Workflow/Coder Workspace after Code Assist completion...'
            )

            run_coding_scenario('Code Accelerate', coding.open_code_accelerate_panel)

            print('\nDemo run finished')
        except Exception:
            if exit_code[0] == 0:
                exit_code[0] = 1
        finally:
            try:
                context.close()
                browser.close()
            except Exception:
                pass

    if exit_code[0] != 0:
        print(f'Exiting with code {exit_code[0]}')
        sys.exit(exit_code[0])
