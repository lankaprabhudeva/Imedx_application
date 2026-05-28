"""Simple script to inspect the Coder Workspace page"""

from playwright.sync_api import sync_playwright


def inspect_coder_workspace():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        try:
            # Navigate to login
            print("Navigating to iMedX...")
            page.goto("https://hcs-internal.imedx.com.au/")
            page.wait_for_selector('form.login-form', timeout=20000)

            # Login
            print("Logging in...")
            username_input = page.locator('input#username')
            password_input = page.locator('input#password')
            login_button = page.locator('button.Login-btn, button[type="submit"]')

            username_input.evaluate('el => el.removeAttribute("disabled")')
            username_input.click(force=True)
            username_input.fill("Sai", force=True)

            password_input.evaluate('el => el.removeAttribute("disabled")')
            password_input.click(force=True)
            password_input.fill("Imedx@123", force=True)

            login_button.evaluate('el => el.removeAttribute("disabled")')
            login_button.click(force=True)

            page.wait_for_load_state('networkidle', timeout=20000)
            page.wait_for_selector('form.login-form', state='detached', timeout=15000)
            print("[OK] Logged in")

            # Navigate to Coder Workspace
            print("Navigating to Coder Workspace...")
            page.goto("https://hcs-internal.imedx.com.au/coder_workspace", wait_until="networkidle", timeout=35000)
            page.wait_for_load_state('domcontentloaded', timeout=10000)
            page.wait_for_timeout(2000)

            print("[OK] Coder Workspace loaded")
            
            # Save screenshot
            page.screenshot(path="coder_workspace_inspection.png")
            print("[OK] Screenshot saved: coder_workspace_inspection.png")
            
            # Print page content for inspection
            print("\n" + "="*80)
            print("PAGE BODY HTML (First 3000 chars):")
            print("="*80)
            body_html = page.evaluate('() => document.body.innerHTML')
            print(body_html[:3000])
            print("\n" + "="*80)
            print("Page title:", page.title())
            print("Page URL:", page.url)
            print("="*80)
            
            # Look for specific elements
            print("\nSearching for key elements...")
            
            # Look for filter-related elements
            try:
                filters = page.locator('[class*="filter"]').all()
                print("  Elements with 'filter' in class:", len(filters))
            except:
                pass
            
            # Look for buttons
            try:
                buttons = page.locator('button').all()
                print("  Total buttons:", len(buttons))
                for i, btn in enumerate(buttons[:10]):
                    text = btn.text_content() or btn.get_attribute('aria-label') or btn.get_attribute('title') or ''
                    print("    Button", i, ":", text[:50])
            except:
                pass
            
            # Look for "Outstanding" text
            try:
                outstanding = page.locator('text=Outstanding').all()
                print("  'Outstanding' text occurrences:", len(outstanding))
            except:
                pass
            
            # Look for table/rows
            try:
                rows = page.locator('tr, [role="row"]').all()
                print("  Table rows or row-like elements:", len(rows))
            except:
                pass
            
            print("\nInspection complete. Keeping browser open for manual inspection...")
            print("Press Ctrl+C or close the browser to exit.")
            
            input("Press Enter to close browser...")

        finally:
            browser.close()


if __name__ == "__main__":
    inspect_coder_workspace()
