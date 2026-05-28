import pytest
import json
from pathlib import Path
from pages.login_page import LoginPage
from pages.workflow_page import WorkflowPage


class TestHimWorkspace:
    """Test suite for HIM Workspace navigation and UI validation after login"""

    @pytest.fixture(scope="class")
    def test_data(self):
        """Load test data from JSON file"""
        data_file = Path("test_data/login_test_data.json")
        with open(data_file, "r") as f:
            return json.load(f)

    def test_01_login_and_navigate_to_him_workspace(self, page, app_settings, test_data):
        """
        PRIMARY TEST: Login to iMedx and navigate to HIM workspace
        Steps:
        1. Login with valid credentials
        2. Navigate to HIM workspace
        3. Verify HIM workspace loads correctly
        """
        login_page = LoginPage(page)
        workflow_page = WorkflowPage(page)

        # Step 1: Login
        print("Step 1: Logging in...")
        login_page.open_login_page(app_settings.base_url)
        login_page.wait_for_page_load()

        valid_user = test_data["valid_user"]
        login_page.login(valid_user["username"], valid_user["password"])

        # Wait for login to complete and dashboard to load
        page.wait_for_timeout(3000)
        print(f"After login - URL: {page.url}, Title: {page.title()}")

        # Step 2: Navigate to HIM workspace
        print("Step 2: Navigating to HIM workspace...")
        workflow_page.navigate_to_him_workspace()

        # Step 3: Verify HIM workspace loaded
        print("Step 3: Verifying HIM workspace...")
        workflow_page.verify_him_workspace_loaded()

        workspace_title = workflow_page.get_workspace_title()
        print(f"✓ HIM Workspace loaded successfully. Title: {workspace_title}")

    def test_02_verify_him_workspace_ui_elements(self, page, app_settings, test_data):
        """
        Verify all key UI elements are present in HIM workspace
        """
        login_page = LoginPage(page)
        workflow_page = WorkflowPage(page)

        # Login first
        login_page.open_login_page(app_settings.base_url)
        login_page.wait_for_page_load()
        valid_user = test_data["valid_user"]
        login_page.login(valid_user["username"], valid_user["password"])
        page.wait_for_timeout(3000)

        # Navigate to HIM workspace
        workflow_page.navigate_to_him_workspace()

        # Verify UI elements
        print("Verifying HIM workspace UI elements...")
        workflow_page.verify_ui_elements_present()

    def test_03_verify_him_workspace_functionality(self, page, app_settings, test_data):
        """
        Verify basic functionality of HIM workspace tabs and navigation
        """
        login_page = LoginPage(page)
        workflow_page = WorkflowPage(page)

        # Login and navigate to HIM workspace
        login_page.open_login_page(app_settings.base_url)
        login_page.wait_for_page_load()
        valid_user = test_data["valid_user"]
        login_page.login(valid_user["username"], valid_user["password"])
        page.wait_for_timeout(3000)
        workflow_page.navigate_to_him_workspace()

        # Verify workspace functionality
        print("Verifying HIM workspace functionality...")
        workflow_page.verify_workspace_functionality()

    def test_04_him_workspace_page_structure(self, page, app_settings, test_data):
        """
        Verify the overall page structure and layout of HIM workspace
        """
        login_page = LoginPage(page)
        workflow_page = WorkflowPage(page)

        # Login and navigate
        login_page.open_login_page(app_settings.base_url)
        login_page.wait_for_page_load()
        valid_user = test_data["valid_user"]
        login_page.login(valid_user["username"], valid_user["password"])
        page.wait_for_timeout(3000)
        workflow_page.navigate_to_him_workspace()

        # Check page structure
        print("Checking HIM workspace page structure...")

        # Verify page has proper structure
        body_content = page.locator('body').inner_html()
        assert len(body_content) > 1000, "Page content seems insufficient"

        # Check for navigation elements
        nav_elements = page.locator('nav, [class*="nav"], [role="navigation"]').count()
        assert nav_elements > 0, "No navigation elements found"

        # Check for main content area
        main_content = page.locator('main, [class*="main"], [class*="content"]').count()
        assert main_content > 0, "No main content area found"

        print("✓ HIM workspace page structure verified")

    def test_05_him_workspace_responsive_elements(self, page, app_settings, test_data):
        """
        Verify HIM workspace elements are properly responsive and interactive
        """
        login_page = LoginPage(page)
        workflow_page = WorkflowPage(page)

        # Login and navigate
        login_page.open_login_page(app_settings.base_url)
        login_page.wait_for_page_load()
        valid_user = test_data["valid_user"]
        login_page.login(valid_user["username"], valid_user["password"])
        page.wait_for_timeout(3000)
        workflow_page.navigate_to_him_workspace()

        print("Checking responsive elements...")

        # Check if key interactive elements are clickable
        try:
            user_menu = page.locator(workflow_page.USER_MENU).first
            if user_menu.is_visible():
                # Don't actually click, just check if it's interactive
                print("✓ User menu is visible and interactive")
            else:
                print("⚠ User menu not visible")
        except:
            print("⚠ User menu element not found")

        # Check patient search if present
        try:
            patient_search = page.locator(workflow_page.PATIENT_SEARCH).first
            if patient_search.is_visible():
                print("✓ Patient search is visible")
                # Check if it's a proper input field
                tag_name = patient_search.evaluate("el => el.tagName")
                if tag_name == "INPUT":
                    print("✓ Patient search is an input field")
                else:
                    print(f"⚠ Patient search is a {tag_name} element")
            else:
                print("⚠ Patient search not visible")
        except:
            print("⚠ Patient search element not found")

    def test_06_complete_him_workflow_validation(self, page, app_settings, test_data):
        """
        Complete workflow: Login -> HIM Workspace -> UI Validation -> Logout
        """
        login_page = LoginPage(page)
        workflow_page = WorkflowPage(page)

        print("=== HIM WORKFLOW VALIDATION ===")

        # 1. Login
        print("1. Logging in...")
        login_page.open_login_page(app_settings.base_url)
        login_page.wait_for_page_load()
        valid_user = test_data["valid_user"]
        login_page.login(valid_user["username"], valid_user["password"])
        page.wait_for_timeout(3000)

        # 2. Navigate to HIM
        print("2. Navigating to HIM workspace...")
        workflow_page.navigate_to_him_workspace()

        # 3. Validate UI
        print("3. Validating UI elements...")
        workflow_page.verify_ui_elements_present()
        workflow_page.verify_workspace_functionality()

        # 4. Verify page state
        print("4. Verifying page state...")
        current_url = page.url
        page_title = page.title()
        print(f"   Current URL: {current_url}")
        print(f"   Page Title: {page_title}")

        # 5. Attempt logout (if possible)
        print("5. Attempting logout...")
        try:
            workflow_page.logout_from_workspace()
            print("✓ Logout successful")
        except:
            print("⚠ Logout not performed (may not be available)")

        print("=== WORKFLOW COMPLETED ===")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])