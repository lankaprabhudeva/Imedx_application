import os
import sys
import re

# Allow direct execution from repository root using `python pages/workflow_page.py`
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from pages.base_page import BasePage


class WorkflowPage(BasePage):
    """Unified page object for login-to-HIM workflow and reassign scenarios."""

    # Navigation and workspace locators
    HIM_WORKSPACE_LINK = 'a:has-text("HIM"), [href*="him"], [href*="workflow"], [data-testid*="him"], [data-testid*="workflow"]'
    CODE_WORKFLOW_IMAGE = 'img[alt*="Code Workflow"], img[title*="Code Workflow"], [aria-label*="Code Workflow"]'
    BREADCRUMB_CODE_WORKFLOW = 'nav[aria-label="breadcrumb"] a:has-text("Code Workflow"), .breadcrumb a:has-text("Code Workflow")'
    UNASSIGNED_EPISODES_LINK = 'a:has-text("Unassigned"), a:has-text("Unassigned Episodes"), [data-testid*="unassigned"]'
    WORKFLOW_HEADER = 'h1:has-text("Code"), [class*="code-workflow"], [class*="workflow"]'
    HIM_WORKSPACE_HEADER = 'h1, [role="heading"], [class*="header"], [class*="title"]'
    WORKSPACE_NAVIGATION = '[class*="workspace-nav"], [class*="nav-menu"], nav, [class*="sidebar"]'
    DASHBOARD_CONTENT = '[class*="dashboard"], [class*="workspace-content"], main, [class*="main"]'
    USER_MENU = '[class*="user-menu"], [class*="profile"], [data-testid*="user"], [class*="account"]'
    LOGOUT_BUTTON = 'button:has-text("Logout"), [href*="logout"], [data-testid*="logout"], button:has-text("Sign Out")'

    # HIM workspace UI locators
    PATIENT_SEARCH = 'input[placeholder*="patient"], [class*="patient-search"], input[type="search"]'
    MEDICAL_RECORDS_TAB = '[role="tab"]:has-text("Medical Records"), [href*="records"], [data-testid*="records"]'
    CODING_TAB = '[role="tab"]:has-text("Coding"), [href*="coding"], [data-testid*="coding"]'
    QUALITY_TAB = '[role="tab"]:has-text("Quality"), [href*="quality"], [data-testid*="quality"]'
    REPORTS_TAB = '[role="tab"]:has-text("Reports"), [href*="reports"], [data-testid*="reports"]'

    # Episode list and action locators
    EPISODE_ROW = '[data-testid*="episode-row"], .episode-row, tr[data-episode-id]'
    EPISODE_CHECKBOX = f"{EPISODE_ROW} input[type='checkbox']"
    REASSIGN_BUTTON = 'button:has-text("Reassign"), button:has-text("Re-assign"), [data-testid*="reassign"], text=Reassign'

    # Reassign dialog locators
    REASSIGN_DIALOG = '[role="dialog"], .modal, .reassign-dialog, .popover'
    REASSIGN_POPUP_TITLE = 'h2:has-text("Reassign"), h1:has-text("Reassign"), [role="dialog"] h2, [role="dialog"] h1'
    QUEUE_DROPDOWN = 'select[name*="queue"], [data-testid*="queue-select"], .queue-select, [aria-label*="Queue"], [placeholder*="Queue"]'
    CODER_DROPDOWN = 'select[name="coder"], [data-testid*="coder-select"], .coder-select, [role="combobox"]'
    CODER_INPUT = '#react-select-3-input, input[role="combobox"], input[placeholder*="Coder"], input[aria-label*="Coder"]'
    CONFIRM_BUTTON = 'button.workflow-him-assign-confirm-btn:not([disabled]), button:has-text("Confirm Assignment"):not([disabled]), button:has-text("Confirm"):not([disabled]), button:has-text("Assign"):not([disabled]), button:has-text("OK"):not([disabled])'
    REASSIGN_SUCCESS_TEXT = 'text=successfully reassigned, text=Assignment successful, text=successfully assigned, text=assigned successfully'

    # --- Navigation Actions ---
    def navigate_to_him_workspace(self):
        current_url = self.page.url.lower()
        if 'code-workflow' in current_url or 'workflow' in current_url or 'him' in current_url:
            return True

        try:
            self.click(self.HIM_WORKSPACE_LINK)
            self.page.wait_for_load_state('networkidle')
            return True
        except Exception:
            pass

        try:
            self.page.goto(f"{self.page.url.rstrip('/')}/Code-Workflow")
            self.page.wait_for_load_state('networkidle')
            return True
        except Exception:
            return False

    def click_breadcrumb_menu(self):
        try:
            breadcrumb = self.page.locator('nav[aria-label="breadcrumb"], .breadcrumb, .breadcrumb-menu').first
            if breadcrumb.is_visible():
                breadcrumb.click()
                self.page.wait_for_timeout(500)
                return True
        except Exception:
            pass
        return False

    def click_him_workspace_menu(self):
        try:
            menu = self.page.locator('a:has-text("HIM Workspace"), button:has-text("HIM Workspace"), a:has-text("HIM"), button:has-text("HIM")').first
            if menu.is_visible():
                menu.click()
                self.page.wait_for_load_state('networkidle')
                return True
        except Exception:
            pass
        return self.navigate_to_him_workspace()

    def click_code_workflow_image(self):
        try:
            image = self.page.locator(self.CODE_WORKFLOW_IMAGE).first
            if image.is_visible():
                image.click()
                self.page.wait_for_load_state('networkidle')
                return True
        except Exception:
            pass
        return False

    def verify_him_workspace_loaded(self):
        current_url = self.page.url.lower()
        page_title = self.page.title().lower()
        if 'him' in current_url or 'code-workflow' in current_url or 'workflow' in current_url:
            return True

        try:
            self.assert_visible(self.HIM_WORKSPACE_HEADER)
            return True
        except Exception:
            pass

        try:
            self.assert_visible(self.WORKFLOW_HEADER)
            return True
        except Exception:
            pass

        raise AssertionError(f"HIM workspace not detected. URL: {current_url}, Title: {page_title}")

    def verify_ui_elements_present(self):
        elements_to_check = [
            (self.WORKSPACE_NAVIGATION, "Workspace navigation"),
            (self.DASHBOARD_CONTENT, "Dashboard content area"),
            (self.USER_MENU, "User menu"),
            (self.PATIENT_SEARCH, "Patient search"),
            (self.MEDICAL_RECORDS_TAB, "Medical Records tab"),
            (self.CODING_TAB, "Coding tab"),
            (self.QUALITY_TAB, "Quality tab"),
            (self.REPORTS_TAB, "Reports tab")
        ]

        for locator, description in elements_to_check:
            try:
                self.assert_visible(locator)
                print(f"[OK] {description} is visible")
            except Exception:
                print(f"[WARN] {description} not found or not visible")

    def verify_workspace_functionality(self):
        tabs = [
            (self.MEDICAL_RECORDS_TAB, "Medical Records"),
            (self.CODING_TAB, "Coding"),
            (self.QUALITY_TAB, "Quality"),
            (self.REPORTS_TAB, "Reports")
        ]

        for tab_locator, tab_name in tabs:
            try:
                tab_element = self.page.locator(tab_locator).first
                if tab_element.is_visible():
                    print(f"[OK] {tab_name} tab is accessible")
                else:
                    print(f"[WARN] {tab_name} tab not visible")
            except Exception:
                print(f"[WARN] {tab_name} tab not found")

    def get_workspace_title(self) -> str:
        try:
            if self.page.locator(self.WORKFLOW_HEADER).count() > 0:
                return self.page.locator(self.WORKFLOW_HEADER).first.inner_text()
        except Exception:
            pass
        try:
            if self.page.locator(self.HIM_WORKSPACE_HEADER).count() > 0:
                return self.page.locator(self.HIM_WORKSPACE_HEADER).first.inner_text()
        except Exception:
            pass
        return self.page.title()

    def logout_from_workspace(self):
        try:
            menu = self.page.locator(self.USER_MENU).first
            if menu.is_visible():
                menu.click()
                self.page.wait_for_timeout(500)
        except Exception:
            pass

        try:
            logout = self.page.locator(self.LOGOUT_BUTTON).first
            if logout.is_visible():
                logout.click()
                self.page.wait_for_load_state('networkidle')
                return True
        except Exception:
            pass

        raise AssertionError("Logout button not found")

    # --- Unassigned Episodes Actions ---
    def go_to_unassigned_episodes(self):
        try:
            link = self.page.locator(self.UNASSIGNED_EPISODES_LINK).first
            if link.is_visible():
                link.click()
                self.page.wait_for_load_state('networkidle')
                return True
        except Exception:
            pass

        try:
            link = self.page.get_by_role('link', name=re.compile(r'unassigned', re.I)).first
            if link.is_visible():
                link.click()
                self.page.wait_for_load_state('networkidle')
                return True
        except Exception:
            pass

        try:
            link = self.page.get_by_text('Unassigned', exact=False).first
            if link.is_visible():
                link.click()
                self.page.wait_for_load_state('networkidle')
                return True
        except Exception:
            pass

        for candidate in ["/unassigned", "/unassigned-episodes", "/unassigned-episodes/list"]:
            try:
                self.page.goto(f"{self.page.url.rstrip('/')}{candidate}")
                self.page.wait_for_load_state('networkidle')
                return True
            except Exception:
                continue

        try:
            nav = self.page.locator(self.WORKSPACE_NAVIGATION).first
            items = nav.locator('text=Unassigned')
            if items.count() > 0:
                items.first.click()
                self.page.wait_for_load_state('networkidle')
                return True
        except Exception:
            pass

        raise AssertionError("Could not navigate to Unassigned Episodes")

    def count_episodes(self) -> int:
        candidates = [self.EPISODE_ROW, "table tbody tr", "[data-testid*='episode-id']", ".episode-row"]
        for sel in candidates:
            try:
                count = self.page.locator(sel).count()
                if count > 0:
                    return count
            except Exception:
                continue

        try:
            total_label = self.page.get_by_text(re.compile(r"Total Episodes:\s*(\d+)", re.I)).first
            if total_label:
                text = total_label.inner_text()
                m = re.search(r"(\d+)", text)
                if m:
                    return int(m.group(1))
        except Exception:
            pass

        return 0

    def select_episode_checkbox(self, index: int = 1):
        if index < 1:
            raise ValueError('Episode index must be 1 or greater')

        # Wait for the episode list or checkbox controls to appear first
        try:
            self.page.wait_for_selector("input[type='checkbox']", timeout=15000)
        except Exception:
            pass

        row_selectors = [self.EPISODE_ROW, "table tbody tr", "[data-testid*='episode-id']", ".episode-row"]
        for sel in row_selectors:
            try:
                rows = self.page.locator(sel)
                count = rows.count()
                print(f"DEBUG: row selector '{sel}' matched {count} rows")
                if count >= index:
                    row = rows.nth(index - 1)
                    checkbox = row.locator("input[type='checkbox']")
                    if checkbox.count() > 0 and checkbox.first.is_visible():
                        checkbox.first.scroll_into_view_if_needed()
                        checkbox.first.check()
                        return True
            except Exception:
                continue

        candidates = ["table tbody tr input[type='checkbox']", "[data-testid*='episode'] input[type='checkbox']", ".episode-row input[type='checkbox']", "input[type='checkbox']"]
        for sel in candidates:
            try:
                locator = self.page.locator(sel)
                count = locator.count()
                print(f"DEBUG: checkbox selector '{sel}' matched {count} elements")
                if count >= index:
                    checkbox = locator.nth(index - 1)
                    if checkbox.is_visible():
                        checkbox.scroll_into_view_if_needed()
                        checkbox.check()
                        return True
            except Exception:
                continue

        raise AssertionError(f"Could not find or select episode checkbox at index {index}")

    def assert_reassign_button_visible(self):
        self.assert_visible(self.REASSIGN_BUTTON)

    def click_reassign_button(self):
        button = self.page.locator(self.REASSIGN_BUTTON).first
        button.scroll_into_view_if_needed()
        button.click()
        self.page.wait_for_load_state('networkidle')
        return True

    def verify_reassign_popup_displayed(self):
        try:
            self.page.locator(self.REASSIGN_DIALOG).first.wait_for(state="visible", timeout=5000)
            return True
        except Exception:
            raise AssertionError("Reassign dialog did not appear")

    def select_first_queue_option(self):
        try:
            queue = self.page.locator(self.QUEUE_DROPDOWN).first
            if queue.is_visible():
                options = queue.locator('option')
                if options.count() > 1:
                    options.nth(1).click()
                    return True
                queue.select_option(index=0)
                return True
        except Exception:
            pass
        raise AssertionError("Could not select a queue option")

    def select_first_coder_option(self):
        try:
            select = self.page.locator(self.CODER_DROPDOWN).first
            if select.is_visible():
                options = select.locator('option')
                if options.count() > 1:
                    options.nth(1).click()
                    return True
                select.select_option(index=0)
                return True
        except Exception:
            pass

        try:
            textbox = self.page.locator(self.CODER_INPUT).first
            if textbox.is_visible():
                textbox.click()
                textbox.press('ArrowDown')
                textbox.press('Enter')
                return True
        except Exception:
            pass

        raise AssertionError("Could not select the first coder option")

    def select_coder_by_name(self, coder_name: str):
        return self.select_coder(coder_name)

    def select_coder(self, coder_name: str):
        input_el = self.page.locator(self.CODER_INPUT).first
        input_el.scroll_into_view_if_needed()
        input_el.click()
        input_el.fill(coder_name)
        self.page.wait_for_timeout(500)

        option_selector = '#react-select-3-option-0, [id^="react-select-3-option"]'
        option = self.page.locator(option_selector).first
        option.wait_for(state='visible', timeout=5000)
        option.click(force=True)
        return True

    def click_confirm_assignment(self):
        confirm = self.page.locator(self.CONFIRM_BUTTON).first
        if confirm.is_visible():
            confirm.click()
            self.page.wait_for_load_state('networkidle')
            return True
        raise AssertionError("Confirm Assignment button not found")

    def verify_reassignment_success(self):
        try:
            self.assert_visible(self.REASSIGN_SUCCESS_TEXT)
            return True
        except Exception:
            try:
                alert = self.page.get_by_role('alert').first
                if alert.is_visible():
                    return True
            except Exception:
                pass
            raise AssertionError("Reassignment success message not detected")


