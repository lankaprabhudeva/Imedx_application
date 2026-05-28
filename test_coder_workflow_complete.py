"""
Complete Playwright script for iMedX Coder Workspace workflow.

Workflow:
1. Login to iMedX internal application
2. Navigate to Code Workflow → Coder Workspace
3. Apply Outstanding filter
4. Open an outstanding episode
5. Launch Code Assist and enter diagnosis code Q87.19
6. Confirm DRG
7. Complete coding
8. Close browser
"""

from playwright.sync_api import sync_playwright
from pages.login_page import LoginPage
from pages.unassignepisode_page import UnassignedEpisodePage
from pages.codingcomplete import CodingCompletePage


def run_coder_workflow() -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        login_page = LoginPage(page)
        navigation_page = UnassignedEpisodePage(page)
        coding_page = CodingCompletePage(page)

        try:
            print("Step 1: Navigating to iMedX application...")
            login_page.open_login_page("https://hcs-internal.imedx.com.au/")

            print("Step 2: Logging in...")
            login_page.login("Sai", "Imedx@123")
            login_page.verify_login_success()
            print("  ✓ Login successful")

            print("Step 3: Opening Code Workflow and Coder Workspace...")
            if not (navigation_page.open_code_workflow() or navigation_page.open_him_workspace()):
                raise AssertionError("Could not open Code Workflow or HIM Workspace")
            if not navigation_page.open_coder_workspace():
                raise AssertionError("Could not open Coder Workspace")
            print("  ✓ Coder Workspace opened")

            print("Step 4: Applying Outstanding filter...")
            if not coding_page.apply_outstanding_filter():
                raise AssertionError("Could not apply Outstanding filter")
            print("  ✓ Outstanding filter applied")

            print("Step 5: Opening the first outstanding episode...")
            if not coding_page.open_first_outstanding_episode():
                raise AssertionError("Could not open first outstanding episode")
            print("  ✓ Outstanding episode opened")

            print("Step 6: Opening Code Assist...")
            if not coding_page.open_code_assist():
                raise AssertionError("Could not open Code Assist")
            coding_page.close_popup_if_visible()
            print("  ✓ Code Assist ready")

            print("Step 7: Entering principal diagnosis code Q87.19...")
            if not coding_page.enter_principal_diagnosis("Q87.19"):
                raise AssertionError("Could not enter principal diagnosis code")
            print("  ✓ Principal diagnosis entered")

            print("Step 8: Confirming DRG...")
            if not coding_page.confirm_drg():
                raise AssertionError("Could not confirm DRG")
            print("  ✓ DRG confirmed")

            print("Step 9: Completing coding...")
            if not coding_page.complete_coding():
                raise AssertionError("Could not click Coding Complete")
            print("  ✓ Coding Complete clicked")

            print("\n✅ Coding workflow completed successfully.")

        except Exception as error:
            print(f"\n❌ Workflow failed with error: {error}")
            try:
                page.screenshot(path='workflow_failure.png')
                print("Debug screenshot saved: workflow_failure.png")
            except Exception:
                pass
            raise

        finally:
            print("\nClosing browser...")
            context.close()
            browser.close()
            print("Browser closed")


if __name__ == '__main__':
    run_coder_workflow()
