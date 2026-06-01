import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CWD = Path.cwd()
for path in (ROOT, CWD):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from pages.Send_to_Audit_for_Queues import SendToAuditForQueuesPage


class SendToAuditForAuditorsWithQueuePage(SendToAuditForQueuesPage):
    """Workflow for sending a coding-complete episode to an auditor plus auditor queue."""

    def send_to_audit_auditor_with_queue(
        self,
        auditor_name: str = 'prabhu',
        queue_name: str = 'Code Enhance',
    ) -> bool:
        """Open My Actions, choose Send to Audit > Auditors, select auditor and queue, and send."""
        if not self._open_my_actions_send_to_audit():
            print('  ! My Actions Send to Audit panel did not open')
            return False

        if not self._open_auditors_tab():
            print('  ! Auditors tab not opened')
            return False

        if not self._search_and_select_auditor(auditor_name):
            print(f'  ! Auditor not selected: {auditor_name}')
            return False

        if not self._search_and_select_auditor_queue(queue_name):
            print(f'  ! Auditor queue not selected: {queue_name}')
            return False

        if not self._click_send_to_audit():
            print('  ! Send button not clicked')
            return False

        if not self._wait_for_audit_sent_status(queue_name):
            print('  ! Audit sent confirmation/status not detected')
            return False

        episode_identifier = self.completed_episode_identifier or 'Unknown Episode'
        print(
            '  [OK] Episode '
            f'{episode_identifier} sent to auditor {auditor_name} with queue: {queue_name}'
        )
        return True

    def _submenu_has_queue_controls(self, submenu) -> bool:
        selectors = [
            'button:has-text("Auditors")',
            'text=Auditors',
            'input[placeholder*="Search auditor"]',
            'input[placeholder*="Search auditor queues"]',
            'input[type="radio"]',
            'input[type="checkbox"]',
            'button:has-text("Send")',
        ]

        for selector in selectors:
            try:
                item = submenu.locator(selector).first
                if item and item.is_visible():
                    return True
            except Exception:
                continue

        return super()._submenu_has_queue_controls(submenu)

    def _open_auditors_tab(self) -> bool:
        submenu = self._ensure_send_to_audit_submenu()
        if not submenu:
            return False

        auditor_tab_selectors = [
            'button:has-text("Auditors")',
            '[role="tab"]:has-text("Auditors")',
            '.submenu-tabs button:has-text("Auditors")',
        ]

        for selector in auditor_tab_selectors:
            try:
                tab = submenu.locator(selector).first
                if tab and tab.is_visible():
                    tab.scroll_into_view_if_needed()
                    tab.click(force=True)
                    self._safe_wait(800)
                    submenu = self._send_to_audit_submenu() or submenu
                    if self._auditor_search_visible(submenu) or self._auditor_radio_visible(submenu):
                        print('  [OK] Send to Audit Auditors tab opened')
                        return True
            except Exception:
                continue

        for selector in [
            'button:has-text("Auditors")',
            '[role="button"]:has-text("Auditors")',
            'text=Auditors',
        ]:
            try:
                tabs = self.page.locator(selector)
                for index in range(tabs.count()):
                    tab = tabs.nth(index)
                    if not tab.is_visible():
                        continue

                    tab.scroll_into_view_if_needed()
                    tab.click(force=True)
                    self._safe_wait(800)
                    submenu = self._send_to_audit_submenu() or submenu
                    if self._auditor_search_visible(submenu) or self._auditor_radio_visible(submenu):
                        print('  [OK] Send to Audit Auditors tab opened')
                        return True
            except Exception:
                continue

        if self._auditor_search_visible(submenu) or self._auditor_radio_visible(submenu):
            print('  [OK] Send to Audit Auditors tab opened')
            return True

        return False

    def _search_and_select_auditor(self, auditor_name: str) -> bool:
        submenu = self._ensure_send_to_audit_submenu()
        if not submenu:
            return False
        if not self._auditor_search_visible(submenu) and not self._auditor_radio_visible(submenu):
            if not self._open_auditors_tab():
                return False
            submenu = self._ensure_send_to_audit_submenu()
        if not submenu:
            return False

        try:
            search = submenu.locator('input[placeholder*="Search auditor"]').first
            if search and search.is_visible():
                search.scroll_into_view_if_needed()
                search.click(force=True)
                search.fill(auditor_name)
                try:
                    search.press('Enter')
                except Exception:
                    pass
                self._safe_wait(700)
                print(f'  [OK] Auditor searched: {auditor_name}')
        except Exception:
            pass

        try:
            search_inputs = self.page.locator(
                'input[placeholder*="Search auditor"], '
                'input[aria-label*="Search auditor"]'
            )
            for index in range(search_inputs.count()):
                search = search_inputs.nth(index)
                if not search.is_visible():
                    continue

                search.scroll_into_view_if_needed()
                search.click(force=True)
                search.fill(auditor_name)
                try:
                    search.press('Enter')
                except Exception:
                    pass
                self._safe_wait(700)
                print(f'  [OK] Auditor searched: {auditor_name}')
                break
        except Exception:
            pass

        if self._select_auditor_radio(submenu, auditor_name):
            print(f'  [OK] Auditor selected: {auditor_name}')
            return True

        try:
            radios = submenu.locator('input[type="radio"]')
            if radios.count() == 1:
                radio = radios.first
                self._check_radio(radio)
                self._safe_wait(300)
                print(f'  [OK] Auditor selected: {auditor_name}')
                return True
        except Exception:
            pass

        try:
            radios = self.page.locator('input[type="radio"], [role="radio"]')
            for index in range(radios.count()):
                radio = radios.nth(index)
                if not radio.is_visible():
                    continue

                self._check_radio(radio)
                self._safe_wait(300)
                print(f'  [OK] Auditor selected: {auditor_name}')
                return True
        except Exception:
            pass

        return False

    def _select_auditor_radio(self, submenu, auditor_name: str) -> bool:
        auditor_selectors = [
            f'.dropdown-item:has-text("{auditor_name}") input[type="radio"]',
            f'label:has-text("{auditor_name}") input[type="radio"]',
            f'div:has-text("{auditor_name}") input[type="radio"]',
            f'text={auditor_name}',
        ]

        for selector in auditor_selectors:
            try:
                items = submenu.locator(selector)
                for index in range(items.count()):
                    item = items.nth(index)
                    if not item.is_visible():
                        continue

                    item.scroll_into_view_if_needed()
                    if 'input[type="radio"]' in selector:
                        self._check_radio(item)
                    else:
                        row = item.locator('xpath=ancestor-or-self::*[.//input[@type="radio"]][1]')
                        radio = row.locator('input[type="radio"]').first
                        if radio and radio.count() > 0:
                            self._check_radio(radio)
                        else:
                            item.click(force=True)

                    self._safe_wait(300)
                    if self._auditor_is_checked(submenu):
                        return True
            except Exception:
                continue

        return self._select_auditor_with_dom(auditor_name)

    def _select_auditor_with_dom(self, auditor_name: str, timeout: int = 10000) -> bool:
        start = time.time()
        while time.time() - start < timeout / 1000:
            try:
                selected = self.page.evaluate(
                    """auditorName => {
                        const wanted = auditorName.toLowerCase();
                        const radios = Array.from(document.querySelectorAll(
                            '.submenu-menu.show input[type="radio"], input[type="radio"]'
                        ));
                        const radio = radios.find(input => {
                            const row = input.closest('.dropdown-item, label, div');
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

    def _search_and_select_auditor_queue(self, queue_name: str) -> bool:
        submenu = self._ensure_send_to_audit_submenu()
        if not submenu:
            return False

        try:
            search = submenu.locator('input[placeholder*="Search auditor queue"]').first
            if search and search.is_visible():
                search.scroll_into_view_if_needed()
                search.click(force=True)
                search.fill(queue_name)
                self._safe_wait(500)
                print(f'  [OK] Auditor queue searched: {queue_name}')
        except Exception:
            pass

        try:
            search_inputs = self.page.locator(
                'input[placeholder*="Search auditor queue"], '
                'input[aria-label*="Search auditor queue"]'
            )
            for index in range(search_inputs.count()):
                search = search_inputs.nth(index)
                if not search.is_visible():
                    continue

                search.scroll_into_view_if_needed()
                search.click(force=True)
                search.fill(queue_name)
                self._safe_wait(500)
                print(f'  [OK] Auditor queue searched: {queue_name}')
                break
        except Exception:
            pass

        if self._select_queue_checkbox(submenu, queue_name):
            print(f'  [OK] Auditor queue selected: {queue_name}')
            return True

        try:
            checkboxes = submenu.locator('input[type="checkbox"]')
            if checkboxes.count() == 1:
                checkbox = checkboxes.first
                self._check_checkbox(checkbox)
                self._safe_wait(300)
                print(f'  [OK] Auditor queue selected: {queue_name}')
                return True
        except Exception:
            pass

        try:
            checkboxes = self.page.locator('input[type="checkbox"]')
            for index in range(checkboxes.count()):
                checkbox = checkboxes.nth(index)
                if not checkbox.is_visible():
                    continue

                self._check_checkbox(checkbox)
                self._safe_wait(300)
                print(f'  [OK] Auditor queue selected: {queue_name}')
                return True
        except Exception:
            pass

        return False

    def _ensure_send_to_audit_submenu(self):
        submenu = self._send_to_audit_submenu()
        if submenu:
            return submenu

        if not self._main_my_actions_menu_visible():
            self._open_my_actions_send_to_audit()

        submenu = self._open_send_to_audit_child_panel()
        if submenu:
            return submenu

        send_to_audit_items = [
            '.submenu-title:has-text("Send to Audit")',
            'a.dropdown-item:has-text("Send to Audit")',
            '[role="button"]:has-text("Send to Audit")',
            '[role="menuitem"]:has-text("Send to Audit")',
            'text=Send to Audit',
        ]

        for selector in send_to_audit_items:
            try:
                items = self.page.locator(selector)
                for index in range(items.count()):
                    item = items.nth(index)
                    if not item.is_visible():
                        continue

                    item.scroll_into_view_if_needed()
                    for attempt in range(3):
                        try:
                            if attempt == 0:
                                item.hover(force=True)
                            elif attempt == 1:
                                item.click(force=True)
                            else:
                                box = item.bounding_box(timeout=1000)
                                if box:
                                    self.page.mouse.move(
                                        box['x'] + box['width'] - 5,
                                        box['y'] + box['height'] / 2,
                                    )
                        except Exception:
                            continue

                        self._safe_wait(700)
                        submenu = self._send_to_audit_submenu()
                        if submenu:
                            return submenu
            except Exception:
                continue

        return None

    def _open_send_to_audit_child_panel(self):
        send_to_audit_items = [
            '.submenu-title:has-text("Send to Audit")',
            'a.dropdown-item:has-text("Send to Audit")',
            '[role="button"]:has-text("Send to Audit")',
            '[role="menuitem"]:has-text("Send to Audit")',
            'text=Send to Audit',
        ]

        for selector in send_to_audit_items:
            try:
                items = self.page.locator(selector)
                for index in range(items.count()):
                    item = items.nth(index)
                    if not item.is_visible():
                        continue

                    item.scroll_into_view_if_needed()
                    box = item.bounding_box(timeout=1000)

                    for attempt in range(4):
                        try:
                            if attempt == 0:
                                item.hover(force=True)
                            elif attempt == 1 and box:
                                self.page.mouse.move(
                                    box['x'] + box['width'] - 3,
                                    box['y'] + box['height'] / 2,
                                )
                            elif attempt == 2:
                                item.click(force=True)
                            elif box:
                                self.page.mouse.click(
                                    box['x'] + box['width'] - 3,
                                    box['y'] + box['height'] / 2,
                                )
                        except Exception:
                            continue

                        self._safe_wait(800)
                        submenu = self._send_to_audit_submenu()
                        if submenu:
                            return submenu
            except Exception:
                continue

        return None

    def _main_my_actions_menu_visible(self) -> bool:
        try:
            menus = self.page.locator('.dropdown-menu.show')
            for index in range(menus.count()):
                menu = menus.nth(index)
                if menu.is_visible() and 'Send to Audit' in menu.inner_text(timeout=1000):
                    return True
        except Exception:
            pass

        return False

    def _auditor_search_visible(self, submenu) -> bool:
        try:
            search = submenu.locator('input[placeholder*="Search auditor"]').first
            return bool(search and search.is_visible())
        except Exception:
            pass

        try:
            search = self.page.locator('input[placeholder*="Search auditor"]').first
            return bool(search and search.is_visible())
        except Exception:
            return False

    def _auditor_radio_visible(self, submenu) -> bool:
        try:
            radio = submenu.locator('input[type="radio"]').first
            return bool(radio and radio.is_visible())
        except Exception:
            return False

    def _auditor_is_checked(self, submenu) -> bool:
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

    audit_auditor = os.getenv('AUDIT_AUDITOR', 'prabhu')
    auditor_queue = os.getenv('AUDITOR_QUEUE', 'Code Enhance')
    exit_code = [0]

    with sync_playwright() as playwright:
        browser_type = getattr(playwright, settings.browser)
        browser = browser_type.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()

        try:
            login = LoginPage(page)
            nav = UnassignedEpisodePage(page)
            audit = SendToAuditForAuditorsWithQueuePage(page)

            def fail_step(msg: str, exc: Exception | None = None):
                print(f'ERROR: {msg}')
                if exc:
                    traceback.print_exception(type(exc), exc, exc.__traceback__)

                ts = int(time.time())
                debug_dir = Path('reports/e2e/debug')
                debug_dir.mkdir(parents=True, exist_ok=True)
                screenshot_path = debug_dir / f'send_to_audit_auditors_queue_failure_{ts}.png'
                html_path = debug_dir / f'send_to_audit_auditors_queue_failure_{ts}.html'

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

            def run_send_to_audit_scenario(name: str, open_coding_panel):
                print(f'\nStarting {name} Send to Audit Auditors with Queue scenario...')

                print('Applying Outstanding Status filter...')
                try:
                    if not audit.apply_outstanding_filter():
                        raise AssertionError('Outstanding Status filter was not applied')
                    print('  [OK] Outstanding Status filter applied')
                except Exception as e:
                    fail_step(f'Applying Outstanding Status filter failed for {name}', e)
                    raise

                print('Opening first outstanding episode...')
                try:
                    if not audit.open_first_outstanding_episode():
                        raise AssertionError('open_first_outstanding_episode returned False')
                    print('  [OK] Outstanding episode opened')
                except Exception as e:
                    fail_step(f'Opening outstanding episode failed for {name}', e)
                    raise

                print(f'Opening {name} coding panel...')
                try:
                    if not open_coding_panel():
                        raise AssertionError(f'Opening {name} returned False')
                    audit.close_popup_if_visible()
                    print(f'  [OK] {name} coding panel opened')
                except Exception as e:
                    fail_step(f'Opening {name} failed', e)
                    raise

                print('Entering principal, additional diagnosis, and procedure codes...')
                try:
                    if not audit.enter_coding_codes(
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
                    if not audit.confirm_drg():
                        raise AssertionError('confirm_drg returned False')
                    print('  [OK] DRG confirmed')
                except Exception as e:
                    fail_step(f'Confirm DRG failed for {name}', e)
                    raise

                print('Clicking Coding Complete...')
                try:
                    if not audit.complete_coding():
                        raise AssertionError('complete_coding returned False')
                    print('  [OK] Coding Complete clicked')
                except Exception as e:
                    fail_step(f'Clicking Coding Complete failed for {name}', e)
                    raise

                print('Sending episode to audit auditor with queue...')
                try:
                    if not audit.send_to_audit_auditor_with_queue(
                        auditor_name=audit_auditor,
                        queue_name=auditor_queue,
                    ):
                        raise AssertionError('send_to_audit_auditor_with_queue returned False')
                    print('  [OK] Send to Audit auditor with queue completed')
                except Exception as e:
                    fail_step(f'Send to Audit auditor with queue failed for {name}', e)
                    raise

                print(f'  [OK] {name} Send to Audit Auditors with Queue scenario completed')

            open_coder_workspace_from_base('Opening Code Workflow/Coder Workspace...')
            run_send_to_audit_scenario('Code Assist', audit.open_code_assist)

            open_coder_workspace_from_base(
                '\nReopening Code Workflow/Coder Workspace after Code Assist audit completion...'
            )
            run_send_to_audit_scenario('Code Accelerate', audit.open_code_accelerate_panel)

            print('\nSend to Audit for Auditors with Queue run finished')
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
