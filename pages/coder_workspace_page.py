import os
import sys
import re
import time
from pathlib import Path

# Allow running this file directly from repository root
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pages.base_page import BasePage


class CoderWorkspacePage(BasePage):
    """Page object for Coder Workspace / Code Assist flows."""

    BREADCRUMB_CODE_WORKFLOW = 'nav[aria-label="breadcrumb"] a:has-text("Code Workflow"), .breadcrumb a:has-text("Code Workflow")'
    CODE_WORKFLOW_IMAGE = 'img[alt*="Code Workflow"], img[title*="Code Workflow"], [aria-label*="Code Workflow"]'
    CODER_WORKSPACE_SIDEBAR = 'div.sidebar-navigation-container >> text="Coder Workspace"'
    CODER_WORKSPACE_LINK = 'a:has-text("Coder Workspace"), button:has-text("Coder Workspace")'
    OUTSTANDING_FILTER_TOGGLE = '.css-8mmkcg, button:has-text("Outstanding")'
    OUTSTANDING_OPTION = 'role=option[name="Outstanding"]'
    APPLY_FILTER_BUTTON = 'button:has-text("Apply")'
    OUTSTANDING_EPISODE_ROW = 'tr:has-text("Outstanding"), div:has-text("Outstanding"), [role="row"]:has-text("Outstanding")'
    FIRST_EPISODE_CELL = 'role=cell'
    CODE_ASSIST_BUTTON = 'button:has-text("Code Assist")'
    CANCEL_BUTTON = 'button:has-text("Cancel")'
    PRINCIPAL_INPUT = 'input[name="principal"], input[placeholder*="principal"], [aria-label*="principal"]'
    ADDITIONAL_INPUT = 'input[name="additional"], input[placeholder*="additional"], [aria-label*="additional"]'
    MY_ACTIONS_BUTTON = 'button:has-text("My Actions")'
    AUDITORS_BUTTON = 'button:has-text("Auditors")'
    CODERS_BUTTON = 'button:has-text("Coders")'
    CODER_SEARCH_INPUT = 'input[role="textbox"][name="Search coders..."], input[placeholder*="Search coders"], input[aria-label*="Search coders"]'
    CODER_RADIO = 'input[type="radio"], [role="radio"]'
    REASON_TEXTBOX = 'input[role="textbox"][name="Enter reason for review..."], textarea[placeholder*="reason"], [aria-label*="Enter reason for review..."]'
    SEND_BUTTON = 'button:has-text("Send")'
    CONFIRM_DRG_BUTTON = 'button:has-text("Confirm DRG"), button:has-text("Confirm DRGconfirm")'
    SEARCH_EPISODE_INPUT = 'input[placeholder*="Search by Episode ID"], input[aria-label*="Search by Episode ID"], input[name*="episode"]'
    CODE_COPIED_PLUS_BUTTON = 'button:has-text("Code Copied plus"), button:has-text("Code Copied +")'
    EPISODE_ROW = 'tr, div, [role="row"]'
    CODE_ROW = '[role="row"]:has-text("{code}"), tr:has-text("{code}"), div:has-text("{code}")'
    EPISODE_ID_REGEX = re.compile(r'EP-[A-Za-z0-9]+')

    def click_breadcrumb_code_workflow(self) -> bool:
        try:
            breadcrumb = self.page.locator(self.BREADCRUMB_CODE_WORKFLOW).first
            if breadcrumb.is_visible():
                breadcrumb.click()
                self.page.wait_for_load_state('networkidle')
                return True
        except Exception:
            pass
        return False

    def open_code_workflow(self) -> bool:
        try:
            # Try to find and click Code Workflow image using the exact role selector
            image = self.page.get_by_role('img', name='Code Workflow').first
            if image and image.is_visible():
                image.scroll_into_view_if_needed()
                image.click()
                self.page.wait_for_load_state('networkidle')
                return True
        except Exception:
            pass

        try:
            # Fallback: try with regex
            image = self.page.get_by_role('img', name=re.compile(r'Code Workflow', re.I)).first
            if image and image.is_visible():
                image.scroll_into_view_if_needed()
                image.click()
                self.page.wait_for_load_state('networkidle')
                return True
        except Exception:
            pass

        try:
            # Fallback: try card-based approach
            card = self.page.locator('div.home-container:has(div.home-card-title:has-text("Code Workflow"))').first
            if card and card.is_visible():
                launch = card.locator('span.home-card-link', has_text='Launch').first
                if launch and launch.is_visible():
                    launch.scroll_into_view_if_needed()
                    launch.click()
                    self.page.wait_for_load_state('networkidle')
                    return True
        except Exception:
            pass

        try:
            # Fallback: try breadcrumb
            breadcrumb = self.page.locator(self.BREADCRUMB_CODE_WORKFLOW).first
            if breadcrumb.is_visible():
                breadcrumb.click()
                self.page.wait_for_load_state('networkidle')
                return True
        except Exception:
            pass

        return False

    def open_coder_workspace(self) -> bool:
        # Primary approach: use the proven role/link selector (no .first)
        try:
            self.page.get_by_role('link', name='Coder Workspace').click()
            self.page.wait_for_load_state('networkidle')
            return True
        except Exception:
            pass

        # Fallback: try with regex
        try:
            self.page.get_by_role('link', name=re.compile(r'Coder Workspace', re.I)).click()
            self.page.wait_for_load_state('networkidle')
            return True
        except Exception:
            pass

        # Fallback: try sidebar navigation item
        try:
            sidebar_item = self.page.locator(self.CODER_WORKSPACE_SIDEBAR).first
            if sidebar_item and sidebar_item.is_visible():
                sidebar_item.scroll_into_view_if_needed()
                sidebar_item.click()
                self.page.wait_for_load_state('networkidle')
                return True
        except Exception:
            pass

        # Fallback: try primary link locator
        try:
            link = self.page.locator(self.CODER_WORKSPACE_LINK).first
            if link and link.is_visible():
                link.scroll_into_view_if_needed()
                link.click()
                self.page.wait_for_load_state('networkidle')
                return True
        except Exception:
            pass

        # Fallback: try text search
        try:
            txt = self.page.get_by_text('Coder Workspace', exact=False).first
            if txt and txt.is_visible():
                txt.scroll_into_view_if_needed()
                txt.click()
                self.page.wait_for_load_state('networkidle')
                return True
        except Exception:
            pass

        # Save debug info for investigation
        try:
            debug_dir = Path('reports/e2e/debug')
            debug_dir.mkdir(parents=True, exist_ok=True)
            ts = int(time.time())
            ss = debug_dir / f'coder_workspace_not_found_{ts}.png'
            html = debug_dir / f'coder_workspace_not_found_{ts}.html'
            try:
                self.page.screenshot(path=str(ss), full_page=True)
            except Exception:
                pass
            try:
                with open(html, 'w', encoding='utf-8') as f:
                    f.write(self.page.content())
            except Exception:
                pass
        except Exception:
            pass

        return False

    def open_code_assist(self) -> bool:
        try:
            button = self.page.locator(self.CODE_ASSIST_BUTTON).first
            button.scroll_into_view_if_needed()
            button.click()
            self.page.wait_for_load_state('networkidle')
            return True
        except Exception:
            return False

    def close_popup_if_visible(self) -> bool:
        try:
            button = self.page.get_by_role('button', name=re.compile(r'Cancel', re.I)).first
            if button.is_visible():
                button.click()
                self.page.wait_for_timeout(500)
                return True
        except Exception:
            pass
        return False

    def apply_outstanding_filter(self) -> bool:
        try:
            filter_toggle = self.page.locator(self.OUTSTANDING_FILTER_TOGGLE).first
            filter_toggle.scroll_into_view_if_needed()
            filter_toggle.click()
            self.page.wait_for_timeout(500)
        except Exception:
            pass

        try:
            option = self.page.get_by_role('option', name='Outstanding').first
            option.scroll_into_view_if_needed()
            option.click()
            self.page.wait_for_timeout(500)
        except Exception:
            try:
                option = self.page.get_by_text('Outstanding', exact=True).first
                option.scroll_into_view_if_needed()
                option.click()
                self.page.wait_for_timeout(500)
            except Exception:
                pass

        try:
            apply_button = self.page.get_by_role('button', name='Apply').first
            apply_button.scroll_into_view_if_needed()
            apply_button.click()
            self.page.wait_for_load_state('networkidle')
            return True
        except Exception:
            return False

    def open_first_outstanding_episode(self) -> bool:
        try:
            cell = self.page.get_by_role('cell').first
            if cell.is_visible():
                cell.scroll_into_view_if_needed()
                cell.click()
                self.page.wait_for_load_state('networkidle')
                return True
        except Exception:
            pass
        return False

    def enter_principal_diagnosis(self, code: str) -> bool:
        if not code:
            return False
        try:
            input_el = self.page.locator(self.PRINCIPAL_INPUT).first
            input_el.scroll_into_view_if_needed()
            input_el.click()
            input_el.fill(code)
            self.page.wait_for_timeout(500)
            input_el.press('Enter')
            self.page.wait_for_timeout(500)
            return True
        except Exception:
            return False

    def open_my_actions(self) -> bool:
        selectors = [
            self.MY_ACTIONS_BUTTON,
            'button:has-text("My Actions")',
            'button[aria-label*="My Actions"]',
            'text=My Actions'
        ]
        for selector in selectors:
            try:
                button = self.page.locator(selector).first
                if button and button.is_visible():
                    button.scroll_into_view_if_needed()
                    button.click()
                    self.page.wait_for_load_state('networkidle')
                    return True
            except Exception:
                pass
        return False

    def navigate_to_coder_assignment(self) -> bool:
        try:
            auditors = self.page.get_by_role('button', name=re.compile(r'Auditors', re.I)).first
            auditors.scroll_into_view_if_needed()
            auditors.click()
            self.page.wait_for_timeout(500)
        except Exception:
            pass

        try:
            coders = self.page.get_by_role('button', name=re.compile(r'Coders', re.I)).first
            coders.scroll_into_view_if_needed()
            coders.click()
            self.page.wait_for_load_state('networkidle')
            return True
        except Exception:
            pass

        try:
            coders = self.page.locator(self.CODERS_BUTTON).first
            coders.scroll_into_view_if_needed()
            coders.click()
            self.page.wait_for_load_state('networkidle')
            return True
        except Exception:
            return False

    def search_coder(self, coder_name: str) -> bool:
        if not coder_name:
            return False
        selectors = [
            'input[role="textbox"][name="Search coders..."], input[placeholder*="Search coders"], input[aria-label*="Search coders"]',
            self.CODER_SEARCH_INPUT,
            'input[placeholder*="Search coders..."], input[aria-label*="Search coders..."]',
            'input[placeholder*="Search coders"], input[aria-label*="Search coders"]'
        ]
        for selector in selectors:
            try:
                search_input = self.page.locator(selector).first
                if search_input and search_input.is_visible():
                    search_input.scroll_into_view_if_needed()
                    search_input.click()
                    search_input.fill(coder_name)
                    self.page.keyboard.press('Enter')
                    self.page.wait_for_timeout(500)
                    return True
            except Exception:
                pass
        try:
            search_input = self.page.get_by_role('textbox', name=re.compile(r'Search coders', re.I)).first
            search_input.scroll_into_view_if_needed()
            search_input.click()
            search_input.fill(coder_name)
            self.page.keyboard.press('Enter')
            self.page.wait_for_timeout(500)
            return True
        except Exception:
            return False

    def select_first_coder(self) -> bool:
        try:
            radio = self.page.get_by_role('radio').first
            if radio and radio.is_visible():
                radio.scroll_into_view_if_needed()
                radio.click()
                self.page.wait_for_timeout(300)
                return True
        except Exception:
            pass

        try:
            radio = self.page.locator('input[type="radio"]').first
            if radio and radio.is_visible():
                radio.scroll_into_view_if_needed()
                radio.check()
                self.page.wait_for_timeout(300)
                return True
        except Exception:
            pass

        try:
            radio = self.page.locator(self.CODER_RADIO).first
            if radio and radio.is_visible():
                radio.scroll_into_view_if_needed()
                radio.click()
                self.page.wait_for_timeout(300)
                return True
        except Exception:
            pass

        return False

    def enter_reason_for_review(self, reason: str) -> bool:
        if not reason:
            return False
        selectors = [
            self.REASON_TEXTBOX,
            'input[placeholder*="reason"], textarea[placeholder*="reason"], input[aria-label*="Enter reason for review..."]',
            'textarea[placeholder*="reason"], input[aria-label*="Enter reason for review"]'
        ]
        for selector in selectors:
            try:
                textbox = self.page.locator(selector).first
                if textbox and textbox.is_visible():
                    textbox.scroll_into_view_if_needed()
                    textbox.click()
                    textbox.fill(reason)
                    self.page.wait_for_timeout(300)
                    return True
            except Exception:
                pass
        return False

    def send_episode_to_coder(self) -> bool:
        selectors = [
            'button:has-text("Send")',
            'button:has-text("Send to")',
            'button[aria-label*="Send"]',
            'text=Send'
        ]
        for selector in selectors:
            try:
                button = self.page.locator(selector).first
                if button and button.is_visible():
                    button.scroll_into_view_if_needed()
                    button.click()
                    self.page.wait_for_load_state('networkidle')
                    return True
            except Exception:
                pass

        try:
            button = self.page.get_by_role('button', name=re.compile(r'Send', re.I)).first
            button.scroll_into_view_if_needed()
            button.click()
            self.page.wait_for_load_state('networkidle')
            return True
        except Exception:
            pass

        try:
            button = self.page.get_by_text('Send', exact=False).first
            if button and button.is_visible():
                button.scroll_into_view_if_needed()
                button.click()
                self.page.wait_for_load_state('networkidle')
                return True
        except Exception:
            pass

        return False

    def find_outstanding_episode_row(self, episode_id: str | None = None):
        self.page.wait_for_load_state('networkidle')
        rows = self.page.locator(self.OUTSTANDING_EPISODE_ROW)
        if rows.count() == 0:
            raise AssertionError('No outstanding episode row found')

        if episode_id:
            for index in range(rows.count()):
                row = rows.nth(index)
                if episode_id in row.inner_text():
                    return row

        return rows.first

    def double_click_outstanding_episode(self, episode_id: str | None = None) -> str:
        row = self.find_outstanding_episode_row(episode_id)
        row.scroll_into_view_if_needed()
        row.dblclick()
        text = row.inner_text()
        match = self.EPISODE_ID_REGEX.search(text)
        return match.group(0) if match else (episode_id or '')

    def search_episode_by_id(self, episode_id: str) -> bool:
        if not episode_id:
            return False
        search_input = self.page.locator(self.SEARCH_EPISODE_INPUT).first
        search_input.scroll_into_view_if_needed()
        search_input.click()
        search_input.fill(episode_id)
        self.page.keyboard.press('Enter')
        self.page.wait_for_timeout(1000)
        return True

    def open_episode_by_id(self, episode_id: str) -> bool:
        if not episode_id:
            return False
        try:
            self.page.get_by_text(episode_id, exact=True).first.dblclick()
            self.page.wait_for_load_state('networkidle')
            return True
        except Exception:
            try:
                row = self.page.locator(self.EPISODE_ROW).filter(has_text=episode_id).first
                if row.count() > 0:
                    row.scroll_into_view_if_needed()
                    row.dblclick()
                    self.page.wait_for_load_state('networkidle')
                    return True
            except Exception:
                pass
        return False

    def add_principal_diagnosis(self, code: str) -> bool:
        if not code:
            raise ValueError('Diagnosis code must be provided')
        input_el = self.page.locator(self.PRINCIPAL_INPUT).first
        input_el.scroll_into_view_if_needed()
        input_el.click()
        input_el.fill(code)
        self.page.wait_for_timeout(500)
        try:
            choice = self.page.get_by_text(code, exact=True).first
            if choice.is_visible():
                choice.click()
        except Exception:
            pass
        self.page.keyboard.press('Enter')
        self.page.wait_for_timeout(500)
        self._click_code_copied_plus_if_available()
        return True

    def add_additional_code(self, code: str) -> bool:
        if not code:
            raise ValueError('Code must be provided')
        input_el = self.page.locator(self.ADDITIONAL_INPUT).first
        input_el.scroll_into_view_if_needed()
        input_el.click()
        input_el.fill(code)
        self.page.wait_for_timeout(500)
        try:
            choice = self.page.get_by_text(code, exact=True).first
            if choice.is_visible():
                choice.click()
        except Exception:
            pass
        self.page.keyboard.press('Enter')
        self.page.wait_for_timeout(500)
        self._click_code_copied_plus_if_available()
        return True

    def _click_code_copied_plus_if_available(self):
        try:
            button = self.page.locator(self.CODE_COPIED_PLUS_BUTTON).first
            if button.is_visible():
                button.scroll_into_view_if_needed()
                button.click()
                self.page.wait_for_timeout(400)
        except Exception:
            pass

    def put_on_hold(self) -> bool:
        self.page.locator(self.MY_ACTIONS_BUTTON).first.click()
        self.page.wait_for_timeout(500)
        self.page.locator(self.ON_HOLD_BUTTON).first.click()
        self.page.wait_for_load_state('networkidle')
        return True

    def confirm_drg(self) -> bool:
        try:
            button = self.page.get_by_role('button', name=re.compile(r'Confirm DRG', re.I)).first
            button.scroll_into_view_if_needed()
            button.click()
            self.page.wait_for_load_state('networkidle')
            return True
        except Exception:
            try:
                button = self.page.get_by_text('Confirm DRG', exact=False).first
                button.scroll_into_view_if_needed()
                button.click()
                self.page.wait_for_load_state('networkidle')
                return True
            except Exception:
                return False


