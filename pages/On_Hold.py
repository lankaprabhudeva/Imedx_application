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


class OnHoldPage(CodingCompletePage):
    """Workflow for moving an Outstanding episode to On Hold after code entry."""

    MY_ACTIONS_BUTTON = 'button:has-text("My Actions"), button[aria-label="My Actions"]'
    ON_HOLD_ACTION_SELECTORS = [
        'button:has-text("On Hold")',
        'a.dropdown-item:has-text("On Hold")',
        '[role="menuitem"]:has-text("On Hold")',
        '[role="button"]:has-text("On Hold")',
        'text=On Hold',
    ]
    ON_HOLD_STATUS_SELECTORS = [
        '.episode-container [aria-label*="On Hold"]',
        '.episode-container .info-value:has-text("On Hold")',
        '.epsoide-status-card [aria-label*="On Hold"]',
        '.epsoide-status-card .info-value:has-text("On Hold")',
        '.my-actions-div:has-text("On Hold")',
        'text=On Hold',
    ]

    def put_status_on_hold(self) -> bool:
        """Open My Actions and select On Hold without confirming DRG."""
        if not self._open_my_actions_menu():
            print('  ! My Actions menu did not open')
            return False

        if not self._click_on_hold_action():
            print('  ! On Hold action not found in My Actions')
            return False

        if not self.wait_for_on_hold_status():
            print('  ! On Hold status not detected')
            return False

        episode_identifier = self.completed_episode_identifier or 'Unknown Episode'
        print(f'  [OK] On Hold status updated for Episode Identifier: {episode_identifier}')
        return True

    def _open_my_actions_menu(self) -> bool:
        for attempt in range(3):
            try:
                self.page.evaluate('window.scrollTo(0, 0)')
                self._safe_wait(300)
            except Exception:
                pass

            selectors = [
                self.MY_ACTIONS_BUTTON,
                'button:has(span[aria-label="My Actions"])',
                'button:has-text("My Actions")',
                'span[aria-label="My Actions"]',
                'text=My Actions',
            ]

            for selector in selectors:
                try:
                    items = self.page.locator(selector)
                    for index in range(items.count()):
                        item = items.nth(index)
                        if not item.is_visible():
                            continue

                        target = item
                        try:
                            if selector.startswith('span') or selector == 'text=My Actions':
                                target = item.locator('xpath=ancestor::button[1]')
                        except Exception:
                            target = item

                        target.scroll_into_view_if_needed()
                        self._safe_wait(200)

                        for click_attempt in range(3):
                            try:
                                if click_attempt == 0:
                                    target.click(force=True)
                                elif click_attempt == 1:
                                    box = target.bounding_box(timeout=1000)
                                    if box:
                                        self.page.mouse.click(
                                            box['x'] + box['width'] / 2,
                                            box['y'] + box['height'] / 2,
                                        )
                                else:
                                    target.evaluate(
                                        """element => {
                                            for (const eventName of [
                                                'pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click'
                                            ]) {
                                                element.dispatchEvent(new MouseEvent(eventName, {
                                                    bubbles: true,
                                                    cancelable: true,
                                                    view: window
                                                }));
                                            }
                                            element.click();
                                        }"""
                                    )
                            except Exception:
                                continue

                            self._safe_wait(900)
                            if self._my_actions_menu_opened():
                                print('  [OK] My Actions menu opened')
                                return True
                except Exception:
                    continue

            self._safe_wait(500)

        return False

    def _my_actions_menu_opened(self) -> bool:
        selectors = [
            '.dropdown-menu.show',
            '[role="menu"]',
            'text=View audit log',
            'text=Sending for billing',
        ]
        selectors.extend(self.ON_HOLD_ACTION_SELECTORS)

        for selector in selectors:
            try:
                items = self.page.locator(selector)
                for index in range(items.count()):
                    if items.nth(index).is_visible():
                        return True
            except Exception:
                continue

        return False

    def _click_on_hold_action(self) -> bool:
        for selector in self.ON_HOLD_ACTION_SELECTORS:
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
                    self._safe_wait(200)
                    item.click(force=True)
                    try:
                        self.page.wait_for_load_state('networkidle', timeout=5000)
                    except Exception:
                        pass
                    self._safe_wait(1000)
                    print('  [OK] On Hold clicked')
                    return True
            except Exception:
                continue

        try:
            button = self.page.get_by_role('button', name=re.compile(r'On Hold', re.I)).first
            if button and button.is_visible():
                button.scroll_into_view_if_needed()
                button.click(force=True)
                self._safe_wait(1000)
                print('  [OK] On Hold clicked')
                return True
        except Exception:
            pass

        return False

    def wait_for_on_hold_status(self, timeout: int = 60000) -> bool:
        start = time.time()

        while time.time() - start < timeout / 1000:
            self.wait_for_loading_overlay(1000)

            for selector in self.ON_HOLD_STATUS_SELECTORS:
                try:
                    items = self.page.locator(selector)
                    for index in range(items.count()):
                        item = items.nth(index)
                        if item.is_visible():
                            print('  [OK] On Hold status is visible')
                            return True
                except Exception:
                    continue

            self._safe_wait(1500)

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
            on_hold = OnHoldPage(page)

            def fail_step(msg: str, exc: Exception | None = None):
                print(f'ERROR: {msg}')
                if exc:
                    traceback.print_exception(type(exc), exc, exc.__traceback__)

                ts = int(time.time())
                debug_dir = Path('reports/e2e/debug')
                debug_dir.mkdir(parents=True, exist_ok=True)
                screenshot_path = debug_dir / f'on_hold_failure_{ts}.png'
                html_path = debug_dir / f'on_hold_failure_{ts}.html'

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

            def run_on_hold_scenario(name: str, open_coding_panel):
                print(f'\nStarting {name} On Hold scenario...')

                print('Applying Outstanding Status filter...')
                try:
                    if not on_hold.apply_outstanding_filter():
                        raise AssertionError('Outstanding Status filter was not applied')
                    print('  [OK] Outstanding Status filter applied')
                except Exception as e:
                    fail_step(f'Applying Outstanding Status filter failed for {name}', e)
                    raise

                print('Opening first outstanding episode...')
                try:
                    if not on_hold.open_first_outstanding_episode():
                        raise AssertionError('open_first_outstanding_episode returned False')
                    print('  [OK] Outstanding episode opened')
                except Exception as e:
                    fail_step(f'Opening outstanding episode failed for {name}', e)
                    raise

                print(f'Opening {name} coding panel...')
                try:
                    if not open_coding_panel():
                        raise AssertionError(f'Opening {name} returned False')
                    on_hold.close_popup_if_visible()
                    print(f'  [OK] {name} coding panel opened')
                except Exception as e:
                    fail_step(f'Opening {name} coding panel failed', e)
                    raise

                print('Entering principal, additional diagnosis, and procedure codes...')
                try:
                    if not on_hold.enter_coding_codes(
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

                print('Skipping Confirm DRG as requested...')
                print('Putting episode status On Hold from My Actions...')
                try:
                    if not on_hold.put_status_on_hold():
                        raise AssertionError('put_status_on_hold returned False')
                    print('  [OK] On Hold clicked')
                except Exception as e:
                    fail_step(f'Putting episode On Hold failed for {name}', e)
                    raise

                print(f'  [OK] {name} On Hold scenario completed')

            open_coder_workspace_from_base('Opening Code Workflow/Coder Workspace...')
            run_on_hold_scenario('Code Assist', on_hold.open_code_assist)

            open_coder_workspace_from_base(
                '\nReopening Code Workflow/Coder Workspace after Code Assist On Hold completion...'
            )
            run_on_hold_scenario('Code Accelerate', on_hold.open_code_accelerate_panel)

            print('\nOn Hold run finished')
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
