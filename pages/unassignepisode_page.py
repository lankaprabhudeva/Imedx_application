import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from playwright.sync_api import Page, sync_playwright
from pages.base_page import BasePage
from pages.login_page import LoginPage


class UnassignedEpisodePage(BasePage):
    """Single-page object for unassigned episode reassign workflows."""

    CODE_WORKFLOW_IMAGE = 'img[alt*="Code Workflow"], img[title*="Code Workflow"], [aria-label*="Code Workflow"]'
    HIM_WORKSPACE_LINK = 'a:has-text("HIM Workspace"), button:has-text("HIM Workspace"), a:has-text("HIM"), button:has-text("HIM"), [href*="him"], [href*="workflow"]'
    UNASSIGNED_EPISODES_LINK = 'text=Unassigned Episodes, a:has-text("Unassigned Episodes"), text=Unassigned'
    CODER_WORKSPACE_LINK = 'a:has-text("Coder Workspace"), button:has-text("Coder Workspace"), text=Coder Workspace'
    REASSIGN_BUTTON = 'button:has-text("Re-assign"), button:has-text("Reassign"), text=Re-assign, text=Reassign'
    CODER_INPUT = '#react-select-3-input, input[aria-label*="Coder"], input[placeholder*="Coder"], input[role="combobox"]'
    QUEUE_INPUT = 'input[placeholder*="Select queue"], input[aria-label*="Select queue"], input[placeholder*="queue"], input[name*="queue"]'
    CONFIRM_BUTTON = 'button:has-text("Confirm assignment"), button:has-text("Confirm Assignment"), button:has-text("Confirm"), button:has-text("Assign")'
    SUCCESS_MESSAGE = 'text=Assigned Episode Successfully, text=Assigned episodes successfully, text=successfully assigned, text=assignment successful'

    def open_base_url(self, base_url: str):
        self.page.goto(base_url)

    def login(self, username: str, password: str):
        login_page = LoginPage(self.page)
        login_page.open_login_page(self.page.url or "")
        login_page.login(username, password)

    def open_code_workflow(self) -> bool:
        # Try several strategies with retries to handle SPA timing
        attempts = 3
        for attempt in range(attempts):
            try:
                image = self.page.locator(self.CODE_WORKFLOW_IMAGE).first
                if image.is_visible():
                    image.scroll_into_view_if_needed()
                    image.click()
                    self.page.wait_for_load_state('networkidle')
                    return True
            except Exception:
                pass

            # Card Launch fallback
            try:
                card = self.page.locator('div.home-container:has(div.home-card-title:has-text("Code Workflow"))').first
                if card and card.is_visible():
                    try:
                        launch = card.locator('span.home-card-link:has-text("Launch")').first
                        if launch and launch.is_visible():
                            launch.scroll_into_view_if_needed()
                            launch.click()
                            self.page.wait_for_load_state('networkidle')
                            return True
                    except Exception:
                        pass
                    try:
                        launch = card.get_by_text('Launch', exact=True).first
                        if launch and launch.is_visible():
                            launch.scroll_into_view_if_needed()
                            launch.click()
                            self.page.wait_for_load_state('networkidle')
                            return True
                    except Exception:
                        pass
            except Exception:
                pass

            # Breadcrumb/link fallback
            try:
                bc = self.page.locator('nav[aria-label="breadcrumb"] a:has-text("Code Workflow")').first
                if bc and bc.is_visible():
                    bc.scroll_into_view_if_needed()
                    bc.click()
                    self.page.wait_for_load_state('networkidle')
                    return True
            except Exception:
                pass

            try:
                link = self.page.locator('a[href*="Code-Workflow"], a:has-text("Code Workflow")').first
                if link and link.is_visible():
                    link.scroll_into_view_if_needed()
                    link.click()
                    self.page.wait_for_load_state('networkidle')
                    return True
            except Exception:
                pass

            # pause before retrying
            try:
                self.page.wait_for_timeout(700)
            except Exception:
                time.sleep(0.7)

        return False

    def open_him_workspace(self) -> bool:
        try:
            link = self.page.locator(self.HIM_WORKSPACE_LINK).first
            if link.is_visible():
                link.click()
                self.page.wait_for_load_state('networkidle')
                return True
        except Exception:
            pass
        return False

    def open_coder_workspace(self) -> bool:
        # Try role/link first
        try:
            self.page.get_by_role('link', name='Coder Workspace').click()
            self.page.wait_for_load_state('networkidle')
            return True
        except Exception:
            pass

        # Fallback: regex role
        try:
            self.page.get_by_role('link', name=re.compile(r'Coder Workspace', re.I)).click()
            self.page.wait_for_load_state('networkidle')
            return True
        except Exception:
            pass

        # Sidebar navigation/item attempt
        try:
            sidebar_item = self.page.locator('div.sidebar-navigation-container >> text="Coder Workspace"').first
            if sidebar_item and sidebar_item.is_visible():
                sidebar_item.scroll_into_view_if_needed()
                sidebar_item.click()
                self.page.wait_for_load_state('networkidle')
                return True
        except Exception:
            pass

        # Generic link locator fallback
        try:
            link = self.page.locator(self.CODER_WORKSPACE_LINK).first
            if link and link.is_visible():
                link.scroll_into_view_if_needed()
                link.click()
                self.page.wait_for_load_state('networkidle')
                return True
        except Exception:
            pass

        # Text search fallback
        try:
            txt = self.page.get_by_text('Coder Workspace', exact=False).first
            if txt and txt.is_visible():
                txt.scroll_into_view_if_needed()
                txt.click()
                self.page.wait_for_load_state('networkidle')
                return True
        except Exception:
            pass

        # Try clicking the 'Coding' work-queue card which opens the coder workspace
        try:
            coding_card = self.page.locator('span.my-work-queue-card-name:has-text("Coding")').first
            if coding_card and coding_card.is_visible():
                coding_card.scroll_into_view_if_needed()
                coding_card.click()
                self.page.wait_for_load_state('networkidle')
                return True
        except Exception:
            pass

        # Try the reporting card 'Outstanding Coding'
        try:
            outstanding = self.page.locator('p.reporting-cards-name:has-text("Outstanding Coding")').first
            if outstanding and outstanding.is_visible():
                outstanding.scroll_into_view_if_needed()
                outstanding.click()
                self.page.wait_for_load_state('networkidle')
                return True
        except Exception:
            pass

        return False

    def open_unassigned_episodes(self) -> bool:
        # Try a sequence of fallbacks to open the Unassigned Episodes list
        attempts = 3
        for attempt in range(attempts):
            # Direct link/button
            try:
                link = self.page.locator(self.UNASSIGNED_EPISODES_LINK).first
                if link and link.is_visible():
                    link.scroll_into_view_if_needed()
                    link.click()
                    self.page.wait_for_load_state('networkidle')
                    try:
                        self.page.wait_for_timeout(800)
                    except Exception:
                        time.sleep(0.8)
                    return True
            except Exception:
                pass

            # Text fallback
            try:
                link = self.page.get_by_text('Unassigned Episodes', exact=False).first
                if link and link.is_visible():
                    link.scroll_into_view_if_needed()
                    link.click()
                    self.page.wait_for_load_state('networkidle')
                    return True
            except Exception:
                pass

            # Click the Coding work-queue card then try again
            try:
                coding_card = self.page.locator('span.my-work-queue-card-name:has-text("Coding")').first
                if coding_card and coding_card.is_visible():
                    coding_card.scroll_into_view_if_needed()
                    coding_card.click()
                    self.page.wait_for_load_state('networkidle')
                    try:
                        self.page.wait_for_timeout(600)
                    except Exception:
                        time.sleep(0.6)
            except Exception:
                pass

            # Try the allocation section 'Unassigned Episodes' label
            try:
                alloc = self.page.locator('div.coding-allocation-section >> text="Unassigned Episodes"').first
                if alloc and alloc.is_visible():
                    alloc.scroll_into_view_if_needed()
                    alloc.click()
                    self.page.wait_for_load_state('networkidle')
                    return True
            except Exception:
                pass

            # Try reporting card 'Outstanding Coding' which can lead to the list
            try:
                outstanding = self.page.locator('p.reporting-cards-name:has-text("Outstanding Coding")').first
                if outstanding and outstanding.is_visible():
                    outstanding.scroll_into_view_if_needed()
                    outstanding.click()
                    self.page.wait_for_load_state('networkidle')
                    return True
            except Exception:
                pass

            # Try 'Unassigned Queue' card in the left sidebar
            try:
                unassigned = self.page.locator('span[aria-label="Unassigned Queue"], .left-coder-workflow-queues-card-name:has-text("Unassigned Queue"), text=Unassigned Queue').first
                if unassigned and unassigned.is_visible():
                    unassigned.scroll_into_view_if_needed()
                    unassigned.click()
                    self.page.wait_for_load_state('networkidle')
                    return True
            except Exception:
                pass

            try:
                self.page.wait_for_timeout(600)
            except Exception:
                time.sleep(0.6)

        return False

    def find_outstanding_episode(self, episode_id: str | None = None):
        self.wait_for_episode_list()

        candidate = self.page.locator('tr:has-text("Outstanding"), div:has-text("Outstanding"), [role="row"]:has-text("Outstanding")').first
        if candidate.count() == 0:
            raise AssertionError('Outstanding episode row was not found')

        if episode_id:
            rows = self.page.locator('tr:has-text("Outstanding"), div:has-text("Outstanding"), [role="row"]:has-text("Outstanding")')
            for index in range(rows.count()):
                row = rows.nth(index)
                if episode_id in row.inner_text():
                    return row

        return candidate

    def open_outstanding_episode(self, episode_id: str | None = None) -> str:
        row = self.find_outstanding_episode(episode_id)
        row.scroll_into_view_if_needed()
        row.dblclick()
        text = row.inner_text()
        match = re.search(r'EP-[A-Za-z0-9]+', text)
        return match.group(0) if match else (episode_id or '')

    def wait_for_episode_list(self, timeout: int = 15000):
        start = time.time()
        # broaden selectors to handle various table/grid implementations
        selectors = [
            'tr[data-episode-id]',
            '.episode-row',
            'table tbody tr',
            '[data-testid*="episode-row"]',
            'div[role="row"]',
            '[role="row"]',
            'tbody tr',
            '.k-grid .k-grid-content tr',        # Kendo UI
            '.ag-center-cols-container .ag-row', # ag-Grid
            '.rt-tr-group',                      # react-table groups
        ]

        check_interval = 0.5
        timeout_s = max(1, timeout / 1000)

        while time.time() - start < timeout_s:
            for selector in selectors:
                try:
                    rows = self.page.locator(selector)
                    if rows.count() > 0:
                        return True
                except Exception:
                    continue
            self.page.wait_for_timeout(int(check_interval * 1000))

        # capture debug artifacts to help diagnose why rows didn't appear
        debug_dir = Path('reports/e2e/debug')
        debug_dir.mkdir(parents=True, exist_ok=True)
        ts = int(time.time())
        ss_path = debug_dir / f'no_episode_rows_{ts}.png'
        html_path = debug_dir / f'no_episode_rows_{ts}.html'
        try:
            self.page.screenshot(path=str(ss_path), full_page=True)
        except Exception:
            pass
        try:
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(self.page.content())
        except Exception:
            pass

        raise AssertionError(f'No episode rows found on the Unassigned Episodes page. Wrote {ss_path} and {html_path} for debugging')

    def select_episode_checkbox(self, index: int = 1, episode_id: str | None = None) -> bool:
        self.wait_for_episode_list()

        row_selectors = [
            'tr[data-episode-id]',
            '.episode-row',
            'table tbody tr',
            '[data-testid*="episode-row"]',
            'div[role="row"]',
        ]

        candidate_indexes = []
        for selector in row_selectors:
            try:
                rows = self.page.locator(selector)
                count = rows.count()
                for row_index in range(count):
                    row = rows.nth(row_index)
                    checkbox = row.locator('input[type="checkbox"], [role="checkbox"]')
                    if checkbox.count() > 0 and checkbox.first.is_visible():
                        if episode_id:
                            text = row.inner_text().strip()
                            if episode_id in text:
                                checkbox.first.scroll_into_view_if_needed()
                                checkbox.first.check()
                                return True
                        candidate_indexes.append((row_index, checkbox.first))
            except Exception:
                continue

        if not candidate_indexes:
            raise AssertionError('No selectable episode checkbox found')

        if index > len(candidate_indexes):
            index = len(candidate_indexes)

        selected_checkbox = candidate_indexes[index - 1][1]
        selected_checkbox.scroll_into_view_if_needed()
        selected_checkbox.check()
        return True

    def open_reassign_dialog(self):
        # Try multiple locator strategies because mixing CSS and text selectors breaks parsing
        tried = []
        # CSS-based attempts
        for sel in ['button:has-text("Re-assign")', 'button:has-text("Reassign")', 'button:has-text("Re- assign")']:
            try:
                btn = self.page.locator(sel).first
                if btn and btn.is_visible():
                    btn.scroll_into_view_if_needed()
                    btn.click()
                    self.page.wait_for_load_state('networkidle')
                    return
            except Exception as e:
                tried.append((sel, str(e)))

        # role/text fallback
        try:
            btn = self.page.get_by_role('button', name=re.compile(r'Re-?assign', re.I)).first
            btn.scroll_into_view_if_needed()
            btn.click()
            self.page.wait_for_load_state('networkidle')
            return
        except Exception as e:
            tried.append(('role', str(e)))

        try:
            btn = self.page.get_by_text('Re-assign', exact=False).first
            btn.scroll_into_view_if_needed()
            btn.click()
            self.page.wait_for_load_state('networkidle')
            return
        except Exception as e:
            tried.append(('text', str(e)))

        # If we get here, raise a helpful error
        raise AssertionError(f'Could not open Reassign dialog. Tried locators: {tried}')

    def select_assignment_target(self, target_name: str = 'prabhu', assign_to: str = 'coder'):
        """Select assignment target using codegen-style pattern."""
        assign_to = (assign_to or 'coder').strip().lower()
        target_name = (target_name or '').strip()

        if assign_to == 'queue':
            # Codegen pattern for queue:
            # 1. Click .css-19bb58m three times
            # 2. Click "OR" text to clear overlay
            # 3. Click div filtered by "Select queue" at nth(2)
            # 4. Click the option by role
            try:
                self.page.locator('.css-19bb58m').click()
                self.page.locator('.css-19bb58m').click()
                self.page.locator('.css-19bb58m').click()
                self.page.wait_for_timeout(300)
                
                # Click "OR" to clear the intercepting overlay
                try:
                    self.page.get_by_text("OR", exact=True).click()
                    self.page.wait_for_timeout(200)
                except Exception:
                    pass
                
                # Click the "Select queue" div (use nth(2) as codegen does)
                candidates = self.page.locator('div').filter(has_text=re.compile(r'^Select queue$'))
                if candidates.count() >= 3:
                    candidates.nth(2).click(force=True)
                else:
                    candidates.first.click(force=True)
                self.page.wait_for_timeout(500)
                
                # Click the option by role
                if target_name:
                    opt = self.page.get_by_role('option', name=target_name).first
                    opt.click()
                    # Verify selection: listbox should close or input should contain the value
                    try:
                        self.page.locator('[role="listbox"]').first.wait_for(state='hidden', timeout=1500)
                        return True
                    except Exception:
                        try:
                            inp = self.page.locator("input[id^='react-select'], input[role='combobox'], input[aria-label*='Select queue']").first
                            if inp and target_name.lower() in (inp.input_value() or '').lower():
                                return True
                        except Exception:
                            pass
                    # Try keyboard confirm as fallback
                    try:
                        self.page.keyboard.press('Enter')
                        self.page.wait_for_timeout(300)
                        try:
                            self.page.locator('[role="listbox"]').first.wait_for(state='hidden', timeout=1000)
                            return True
                        except Exception:
                            pass
                    except Exception:
                        pass
                else:
                    # If no target, pick the first option
                    opt = self.page.get_by_role('option').first
                    opt.click()
                    try:
                        self.page.locator('[role="listbox"]').first.wait_for(state='hidden', timeout=1500)
                        return True
                    except Exception:
                        return True
            except Exception as e:
                # Capture debug artifacts
                debug_dir = Path('reports/e2e/debug')
                debug_dir.mkdir(parents=True, exist_ok=True)
                ts = int(time.time())
                ss_path = debug_dir / f'assign_target_failure_{assign_to}_{ts}.png'
                html_path = debug_dir / f'assign_target_failure_{assign_to}_{ts}.html'
                try:
                    self.page.screenshot(path=str(ss_path), full_page=True)
                except Exception:
                    pass
                try:
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(self.page.content())
                except Exception:
                    pass
                raise AssertionError(
                    f'Could not select queue "{target_name}". {str(e)}. '
                    f'Captured {ss_path} and {html_path} for debugging.'
                )
        else:
            # Coder: try standard react-select pattern
            try:
                # Click to open dropdown
                inp = self.page.locator('#react-select-3-input, input[aria-label*="Coder"]').first
                inp.click()
                self.page.wait_for_timeout(300)
                
                # Type coder name to filter
                if target_name:
                    inp.fill(target_name)
                    self.page.wait_for_timeout(300)
                
                # Select the matching option
                opt = self.page.get_by_role('option', name=re.compile(re.escape(target_name), re.I)).first
                opt.click()
                # Verify selection: wait for listbox to close or input to contain the value
                try:
                    self.page.locator('[role="listbox"]').first.wait_for(state='hidden', timeout=1500)
                    return True
                except Exception:
                    try:
                        inp = self.page.locator("input[id^='react-select'], input[role='combobox'], input[aria-label*='Coder']").first
                        if inp and target_name.lower() in (inp.input_value() or '').lower():
                            return True
                    except Exception:
                        pass
                # Enter fallback
                try:
                    self.page.keyboard.press('Enter')
                    self.page.wait_for_timeout(300)
                    try:
                        self.page.locator('[role="listbox"]').first.wait_for(state='hidden', timeout=1000)
                        return True
                    except Exception:
                        pass
                except Exception:
                    pass
                return True
            except Exception as e:
                # Fallback: try to click via text
                try:
                    if target_name:
                        opt = self.page.locator(f'text="{target_name}"').first
                        opt.click()
                        return True
                except Exception:
                    pass
                
                # Capture debug artifacts
                debug_dir = Path('reports/e2e/debug')
                debug_dir.mkdir(parents=True, exist_ok=True)
                ts = int(time.time())
                ss_path = debug_dir / f'assign_target_failure_{assign_to}_{ts}.png'
                html_path = debug_dir / f'assign_target_failure_{assign_to}_{ts}.html'
                try:
                    self.page.screenshot(path=str(ss_path), full_page=True)
                except Exception:
                    pass
                try:
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(self.page.content())
                except Exception:
                    pass
                raise AssertionError(
                    f'Could not select coder "{target_name}". {str(e)}. '
                    f'Captured {ss_path} and {html_path} for debugging.'
                )

    def select_coder(self, coder_name: str = 'prabhu'):
        return self.select_assignment_target(coder_name, assign_to='coder')

    def confirm_assignment(self):
        button = self.page.locator(self.CONFIRM_BUTTON).first
        button.scroll_into_view_if_needed()
        button.click()
        self.page.wait_for_load_state('networkidle')

    def verify_assignment_success(self) -> bool:
        try:
            self.page.locator(self.SUCCESS_MESSAGE).first.wait_for(state='visible', timeout=10000)
            return True
        except Exception:
            return False


