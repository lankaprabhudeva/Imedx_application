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

from pages.codingcomplete import CodingCompletePage


class ForReviewSendToAuditorPage(CodingCompletePage):
    """Workflow for sending an Outstanding episode to an auditor for review."""

    MY_ACTIONS_BUTTON = 'button:has-text("My Actions"), button[aria-label="My Actions"]'
    AUDITOR_SEARCH_INPUTS = [
        'input[placeholder="Search auditors..."]',
        'input[placeholder*="Search auditors"]',
        'input[aria-label*="Search auditors"]',
        'role=textbox[name="Search auditors..."]',
    ]
    AUDITOR_RADIO = 'input[type="radio"], [role="radio"]'
    REVIEW_REASON_INPUTS = [
        'textarea[placeholder*="Enter reason for review"]',
        'input[placeholder*="Enter reason for review"]',
        '[aria-label*="Enter reason for review"]',
        'role=textbox[name="Enter reason for review..."]',
    ]
    SEND_BUTTONS = [
        'button:has-text("Send")',
        'role=button[name="Send"]',
    ]
    FOR_REVIEW_SUBMENU = (
        '.dropdown-submenu-myactions:has(a.submenu-title:has-text("For Review")) '
        '> .submenu-menu.dropdown-menu.show'
    )

    def send_for_review_to_auditor(
        self,
        auditor_name: str = 'Prabhu',
        reason: str = 'Sai auditor sends this episode to PRABHU AUDITOR',
    ) -> bool:
        """Open My Actions, choose Auditor, add reason, and send for review."""
        if not self._open_my_actions_for_review():
            print('  ! My Actions review panel did not open')
            return False

        if not self._search_and_select_auditor(auditor_name):
            print(f'  ! Auditor not selected: {auditor_name}')
            return False

        if not self._enter_review_reason(reason):
            print('  ! Review reason not entered')
            return False

        if not self._click_send_review():
            print('  ! Send button not clicked')
            return False

        if not self._wait_for_review_sent_status(auditor_name):
            print('  ! Review sent confirmation/status not detected')
            return False

        episode_identifier = self.completed_episode_identifier or 'Unknown Episode'
        print(f'  [OK] Episode {episode_identifier} sent for review to Auditor: {auditor_name}')
        return True

    def _open_my_actions_for_review(self) -> bool:
        for attempt in range(3):
            try:
                button = self.page.locator(self.MY_ACTIONS_BUTTON).first
                if button and button.is_visible():
                    button.scroll_into_view_if_needed()
                    button.click(force=True)
                    self._safe_wait(700)

                    if self._select_for_review_action():
                        print('  [OK] My Actions review panel opened')
                        return True

                    if self._review_panel_is_visible():
                        print('  [OK] My Actions review panel opened')
                        return True
            except Exception:
                pass

            self._safe_wait(500)

        return False

    def _select_for_review_action(self) -> bool:
        """Select For Review from the My Actions dropdown, including submenu variants."""
        if self._for_review_submenu_is_visible() and self._visible_auditor_search():
            return True

        review_selectors = [
            '.submenu-title:has-text("For Review")',
            'a.dropdown-item:has-text("For Review")',
            '[role="button"]:has-text("For Review")',
            '[role="menuitem"]:has-text("For Review")',
        ]

        for selector in review_selectors:
            try:
                items = self.page.locator(selector)
                for index in range(items.count()):
                    item = items.nth(index)
                    if not item.is_visible():
                        continue

                    item.scroll_into_view_if_needed()
                    try:
                        item.hover()
                    except Exception:
                        pass
                    self._safe_wait(400)

                    if self._for_review_submenu_is_visible() and self._visible_auditor_search():
                        return True

                    if self._click_review_submenu_item():
                        return True

                    try:
                        item.click(force=True)
                    except Exception:
                        pass
                    self._safe_wait(700)

                    if self._for_review_submenu_is_visible() and self._visible_auditor_search():
                        return True

                    if self._click_review_submenu_item():
                        return True
            except Exception:
                continue

        return False

    def _click_review_submenu_item(self) -> bool:
        """Click the submenu action that opens the send-for-review form."""
        submenu_selectors = [
            'text=Send to Auditor',
            'text=Send To Auditor',
            'text=Send to Auditor',
            'text=Send for Review',
            'text=Send For Review',
            '.submenu-tabs button:has-text("Auditors")',
            '[role="menuitem"]:has-text("Auditors")',
        ]

        for selector in submenu_selectors:
            try:
                items = self.page.locator(selector)
                for index in range(items.count()):
                    item = items.nth(index)
                    if not item.is_visible():
                        continue

                    item.scroll_into_view_if_needed()
                    item.click(force=True)
                    self._safe_wait(700)

                    if self._for_review_submenu_is_visible() and self._visible_auditor_search():
                        return True

                    if self._review_panel_is_visible():
                        return True
            except Exception:
                continue

        return False

    def _review_panel_is_visible(self) -> bool:
        if self._visible_auditor_search():
            return True

        if self._for_review_submenu_is_visible() and self._visible_auditor_search():
            return True

        selectors = [
            'text=Search auditors',
            'text=Enter reason for review',
        ]
        selectors.extend(self.AUDITOR_SEARCH_INPUTS)
        selectors.extend(self.REVIEW_REASON_INPUTS)

        for selector in selectors:
            try:
                locator = self.page.locator(selector).first
                if locator and locator.is_visible():
                    return True
            except Exception:
                continue

        return False

    def _visible_auditor_search(self) -> bool:
        return bool(self._visible_for_review_submenu())

    def _visible_for_review_submenu(self):
        try:
            submenus = self.page.locator(self.FOR_REVIEW_SUBMENU)
            for index in range(submenus.count()):
                submenu = submenus.nth(index)
                try:
                    search = submenu.locator('input.submenu-search-input[placeholder*="Search auditors"]').first
                    box = search.bounding_box(timeout=1000)
                    if search.is_visible() and box and box.get('width', 0) > 0 and box.get('height', 0) > 0:
                        return submenu
                except Exception:
                    continue
        except Exception:
            pass

        return None

    def _for_review_submenu_is_visible(self) -> bool:
        return bool(self._visible_for_review_submenu())

    def _for_review_submenu(self):
        return self._visible_for_review_submenu()

    def _search_and_select_auditor(self, auditor_name: str) -> bool:
        submenu = self._for_review_submenu()
        search = None

        if submenu:
            try:
                search = submenu.locator('input.submenu-search-input[placeholder*="Search auditors"]').first
                if not search.is_visible():
                    search = None
            except Exception:
                search = None

        if not search:
            try:
                search_inputs = self.page.locator('input.submenu-search-input[placeholder*="Search auditors"]')
                for index in range(search_inputs.count()):
                    candidate = search_inputs.nth(index)
                    box = candidate.bounding_box(timeout=500)
                    if candidate.is_visible() and box and box.get('width', 0) > 0 and box.get('height', 0) > 0:
                        search = candidate
                        break
            except Exception:
                search = None

        if search:
            try:
                search.scroll_into_view_if_needed()
                search.click(force=True)
                search.fill(auditor_name.lower())
                self._safe_wait(700)
                print(f'  [OK] Auditor searched: {auditor_name.lower()}')
            except Exception:
                pass

        submenu = self._for_review_submenu() or submenu

        if submenu:
            try:
                rows = submenu.locator('.dropdown-item')
                for index in range(rows.count()):
                    row = rows.nth(index)
                    try:
                        row_text = row.inner_text(timeout=1000)
                    except Exception:
                        continue
                    if auditor_name.lower() not in row_text.lower():
                        continue

                    radio = row.locator('input[type="radio"], [role="radio"]').first
                    if radio and radio.count() > 0:
                        self._check_radio(radio)
                    else:
                        row.click(force=True)

                    self._safe_wait(300)
                    if not self._radio_is_checked(submenu):
                        continue
                    print(f'  [OK] Auditor selected: {auditor_name}')
                    self._wait_for_review_reason_input()
                    return True
            except Exception:
                pass

            try:
                radios = submenu.locator('input[type="radio"], [role="radio"]')
                if radios.count() == 1:
                    radio = radios.first
                    self._check_radio(radio)
                    self._safe_wait(300)
                    if not self._radio_is_checked(submenu):
                        return False
                    print(f'  [OK] Auditor selected: {auditor_name}')
                    self._wait_for_review_reason_input()
                    return True
            except Exception:
                pass

        if self._select_auditor_radio_with_dom(auditor_name, timeout=10000):
            self._safe_wait(300)
            print(f'  [OK] Auditor selected: {auditor_name}')
            self._wait_for_review_reason_input()
            return True

        auditor_selectors = [
            f'label:has-text("{auditor_name}") input[type="radio"]',
            f'.dropdown-item:has-text("{auditor_name}") input[type="radio"]',
            f'[role="radio"]:has-text("{auditor_name}")',
        ]

        for selector in auditor_selectors:
            try:
                radios = self.page.locator(selector)
                for index in range(radios.count()):
                    radio = radios.nth(index)
                    if not radio.is_visible():
                        continue

                    radio.scroll_into_view_if_needed()
                    try:
                        self._check_radio(radio)
                    except Exception:
                        radio.click(force=True)
                    self._safe_wait(300)
                    print(f'  [OK] Auditor selected: {auditor_name}')
                    self._wait_for_review_reason_input()
                    return True
            except Exception:
                continue

        return False

    def _select_auditor_radio_with_dom(self, auditor_name: str, timeout: int = 10000) -> bool:
        start = time.time()
        while time.time() - start < timeout / 1000:
            try:
                selected = self.page.evaluate(
                    """auditorName => {
                        const wanted = auditorName.toLowerCase();
                        const radios = Array.from(document.querySelectorAll(
                            '.submenu-menu.show input[type="radio"][name="user"], input[type="radio"][name="user"]'
                        ));
                        const radio = radios.find(input => {
                            const row = input.closest('.dropdown-item') || input.parentElement;
                            return row && row.textContent.toLowerCase().includes(wanted);
                        }) || (radios.length === 1 ? radios[0] : null);
                        if (!radio) return false;

                        radio.scrollIntoView({ block: 'center', inline: 'center' });
                        radio.click();

                        const setter = Object.getOwnPropertyDescriptor(
                            HTMLInputElement.prototype,
                            'checked'
                        ).set;
                        setter.call(radio, true);
                        radio.dispatchEvent(new MouseEvent('click', { bubbles: true }));
                        radio.dispatchEvent(new Event('input', { bubbles: true }));
                        radio.dispatchEvent(new Event('change', { bubbles: true }));
                        return radio.checked;
                    }""",
                    auditor_name,
                )
                if selected:
                    return True
            except Exception:
                pass

            self._safe_wait(300)

        return False

    def _radio_is_checked(self, submenu) -> bool:
        try:
            return bool(submenu.locator('input[type="radio"]:checked').count())
        except Exception:
            return False

    def _check_radio(self, radio) -> None:
        try:
            radio.scroll_into_view_if_needed(timeout=1000)
            radio.check(force=True, timeout=2000)
            return
        except Exception:
            pass

        try:
            radio.click(force=True, timeout=2000)
            return
        except Exception:
            pass

        radio.evaluate(
            """element => {
                element.click();
                element.checked = true;
                element.dispatchEvent(new Event('input', { bubbles: true }));
                element.dispatchEvent(new Event('change', { bubbles: true }));
            }"""
        )

    def _enter_review_reason(self, reason: str) -> bool:
        reason_input = self._wait_for_review_reason_input()
        if not reason_input:
            return False

        try:
            reason_input.scroll_into_view_if_needed()
            reason_input.click(force=True)
            reason_input.fill(reason)
            self._safe_wait(300)
            print('  [OK] Review reason entered')
            return True
        except Exception:
            pass

        return False

    def _wait_for_review_reason_input(self, timeout: int = 10000):
        start = time.time()
        while time.time() - start < timeout / 1000:
            submenu = self._for_review_submenu()
            if submenu:
                try:
                    reason_input = submenu.locator(
                        'textarea[placeholder*="Enter reason for review"], '
                        'input[placeholder*="Enter reason for review"]'
                    ).first
                    if reason_input and reason_input.is_visible():
                        return reason_input
                except Exception:
                    pass

                for selector in self.REVIEW_REASON_INPUTS:
                    try:
                        reason_input = submenu.locator(selector).first
                        if reason_input and reason_input.is_visible():
                            return reason_input
                    except Exception:
                        continue

            reason_input = self._first_visible_locator(self.REVIEW_REASON_INPUTS)
            if reason_input:
                return reason_input

            self._safe_wait(300)

        return None

    def _click_send_review(self) -> bool:
        button = None
        submenu = self._for_review_submenu()

        if submenu:
            try:
                buttons = submenu.locator('button.send-to-review-btn, button:has-text("Send")')
                for index in range(buttons.count()):
                    candidate = buttons.nth(index)
                    if candidate.is_visible() and candidate.is_enabled():
                        button = candidate
                        break
            except Exception:
                button = None

        if not button:
            button = self._first_visible_locator(self.SEND_BUTTONS)

        if not button:
            return False

        try:
            button.scroll_into_view_if_needed()
            button.click(force=True)
            self._safe_wait(1000)
            print('  [OK] Send clicked')
            return True
        except Exception:
            pass

        return False

    def _first_visible_locator(self, selectors: list[str]):
        for selector in selectors:
            try:
                locator = self.page.locator(selector)
                for index in range(locator.count()):
                    item = locator.nth(index)
                    if item.is_visible():
                        return item
            except Exception:
                continue

        return None

    def _wait_for_review_sent_status(self, auditor_name: str, timeout: int = 60000) -> bool:
        start = time.time()
        success_selectors = [
            '.episode-container [aria-label*="Audit - For Review"]',
            '.episode-container .info-value:has-text("Audit - For Review")',
            '.epsoide-status-card [aria-label*="Audit - For Review"]',
            '.epsoide-status-card .info-value:has-text("Audit - For Review")',
            '.my-actions-div:has-text("Audit - For Review")',
            'text=Audit - For Review',
            '.episode-container [aria-label="For Review"]',
            '.episode-container .info-value:has-text("For Review")',
            '.epsoide-status-card [aria-label="For Review"]',
            '.epsoide-status-card .info-value:has-text("For Review")',
        ]

        while time.time() - start < timeout / 1000:
            self.wait_for_loading_overlay(1000)

            for selector in success_selectors:
                try:
                    locator = self.page.locator(selector)
                    for index in range(locator.count()):
                        item = locator.nth(index)
                        if item.is_visible():
                            print('  [OK] Review sent status detected')
                            return True
                except Exception:
                    continue

            self._safe_wait(1000)

        return False


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
            review = ForReviewSendToAuditorPage(page)

            def fail_step(msg: str, exc: Exception | None = None):
                print(f'ERROR: {msg}')
                if exc:
                    traceback.print_exception(type(exc), exc, exc.__traceback__)

                ts = int(time.time())
                debug_dir = Path('reports/e2e/debug')
                debug_dir.mkdir(parents=True, exist_ok=True)
                screenshot_path = debug_dir / f'for_review_sendtoauditor_failure_{ts}.png'
                html_path = debug_dir / f'for_review_sendtoauditor_failure_{ts}.html'

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

            print('Opening Code Workflow/Coder Workspace...')
            try:
                opened = nav.open_code_workflow() or nav.open_him_workspace()
                if not opened:
                    raise AssertionError('Could not open Code Workflow or HIM Workspace')
                if not nav.open_coder_workspace():
                    raise AssertionError('Could not open Coder Workspace')
                print('  [OK] Coder Workspace opened')
            except Exception as e:
                fail_step('Navigation to Coder Workspace failed', e)
                raise

            print('Applying Outstanding Status filter...')
            try:
                if not review.apply_outstanding_filter():
                    raise AssertionError('Outstanding Status filter was not applied')
                print('  [OK] Outstanding Status filter applied')
            except Exception as e:
                fail_step('Applying Outstanding Status filter failed', e)
                raise

            print('Opening first outstanding episode...')
            try:
                if not review.open_first_outstanding_episode():
                    raise AssertionError('open_first_outstanding_episode returned False')
                print('  [OK] Outstanding episode opened')
            except Exception as e:
                fail_step('Opening outstanding episode failed', e)
                raise

            print('Opening Code Assist...')
            try:
                if not review.open_code_assist():
                    raise AssertionError('open_code_assist returned False')
                review.close_popup_if_visible()
                print('  [OK] Code Assist opened')
            except Exception as e:
                fail_step('Opening Code Assist failed', e)
                raise

            print('Entering principal, additional diagnosis, and procedure codes...')
            try:
                if not review.enter_coding_codes(
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
                fail_step('Entering diagnosis/procedure codes failed', e)
                raise

            print('Confirming DRG...')
            try:
                if not review.confirm_drg():
                    raise AssertionError('confirm_drg returned False')
                print('  [OK] DRG confirmed')
            except Exception as e:
                fail_step('Confirm DRG failed', e)
                raise

            print('Sending episode for review to auditor...')
            try:
                if not review.send_for_review_to_auditor(
                    auditor_name='Prabhu',
                    reason='Sai auditor sends this episode to PRABHU AUDITOR',
                ):
                    raise AssertionError('send_for_review_to_auditor returned False')
                print('  [OK] Send for review completed')
            except Exception as e:
                fail_step('Send for review failed', e)
                raise

            print('\nFor Review Send to Auditor run finished')
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


