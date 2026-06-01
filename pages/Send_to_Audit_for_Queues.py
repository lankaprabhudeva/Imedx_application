import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CWD = Path.cwd()
for path in (ROOT, CWD):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from pages.codingcomplete import CodingCompletePage


class SendToAuditForQueuesPage(CodingCompletePage):
    """Workflow for sending a coding-complete episode to an audit queue."""

    MY_ACTIONS_BUTTON = 'button:has-text("My Actions"), button[aria-label="My Actions"]'
    SEND_TO_AUDIT_SUBMENU = (
        '.dropdown-submenu-myactions:has(a.submenu-title:has-text("Send to Audit")) '
        '> .submenu-menu.dropdown-menu.show'
    )

    def send_to_audit_queue(self, queue_name: str = 'Code Enhance') -> bool:
        """Open My Actions, choose Send to Audit > Queues, select queue, and send."""
        if not self._open_my_actions_send_to_audit():
            print('  ! My Actions Send to Audit panel did not open')
            return False

        if not self._open_queues_tab():
            print('  ! Queues tab not opened')
            return False

        if not self._search_and_select_queue(queue_name):
            print(f'  ! Audit queue not selected: {queue_name}')
            return False

        if not self._click_send_to_audit():
            print('  ! Send button not clicked')
            return False

        if not self._wait_for_audit_sent_status(queue_name):
            print('  ! Audit sent confirmation/status not detected')
            return False

        episode_identifier = self.completed_episode_identifier or 'Unknown Episode'
        print(f'  [OK] Episode {episode_identifier} sent to audit queue: {queue_name}')
        return True

    def _open_my_actions_send_to_audit(self) -> bool:
        for attempt in range(3):
            try:
                button = self.page.locator(self.MY_ACTIONS_BUTTON).first
                if button and button.is_visible():
                    button.scroll_into_view_if_needed()
                    button.click(force=True)
                    self._safe_wait(700)

                    if self._select_send_to_audit_action():
                        print('  [OK] My Actions Send to Audit panel opened')
                        return True

                    if self._send_to_audit_panel_is_visible():
                        print('  [OK] My Actions Send to Audit panel opened')
                        return True
            except Exception:
                pass

            self._safe_wait(500)

        return False

    def _select_send_to_audit_action(self) -> bool:
        if self._send_to_audit_panel_is_visible():
            return True

        audit_selectors = [
            '.submenu-title:has-text("Send to Audit")',
            'a.dropdown-item:has-text("Send to Audit")',
            '[role="button"]:has-text("Send to Audit")',
            '[role="menuitem"]:has-text("Send to Audit")',
            'text=Send to Audit',
        ]

        for selector in audit_selectors:
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

                    if self._send_to_audit_panel_is_visible():
                        return True

                    try:
                        item.click(force=True)
                    except Exception:
                        pass
                    self._safe_wait(700)

                    if self._send_to_audit_panel_is_visible():
                        return True
            except Exception:
                continue

        return False

    def _send_to_audit_panel_is_visible(self) -> bool:
        return bool(self._send_to_audit_submenu())

    def _send_to_audit_submenu(self):
        try:
            submenus = self.page.locator(self.SEND_TO_AUDIT_SUBMENU)
            for index in range(submenus.count()):
                submenu = submenus.nth(index)
                if not submenu.is_visible():
                    continue

                if self._submenu_has_queue_controls(submenu):
                    return submenu
        except Exception:
            pass

        try:
            panels = self.page.locator(
                '.submenu-menu.dropdown-menu.show:has-text("Queues"), '
                '.dropdown-menu.show:has-text("Queues")'
            )
            for index in range(panels.count()):
                panel = panels.nth(index)
                if panel.is_visible() and self._submenu_has_queue_controls(panel):
                    return panel
        except Exception:
            pass

        return None

    def _submenu_has_queue_controls(self, submenu) -> bool:
        selectors = [
            'button:has-text("Queues")',
            'text=Queues',
            'input[placeholder*="Search queues"]',
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

        return False

    def _open_queues_tab(self) -> bool:
        submenu = self._send_to_audit_submenu()
        if not submenu:
            return False

        queue_tab_selectors = [
            'button:has-text("Queues")',
            '[role="tab"]:has-text("Queues")',
            '.submenu-tabs button:has-text("Queues")',
            'text=Queues',
        ]

        for selector in queue_tab_selectors:
            try:
                tab = submenu.locator(selector).first
                if tab and tab.is_visible():
                    tab.scroll_into_view_if_needed()
                    tab.click(force=True)
                    self._safe_wait(500)
                    print('  [OK] Send to Audit Queues tab opened')
                    return True
            except Exception:
                continue

        return self._queue_checkbox_visible(submenu)

    def _search_and_select_queue(self, queue_name: str) -> bool:
        submenu = self._send_to_audit_submenu()
        if not submenu:
            return False

        try:
            search = submenu.locator('input[placeholder*="Search queues"]').first
            if search and search.is_visible():
                search.scroll_into_view_if_needed()
                search.click(force=True)
                search.fill(queue_name)
                self._safe_wait(500)
                print(f'  [OK] Audit queue searched: {queue_name}')
        except Exception:
            pass

        if self._select_queue_checkbox(submenu, queue_name):
            print(f'  [OK] Audit queue selected: {queue_name}')
            return True

        try:
            checkboxes = submenu.locator('input[type="checkbox"]')
            if checkboxes.count() == 1:
                checkbox = checkboxes.first
                self._check_checkbox(checkbox)
                self._safe_wait(300)
                print(f'  [OK] Audit queue selected: {queue_name}')
                return True
        except Exception:
            pass

        return False

    def _select_queue_checkbox(self, submenu, queue_name: str) -> bool:
        queue_selectors = [
            f'.dropdown-item:has-text("{queue_name}") input[type="checkbox"]',
            f'label:has-text("{queue_name}") input[type="checkbox"]',
            f'div:has-text("{queue_name}") input[type="checkbox"]',
            f'text={queue_name}',
        ]

        for selector in queue_selectors:
            try:
                items = submenu.locator(selector)
                for index in range(items.count()):
                    item = items.nth(index)
                    if not item.is_visible():
                        continue

                    item.scroll_into_view_if_needed()
                    if 'input[type="checkbox"]' in selector:
                        self._check_checkbox(item)
                    else:
                        row = item.locator('xpath=ancestor-or-self::*[.//input[@type="checkbox"]][1]')
                        checkbox = row.locator('input[type="checkbox"]').first
                        if checkbox and checkbox.count() > 0:
                            self._check_checkbox(checkbox)
                        else:
                            item.click(force=True)

                    self._safe_wait(300)
                    if self._queue_is_checked(submenu):
                        return True
            except Exception:
                continue

        return self._select_queue_with_dom(queue_name)

    def _select_queue_with_dom(self, queue_name: str, timeout: int = 10000) -> bool:
        start = time.time()
        while time.time() - start < timeout / 1000:
            try:
                selected = self.page.evaluate(
                    """queueName => {
                        const wanted = queueName.toLowerCase();
                        const boxes = Array.from(document.querySelectorAll(
                            '.submenu-menu.show input[type="checkbox"], input[type="checkbox"]'
                        ));
                        const checkbox = boxes.find(input => {
                            const row = input.closest('.dropdown-item, label, div');
                            return row && row.textContent.toLowerCase().includes(wanted);
                        }) || (boxes.length === 1 ? boxes[0] : null);
                        if (!checkbox) return false;

                        checkbox.scrollIntoView({ block: 'center', inline: 'center' });
                        checkbox.click();
                        const setter = Object.getOwnPropertyDescriptor(
                            HTMLInputElement.prototype,
                            'checked'
                        ).set;
                        setter.call(checkbox, true);
                        checkbox.dispatchEvent(new MouseEvent('click', { bubbles: true }));
                        checkbox.dispatchEvent(new Event('input', { bubbles: true }));
                        checkbox.dispatchEvent(new Event('change', { bubbles: true }));
                        return checkbox.checked;
                    }""",
                    queue_name,
                )
                if selected:
                    return True
            except Exception:
                pass

            self._safe_wait(300)

        return False

    def _queue_checkbox_visible(self, submenu) -> bool:
        try:
            checkbox = submenu.locator('input[type="checkbox"]').first
            return bool(checkbox and checkbox.is_visible())
        except Exception:
            return False

    def _queue_is_checked(self, submenu) -> bool:
        try:
            return bool(submenu.locator('input[type="checkbox"]:checked').count())
        except Exception:
            return False

    def _check_checkbox(self, checkbox) -> None:
        try:
            checkbox.scroll_into_view_if_needed(timeout=1000)
            checkbox.check(force=True, timeout=2000)
            return
        except Exception:
            pass

        try:
            checkbox.click(force=True, timeout=2000)
            return
        except Exception:
            pass

        checkbox.evaluate(
            """element => {
                element.click();
                element.checked = true;
                element.dispatchEvent(new Event('input', { bubbles: true }));
                element.dispatchEvent(new Event('change', { bubbles: true }));
            }"""
        )

    def _click_send_to_audit(self) -> bool:
        submenu = self._send_to_audit_submenu()
        if not submenu:
            return False

        send_selectors = [
            'button:has-text("Send")',
            'role=button[name="Send"]',
            '.send-to-review-btn',
        ]

        for selector in send_selectors:
            try:
                buttons = submenu.locator(selector)
                for index in range(buttons.count()):
                    button = buttons.nth(index)
                    if not button.is_visible():
                        continue

                    button.scroll_into_view_if_needed()
                    button.click(force=True)
                    self.page.wait_for_load_state('networkidle')
                    self._safe_wait(1000)
                    print('  [OK] Send to Audit clicked')
                    return True
            except Exception:
                continue

        return False

    def _wait_for_audit_sent_status(self, queue_name: str, timeout: int = 60000) -> bool:
        start = time.time()
        success_patterns = [
            'Sent to Audit',
            'Send to Audit',
            'Audit',
            queue_name,
            'success',
            'successfully',
        ]

        while time.time() - start < timeout / 1000:
            self.wait_for_loading_overlay(1000)

            try:
                toast = self.page.locator(
                    '.Toastify__toast--success, .Toastify__toast-body, [role="alert"]'
                )
                for index in range(toast.count()):
                    item = toast.nth(index)
                    if item.is_visible():
                        text = item.inner_text(timeout=1000)
                        if any(pattern.lower() in text.lower() for pattern in success_patterns):
                            print('  [OK] Send to Audit status detected')
                            return True
            except Exception:
                pass

            try:
                if not self._send_to_audit_panel_is_visible():
                    print('  [OK] Send to Audit panel closed')
                    return True
            except Exception:
                pass

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

    audit_queue = os.getenv('AUDIT_QUEUE', 'Code Enhance')
    exit_code = [0]

    with sync_playwright() as playwright:
        browser_type = getattr(playwright, settings.browser)
        browser = browser_type.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()

        try:
            login = LoginPage(page)
            nav = UnassignedEpisodePage(page)
            audit = SendToAuditForQueuesPage(page)

            def fail_step(msg: str, exc: Exception | None = None):
                print(f'ERROR: {msg}')
                if exc:
                    traceback.print_exception(type(exc), exc, exc.__traceback__)

                ts = int(time.time())
                debug_dir = Path('reports/e2e/debug')
                debug_dir.mkdir(parents=True, exist_ok=True)
                screenshot_path = debug_dir / f'send_to_audit_for_queues_failure_{ts}.png'
                html_path = debug_dir / f'send_to_audit_for_queues_failure_{ts}.html'

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
                print(f'\nStarting {name} Send to Audit Queues scenario...')

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

                print('Sending episode to audit queue...')
                try:
                    if not audit.send_to_audit_queue(audit_queue):
                        raise AssertionError('send_to_audit_queue returned False')
                    print('  [OK] Send to Audit queue completed')
                except Exception as e:
                    fail_step(f'Send to Audit queue failed for {name}', e)
                    raise

                print(f'  [OK] {name} Send to Audit Queues scenario completed')

            open_coder_workspace_from_base('Opening Code Workflow/Coder Workspace...')
            run_send_to_audit_scenario('Code Assist', audit.open_code_assist)

            open_coder_workspace_from_base(
                '\nReopening Code Workflow/Coder Workspace after Code Assist audit completion...'
            )
            run_send_to_audit_scenario('Code Accelerate', audit.open_code_accelerate_panel)

            print('\nSend to Audit for Queues run finished')
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