if __name__ == '__main__':
    # Small demo runner so this page object can be executed directly for quick smoke checks.
    import os
    from playwright.sync_api import sync_playwright
    from pages.login_page import LoginPage
    from config.settings import Settings

    settings = Settings(env=os.getenv('ENV', 'dev'))
    base_url = settings.base_url
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
            login = LoginPage(page)
            coder = CoderWorkspacePage(page)

            print('Navigating to base URL...')
            page.goto(base_url)
            print('Performing login...')
            login.login(os.getenv('IMEDX_USERNAME', 'Sai'), os.getenv('IMEDX_PASSWORD', 'Imedx@123'))

            try:
                login.verify_login_success()
                print('Login appears successful')
            except AssertionError as e:
                print(f'Login did not succeed: {e}')
                debug_dir = Path('reports/e2e/debug')
                debug_dir.mkdir(parents=True, exist_ok=True)
                ts = int(time.time())
                ss = debug_dir / f'login_failure_{ts}.png'
                html = debug_dir / f'login_failure_{ts}.html'
                try:
                    page.screenshot(path=str(ss), full_page=True)
                except Exception:
                    pass
                try:
                    with open(html, 'w', encoding='utf-8') as f:
                        f.write(page.content())
                except Exception:
                    pass
                print(f'Login debug files written: {ss} {html}')
                raise

            print('Clicking Code Workflow breadcrumb...')
            if coder.click_breadcrumb_code_workflow():
                print('Code Workflow breadcrumb clicked')
            else:
                print('Could not click Code Workflow breadcrumb; attempting Code Workflow image')
                try:
                    page.get_by_role('img', name='Code Workflow').click()
                    page.wait_for_load_state('networkidle')
                    print('Code Workflow image clicked')
                except Exception as e:
                    print(f'Could not click Code Workflow image: {e}; attempting Code Workflow card')
                    if coder.open_code_workflow():
                        print('Code Workflow opened')
                    else:
                        print('Could not open Code Workflow; continuing to Coder Workspace fallback')

            print('Opening Coder Workspace...')
            opened = coder.open_coder_workspace()
            if opened:
                print('Coder Workspace opened')
            else:
                print('Could not open Coder Workspace')
                try:
                    debug_dir = Path('reports/e2e/debug')
                    debug_dir.mkdir(parents=True, exist_ok=True)
                    ts = int(time.time())
                    ss = debug_dir / f'coder_workspace_not_found_{ts}.png'
                    html = debug_dir / f'coder_workspace_not_found_{ts}.html'
                    try:
                        page.screenshot(path=str(ss), full_page=True)
                    except Exception:
                        pass
                    try:
                        with open(html, 'w', encoding='utf-8') as f:
                            f.write(page.content())
                    except Exception:
                        pass
                    print(f'Debug files written: {ss} {html}')
                except Exception:
                    pass

            print('Applying Outstanding filter...')
            coder.apply_outstanding_filter()

            print('Opening first available outstanding episode...')
            coder.open_first_outstanding_episode()

            print('Opening Code Assist...')
            coder.open_code_assist()
            coder.close_popup_if_visible()

            print('Entering principal diagnosis code Q87.19...')
            coder.enter_principal_diagnosis('Q87.19')

            print('Confirming DRG...')
            coder.confirm_drg()

            print('Opening My Actions...')
            coder.open_my_actions()

            print('Navigating to coder assignment section...')
            coder.navigate_to_coder_assignment()

            print('Searching for coder prabhu...')
            coder.search_coder('prabhu')
            coder.select_first_coder()

            print('Entering review reason comment...')
            coder.enter_reason_for_review('Sai coder sends this episode to coder Prabhu')

            print('Sending episode to coder...')
            if coder.send_episode_to_coder():
                print('Episode sent to coder successfully')
            else:
                print('Failed to send episode to coder')

            print('Workflow execution completed')
        finally:
            context.close()
            browser.close()
