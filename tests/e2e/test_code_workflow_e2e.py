"""
Requirement: Reassign an unassigned episode to coder prabhu after login.

User Story:
As a coder, I want to open Code Workflow after login, navigate to HIM Workspace, go to Unassigned Episodes,
select an episode, open the Reassign popup, type prabhu into the coder dropdown/input, and confirm DRG.
"""

from pages.login_page import LoginPage
from pages.workflow_page import WorkflowPage
from pathlib import Path
import pytest


REPORTS_DIR = Path("reports/e2e")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def _screenshot(page, name: str):
    path = REPORTS_DIR / f"{name}.png"
    page.screenshot(path=str(path))
    return path


def test_reassign_popup_opens_after_episode_selection(page, app_settings):
    login_page = LoginPage(page)
    workflow_page = WorkflowPage(page)

    try:
        login_page.open_login_page(app_settings.base_url)
        login_page.login("Sai", "Imedx@123")
        login_page.verify_login_success()

        workflow_page.click_breadcrumb_menu()
        workflow_page.click_him_workspace_menu()
        assert workflow_page.verify_him_workspace_loaded()

        workflow_page.go_to_unassigned_episodes()

        count = workflow_page.count_episodes()
        if count < 2:
            import pytest

            pytest.skip("Less than 2 unassigned episodes found in environment — cannot verify second-row selection")

        workflow_page.select_episode_checkbox(2)
        workflow_page.assert_reassign_button_visible()
        workflow_page.click_reassign_button()
        assert workflow_page.verify_reassign_popup_displayed()

    except Exception:
        _screenshot(page, "reassign_popup_failure")
        raise


def test_reassign_unassigned_episode_successfully(page, app_settings):
    login_page = LoginPage(page)
    workflow_page = WorkflowPage(page)

    try:
        # Login
        login_page.open_login_page(app_settings.base_url)
        login_page.login("Sai", "Imedx@123")
        login_page.verify_login_success()

        # Navigate to HIM workspace using breadcrumb
        workflow_page.click_breadcrumb_menu()
        workflow_page.click_him_workspace_menu()
        assert workflow_page.verify_him_workspace_loaded()

        # Go to unassigned episodes
        workflow_page.go_to_unassigned_episodes()

        # Check episode count and skip if there are not enough episodes for the third selection
        count = workflow_page.count_episodes()
        if count < 3:
            import pytest

            pytest.skip("Less than 3 unassigned episodes found in environment — seed test data before running this E2E")

        # Select the third episode checkbox
        workflow_page.select_episode_checkbox(3)

        # Verify the Re-assign button is displayed
        workflow_page.assert_reassign_button_visible()

        # Click the Re-assign button and verify popup
        workflow_page.click_reassign_button()
        assert workflow_page.verify_reassign_popup_displayed()

        # Select the first queue option and first coder option
        workflow_page.select_first_queue_option()
        workflow_page.select_first_coder_option()

        # Confirm assignment and verify success
        workflow_page.click_confirm_assignment()
        assert workflow_page.verify_reassignment_success()

    except Exception:
        _screenshot(page, "code_workflow_failure")
        raise


def test_reassign_unassigned_episode_to_prabhu(page, app_settings):
    login_page = LoginPage(page)
    workflow_page = WorkflowPage(page)

    try:
        login_page.open_login_page(app_settings.base_url)
        login_page.login("Sai", "Imedx@123")
        login_page.verify_login_success()

        # Navigate into Code Workflow / HIM workspace
        if not workflow_page.click_code_workflow_image():
            workflow_page.click_breadcrumb_menu()
            workflow_page.click_him_workspace_menu()

        assert workflow_page.verify_him_workspace_loaded()

        workflow_page.go_to_unassigned_episodes()

        count = workflow_page.count_episodes()
        if count < 1:
            pytest.skip("No unassigned episodes found in environment")

        workflow_page.select_episode_checkbox(1)
        workflow_page.assert_reassign_button_visible()
        workflow_page.click_reassign_button()
        assert workflow_page.verify_reassign_popup_displayed()

        assert workflow_page.select_coder_by_name("prabhu")
        workflow_page.click_confirm_assignment()
        assert workflow_page.verify_reassignment_success()

    except Exception:
        _screenshot(page, "reassign_to_prabhu_failure")
        raise
