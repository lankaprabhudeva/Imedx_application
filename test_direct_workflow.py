"""Direct test using the working code snippet provided"""
import re
from playwright.sync_api import sync_playwright


def run(playwright) -> None:
    # Launch browser
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # Open application
    print("Opening application...")
    page.goto("https://hcs-internal.imedx.com.au/")

    # Login
    print("Logging in...")
    page.get_by_role("textbox", name="Username").fill("Sai")
    page.get_by_role("textbox", name="Password").fill("Imedx@123")
    page.get_by_role("button", name="Log In").click()
    page.wait_for_load_state('networkidle')

    # Navigate to Code Workflow
    print("Navigating to Code Workflow...")
    page.get_by_role("img", name="Code Workflow").click()
    page.wait_for_load_state('networkidle')
    
    print("Opening Coder Workspace...")
    page.get_by_role("link", name="Coder Workspace").click()
    page.wait_for_load_state('networkidle')

    # Apply Outstanding filter
    print("Applying Outstanding filter...")
    page.locator(".css-8mmkcg").click()
    page.get_by_role("option", name="Outstanding").click()
    page.get_by_role("button", name="Apply").click()
    page.wait_for_load_state('networkidle')

    # Open first available outstanding episode dynamically
    print("Opening first outstanding episode...")
    page.get_by_role("cell").first.click()
    page.wait_for_load_state('networkidle')

    # Open Code Assist
    print("Opening Code Assist...")
    page.get_by_text("Code Assist").click()
    page.wait_for_load_state('networkidle')

    # Close popup if visible
    try:
        page.get_by_role("button", name="Cancel").click(timeout=3000)
    except:
        pass

    # Enter principal diagnosis code
    print("Entering principal diagnosis code...")
    principal_input = page.locator('input[name="principal"]')
    principal_input.click()
    principal_input.fill("Q87.19")
    principal_input.press("Enter")
    page.wait_for_timeout(500)

    # Confirm DRG
    print("Confirming DRG...")
    page.get_by_role("button", name="Confirm DRGconfirm").click()
    page.wait_for_load_state('networkidle')

    # Open My Actions
    print("Opening My Actions...")
    page.get_by_role("button", name="My Actions").click()
    page.wait_for_load_state('networkidle')

    # Navigate to Coders section
    print("Navigating to Coders...")
    page.get_by_role("button", name="Auditors").click()
    page.wait_for_timeout(500)
    page.get_by_role("button", name="Coders").click()
    page.wait_for_load_state('networkidle')

    # Search coder
    print("Searching for coder...")
    coder_search = page.get_by_role("textbox", name="Search coders...")
    coder_search.fill("prabhu")
    page.wait_for_timeout(500)

    # Select coder
    print("Selecting coder...")
    page.get_by_role("radio").check()
    page.wait_for_timeout(300)

    # Enter reason/comment
    print("Entering reason...")
    reason_box = page.get_by_role(
        "textbox",
        name="Enter reason for review..."
    )

    reason_box.fill(
        "Sai coder sends this episode to coder Prabhu"
    )
    page.wait_for_timeout(300)

    # Send episode
    print("Sending episode...")
    page.get_by_role("button", name="Send", exact=True).click()
    page.wait_for_load_state('networkidle')

    print("SUCCESS: Workflow completed!")

    # Close browser
    context.close()
    browser.close()


if __name__ == '__main__':
    with sync_playwright() as playwright:
        run(playwright)