def run_reassign_flow(username: str, password: str, env: str = "dev"):
    from playwright.sync_api import sync_playwright
    from config.settings import Settings
    from pages.login_page import LoginPage

    settings = Settings(env=env)
    headless = settings.headless
    headless_env = None
    if "HEADLESS" in __import__("os").environ:
        headless_env = __import__("os").environ["HEADLESS"].lower() in ("1", "true", "yes")
        headless = headless_env

    with sync_playwright() as playwright:
        browser_type = getattr(playwright, settings.browser)
        browser = browser_type.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()

        try:
            print("Navigating to base URL...")
            page.goto(settings.base_url)
            print("Opened base URL")

            login_page = LoginPage(page)
            workflow_page = WorkflowPage(page)

            print("Performing login...")
            login_page.login(username, password)
            print("Clicked Log In")

            if workflow_page.click_code_workflow_image():
                print("Clicked Code Workflow image")
            else:
                print("Code Workflow image not found, navigating to HIM workspace")
                workflow_page.navigate_to_him_workspace()
                print("Clicked HIM Workspace link")

            workflow_page.go_to_unassigned_episodes()
            print("Opened Unassigned Episodes")

            success = workflow_page.select_episode_checkbox(1)
            print(f"select_episode_checkbox -> success={success}")

            print("Waiting briefly for action toolbar to appear...")
            page.wait_for_timeout(1000)

            workflow_page.click_reassign_button()
            print("Clicked Re-assign")

            workflow_page.select_coder_by_name("prabhu")
            print("Selected coder prabhu")

            workflow_page.click_confirm_assignment()
            print("Clicked confirm assignment")

            if workflow_page.verify_reassignment_success():
                print("Reassign dialog closed after confirm. Assignment likely completed.")
            else:
                print("Reassignment may not have completed successfully.")

        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    import os
    user = os.getenv("IMEDX_USERNAME", "Sai")
    pwd = os.getenv("IMEDX_PASSWORD", "Imedx@123")
    env = os.getenv("ENV", "dev")
    run_reassign_flow(user, pwd, env)