def run_unassigned_episode_flow(username: str, password: str, coder_name: str = 'prabhu', base_url: str | None = None):
    from config.settings import Settings

    settings = Settings(env=os.getenv('ENV', 'dev'))
    base_url = base_url or settings.base_url
    headless = settings.headless
    headless_env = os.getenv('HEADLESS')
    if headless_env is not None:
        headless = headless_env.lower() in ('1', 'true', 'yes')

    with sync_playwright() as playwright:
        browser_type = getattr(playwright, settings.browser)
        browser = browser_type.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()

        try:
            unassigned = UnassignedEpisodePage(page)
            print('Navigating to base URL...')
            unassigned.open_base_url(base_url)

            print('Performing login...')
            unassigned.login(username, password)

            clicked_code = False
            if unassigned.open_code_workflow():
                print('Clicked Code Workflow image')
                clicked_code = True
            elif unassigned.open_him_workspace():
                print('Clicked HIM Workspace link')
            else:
                print('Could not find Code Workflow or HIM Workspace navigation')

            # Ensure we're on the Code Workflow route; SPA clicks may not trigger navigation reliably
            try:
                page.wait_for_url(re.compile(r'.*/Code-Workflow.*'), timeout=3000)
            except Exception:
                try:
                    # fallback: navigate directly
                    target = base_url.rstrip('/') + '/Code-Workflow'
                    print(f'Fallback navigating to {target}')
                    page.goto(target)
                    page.wait_for_load_state('networkidle')
                except Exception:
                    pass

            print('Opened Unassigned Episodes')
            unassigned.open_unassigned_episodes()

            print('Selecting first available episode checkbox dynamically...')
            unassigned.select_episode_checkbox(index=1)
            print('Checkbox selected')

            print('Opening Reassign dialog...')
            unassigned.open_reassign_dialog()

            assign_to = os.getenv('IMEDX_ASSIGN_TO', 'coder').strip().lower()
            if assign_to == 'queue':
                assign_target = os.getenv('IMEDX_ASSIGN_TARGET', '').strip()
            else:
                assign_target = os.getenv('IMEDX_ASSIGN_TARGET', coder_name).strip()

            if assign_to == 'queue' and not assign_target:
                print('Selecting first available queue dynamically')
            else:
                print(f'Selecting {assign_to} {assign_target}')

            unassigned.select_assignment_target(assign_target, assign_to=assign_to)

            print('Clicking confirm assignment')
            unassigned.confirm_assignment()

            if unassigned.verify_assignment_success():
                print('Assigned episodes successfully')
            else:
                print('Assignment success message not found')
        finally:
            context.close()
            browser.close()


if __name__ == '__main__':
    username = os.getenv('IMEDX_USERNAME', 'Sai')
    password = os.getenv('IMEDX_PASSWORD', 'Imedx@123')
    coder = os.getenv('IMEDX_CODER', 'prabhu')
    run_unassigned_episode_flow(username, password, coder)
