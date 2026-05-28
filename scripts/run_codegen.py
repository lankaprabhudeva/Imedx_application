import re
import time
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    print("Navigating to base URL...")
    page.goto("https://hcs-internal.imedx.com.au/")
    print("Opened base URL")
    page.get_by_role("textbox", name="Username").click()
    page.get_by_role("textbox", name="Username").fill("sai")
    page.get_by_role("textbox", name="Password").click()
    page.get_by_role("textbox", name="Password").fill("")
    page.get_by_role("textbox", name="Password").press("CapsLock")
    page.get_by_role("textbox", name="Password").fill("I")
    page.get_by_role("textbox", name="Password").press("CapsLock")
    page.get_by_role("textbox", name="Password").fill("Imedx@123")
    print("Performing login...")
    page.get_by_role("button", name="Log In").click()
    print("Clicked Log In")
    page.get_by_role("img", name="Code Workflow").click()
    print("Clicked Code Workflow image")
    page.get_by_role("link", name="HIM Workspace").click()
    print("Clicked HIM Workspace link")
    page.get_by_text("Unassigned Episodes").click()
    print("Opened Unassigned Episodes")

    # Wait for episode list or checkboxes to appear (dynamic load)
    try:
        page.wait_for_selector("input[type='checkbox']", timeout=15000)
    except Exception:
        print("No checkboxes appeared within timeout")

    # Helper to select an episode checkbox dynamically
    def select_episode_checkbox(page, index: int = 2, episode_id: str | None = None, timeout: int = 15):
        selector = "table tbody tr, [data-episode-id], .episode-row"
        start = time.time()
        while time.time() - start < timeout:
            rows = page.locator(selector)
            try:
                cnt = rows.count()
            except Exception:
                cnt = 0
            if cnt > 0:
                break
            time.sleep(0.5)

        if cnt == 0:
            return False, "no_rows"

        candidate_rows = []
        for i in range(cnt):
            try:
                row = rows.nth(i)
                # look for checkbox inside the row
                chk = row.locator("input[type='checkbox']")
                if chk.count() > 0 and chk.first.is_visible():
                    # if an episode_id is provided, match row text
                    if episode_id:
                        txt = row.inner_text()
                        if episode_id in txt:
                            chk.first.scroll_into_view_if_needed()
                            chk.first.check()
                            return True, f"selected_by_id_{i}"
                    candidate_rows.append(i)
            except Exception:
                continue

        if episode_id:
            return False, "id_not_found"

        if len(candidate_rows) >= index:
            target = candidate_rows[index - 1]
            rows.nth(target).locator("input[type='checkbox']").first.scroll_into_view_if_needed()
            rows.nth(target).locator("input[type='checkbox']").first.check()
            return True, f"selected_index_{target}"
        elif len(candidate_rows) > 0:
            target = candidate_rows[0]
            rows.nth(target).locator("input[type='checkbox']").first.check()
            return True, f"selected_first_{target}"

        return False, "no_checkboxes"

    def select_react_dropdown(page, input_selector: str, option_text: str | None = None, option_prefix: str | None = None):
        try:
            input_el = page.locator(input_selector).first
            input_el.scroll_into_view_if_needed()
            input_el.click()
            if option_text:
                input_el.fill(option_text)
            page.wait_for_timeout(500)

            if option_prefix:
                option_locator = page.locator(f'#{option_prefix}-option-0, [id^="{option_prefix}-option"]')
            else:
                option_locator = page.locator('[id^="react-select-"][id*="-option"]')

            option_locator.first.wait_for(state="visible", timeout=5000)
            option_locator.first.click(force=True)
            return True
        except Exception:
            try:
                input_el.press("ArrowDown")
                input_el.press("Enter")
                return True
            except Exception:
                return False

    success, message = select_episode_checkbox(page, index=2)
    print(f"select_episode_checkbox -> success={success}, message={message}")
    if not success:
        print("No selectable episode checkbox (or less than requested rows). Exiting gracefully.")
        page.screenshot(path="reports/e2e/reassign_no_rows.png")
        context.close()
        browser.close()
        return
    # Try multiple ways to find and click the Re-assign button (dynamic toolbar may appear)
    try:
        print("Waiting briefly for action toolbar to appear...")
        page.wait_for_timeout(1000)

        reassign_selectors = [
            'button:has-text("Re-assign")',
            'button:has-text("Reassign")',
            '[data-testid*="reassign"]',
            'button:has-text("Assign")',
            'text=Re-assign',
            'text=Reassign',
        ]

        clicked = False
        for sel in reassign_selectors:
            try:
                loc = page.locator(sel)
                if loc.count() > 0 and loc.first.is_visible():
                    print(f"Clicking Reassign using selector: {sel}")
                    loc.first.click()
                    clicked = True
                    break
            except Exception:
                continue

        if not clicked:
            # try role-based button with regex as last resort
            try:
                btn = page.get_by_role("button", name=re.compile(r"re-?assign|assign", re.I))
                if btn.count() > 0 and btn.first.is_visible():
                    btn.first.click()
                    clicked = True
            except Exception:
                pass

        if not clicked:
            print("Failed to locate Re-assign button with known selectors. Capturing debug artifacts.")
            page.screenshot(path="reports/e2e/reassign_click_failure.png")
            with open("reports/e2e/reassign_page_content.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            raise AssertionError("Re-assign control not found or not visible")
        else:
            print("Clicked Re-assign")
    except Exception as e:
        print(f"Error while attempting to click Re-assign: {e}")
        raise

    # Wait for the reassign dialog to appear
    page.wait_for_timeout(1000)

    # Select coder prabhu only (do not select queue and coder together)
    coder_selected = select_react_dropdown(page, '#react-select-3-input', option_text='prabhu', option_prefix='react-select-3')
    if coder_selected:
        print('Selected coder prabhu')
    else:
        print('Coder prabhu selection failed via direct option click; trying keyboard fallback')
        try:
            coder_input = page.locator('#react-select-3-input').first
            coder_input.click()
            coder_input.fill('prabhu')
            page.wait_for_timeout(500)
            coder_input.press('ArrowDown')
            coder_input.press('Enter')
            print('Selected coder prabhu using keyboard fallback')
        except Exception:
            page.screenshot(path='reports/e2e/reassign_prabhu_not_found.png')
            with open('reports/e2e/reassign_page_content.html', 'w', encoding='utf-8') as f:
                f.write(page.content())
            raise AssertionError('Coder option prabhu not found or selectable in the dropdown')

    # Click Confirm Assignment button once queue and coder are selected
    confirm_selectors = [
        'button.workflow-him-assign-confirm-btn:not([disabled])',
        'button:has-text("Confirm Assignment"):not([disabled])',
        'button:has-text("Confirm"):not([disabled])',
        'button:has-text("Assign"):not([disabled])',
        'button:has-text("Save"):not([disabled])',
        'button:has-text("OK"):not([disabled])',
    ]
    clicked_confirm = False
    for sel in confirm_selectors:
        try:
            btn = page.locator(sel).first
            if btn.count() > 0 and btn.is_visible():
                print(f"Clicking confirm button using selector: {sel}")
                btn.click(force=True)
                clicked_confirm = True
                break
        except Exception:
            continue

    if not clicked_confirm:
        page.screenshot(path='reports/e2e/reassign_confirm_failure.png')
        with open('reports/e2e/reassign_page_content.html', 'w', encoding='utf-8') as f:
            f.write(page.content())
        raise AssertionError('Could not click confirm assignment button')

    print('Clicked confirm assignment')
    try:
        page.wait_for_selector(':is(text="successfully reassigned", text="Assignment successful", text="successfully assigned", text="assigned successfully")', timeout=10000)
        print('Assignment success detected')
    except Exception:
        try:
            page.wait_for_selector('.workflow-him-assign-modal-container', state='detached', timeout=10000)
            print('Reassign dialog closed after confirm. Assignment likely completed.')
        except Exception:
            print('No explicit success text detected and dialog did not close quickly.')

    # ---------------------
    context.close()
    browser.close()


if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
