from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from playwright.sync_api import sync_playwright

from pages.filters_search.Coderworkspace_filter import CoderworkspaceFilterPage
from pages.login_page import LoginPage


def _login_form_visible(page) -> bool:
    """Check if login form is visible."""
    try:
        return (
            page.get_by_placeholder(re.compile(r"Username|Email", re.I)).count() > 0
            and page.get_by_placeholder(re.compile(r"Password", re.I)).count() > 0
        )
    except Exception:
        return False


def _login_with_retry(login_page: LoginPage, username: str, password: str, max_retries: int = 3) -> None:
    """Login with retry logic."""
    for attempt in range(max_retries):
        try:
            login_page.login(username, password)
            login_page.page.wait_for_load_state("networkidle", timeout=5000)
            if not _login_form_visible(login_page.page):
                return
        except Exception as exc:
            if attempt == max_retries - 1:
                raise
            login_page.page.reload()


class CodeAccelerateEpisodeListFilterPage(CoderworkspaceFilterPage):
    """Filter automation for Code Accelerate > Episode List."""

    TARGET_LINKS = [
        'a:has-text("Episode List")',
        'button:has-text("Episode List")',
        'p:has-text("Episode List")',
        'span:has-text("Episode List")',
        'div:has-text("Episode List")',
        'text=Episode List',
    ]

    # Filter names supported by this page
    FILTERS = {
        "Episode Identifier",
        "MRN/UR",
        "Admission Date From",
        "Admission Date To",
        "Discharge Date From",
        "Discharge Date To",
        "Speciality",
        "Status",
        "Health Fund Contract",
        "DRG",
        "Document Types",
        "LOS Operator",
        "Length of Stay (LOS)",
    }

    DEFAULT_FILTERS = [
        "Episode Identifier",
        "MRN/UR",
        "Speciality",
        "Status",
        "LOS Operator",
    ]

    def _code_accelerate_filter_available(self) -> bool:
        """Check if Code Accelerate Episode List filter is available."""
        checks = [
            self.page.get_by_text(re.compile(r"Code Accelerate", re.I)).first,
            self.page.get_by_text(re.compile(r"Episode List", re.I)).first,
            self.page.get_by_text(re.compile(r"Episode Filters", re.I)).first,
            self.page.get_by_text(re.compile(r"Episode Identifier", re.I)).first,
        ]
        for check in checks:
            try:
                if check.count() > 0 and check.is_visible():
                    return True
            except Exception:
                continue
        return False

    def _filter_card(self, filter_name: str):
        """Get the filter card container for a given filter name."""
        # Try to find by label text
        labels = self.page.get_by_text(filter_name, exact=True).all()
        for label in labels:
            try:
                if label.is_visible():
                    # Get the parent container (usually a div wrapping the label and input)
                    return label.locator("xpath=ancestor::div[@class and contains(@class, 'filter') or contains(@class, 'input') or contains(@class, 'field')]").first
            except Exception:
                continue
        return None

    def _collect_select_options(self, filter_name: str) -> list[str]:
        """Collect available dropdown options for a select filter."""
        options = []
        try:
            # Find the filter input/dropdown
            filter_input = self.page.get_by_placeholder(re.compile(filter_name, re.I)).first
            if not filter_input.count():
                filter_input = self.page.get_by_text(filter_name).first
            
            # Click to open dropdown
            if filter_input.count():
                filter_input.click()
                self.page.wait_for_timeout(300)
            
            # Collect visible options
            option_elements = self.page.locator("div[role='option'], li[role='option'], [data-value]").all()
            for opt in option_elements:
                try:
                    text = opt.text_content().strip()
                    if text:
                        options.append(text)
                except Exception:
                    continue
            
            # Click elsewhere to close dropdown
            self.page.locator("body").click()
            self.page.wait_for_timeout(200)
        except Exception as exc:
            print(f"Warning: Could not collect options for {filter_name}: {exc}")
        
        return list(set(options))

    def apply_named_filter(self, filter_name: str) -> None:
        """Apply a specific filter by name."""
        if filter_name not in self.FILTERS:
            raise ValueError(f"Unknown filter: {filter_name}")
        
        print(f"Applying filter: {filter_name}")
        
        # Handle text input filters
        if filter_name in ["Episode Identifier", "MRN/UR", "Length of Stay (LOS)"]:
            self._fill_text_filter(filter_name)
        
        # Handle date filters
        elif filter_name in [
            "Admission Date From",
            "Admission Date To",
            "Discharge Date From",
            "Discharge Date To",
        ]:
            self._fill_date_filter(filter_name)
        
        # Handle dropdown/select filters
        elif filter_name in [
            "Speciality",
            "Status",
            "Health Fund Contract",
            "DRG",
            "Document Types",
            "LOS Operator",
        ]:
            self._select_dropdown_filter(filter_name)

    def _fill_text_filter(self, filter_name: str) -> None:
        """Fill text-based filters."""
        values = {
            "Episode Identifier": "TEST001",
            "MRN/UR": "MRN123",
            "Length of Stay (LOS)": "5",
        }
        value = values.get(filter_name, "test_value")
        
        # Find the input field by placeholder or label
        input_field = self.page.get_by_placeholder(re.compile(filter_name, re.I)).first
        if not input_field.count():
            input_field = self.page.get_by_placeholder(f"Search {filter_name}").first
        
        if input_field.count():
            input_field.fill(value)
            print(f"  ✓ Filled {filter_name} with: {value}")
        else:
            print(f"  ✗ Could not find input field for {filter_name}")

    def _fill_date_filter(self, filter_name: str) -> None:
        """Fill date-based filters."""
        dates = {
            "Admission Date From": "01/01/2024",
            "Admission Date To": "31/01/2024",
            "Discharge Date From": "01/02/2024",
            "Discharge Date To": "28/02/2024",
        }
        date_value = dates.get(filter_name, "01/01/2024")
        
        # Find date input field
        input_field = self.page.get_by_placeholder(re.compile(filter_name, re.I)).first
        if not input_field.count():
            input_field = self.page.locator(f"input[placeholder*='{filter_name}']").first
        
        if input_field.count():
            input_field.fill(date_value)
            print(f"  ✓ Filled {filter_name} with: {date_value}")
        else:
            print(f"  ✗ Could not find date field for {filter_name}")

    def _select_dropdown_filter(self, filter_name: str) -> None:
        """Select a dropdown filter."""
        # Map of filters to example values
        filter_values = {
            "Speciality": "Cardiology",
            "Status": "Open",
            "Health Fund Contract": "Medicare",
            "DRG": "DRG001",
            "Document Types": "Report",
            "LOS Operator": "Greater Than",
        }
        value = filter_values.get(filter_name, "Option 1")
        
        # Find the dropdown/select element
        select_input = self.page.get_by_placeholder(re.compile(f"Search|Select", re.I)).first
        if not select_input.count():
            select_input = self.page.locator(f"input[placeholder*='{filter_name}']").first
        
        if select_input.count():
            select_input.click()
            self.page.wait_for_timeout(300)
            
            # Look for the option in the dropdown
            option = self.page.get_by_text(value, exact=True).first
            if option.count() and option.is_visible():
                option.click()
                print(f"  ✓ Selected {filter_name}: {value}")
            else:
                # Try to find by partial match
                all_options = self.page.locator("div[role='option'], li").all()
                selected = False
                for opt in all_options:
                    if value.lower() in opt.text_content().lower():
                        opt.click()
                        print(f"  ✓ Selected {filter_name}: {value}")
                        selected = True
                        break
                
                if not selected:
                    print(f"  ✗ Could not find option '{value}' for {filter_name}")
        else:
            print(f"  ✗ Could not find dropdown for {filter_name}")

    def apply_filters_and_verify(self, filters: list[str]) -> bool:
        """Apply multiple filters and verify application."""
        for filter_name in filters:
            try:
                self.apply_named_filter(filter_name)
            except Exception as exc:
                print(f"Error applying filter {filter_name}: {exc}")
                return False
        
        return True

    def click_apply_button(self) -> None:
        """Click the Apply button to apply all filters."""
        apply_btn = self.page.get_by_text("Apply", exact=True).first
        if apply_btn.count() and apply_btn.is_visible():
            apply_btn.click()
            self.page.wait_for_load_state("networkidle", timeout=5000)
            print("✓ Applied filters")
        else:
            print("✗ Could not find Apply button")

    def click_cancel_button(self) -> None:
        """Click the Cancel button to close filters without applying."""
        cancel_btn = self.page.get_by_text("Cancel", exact=True).first
        if cancel_btn.count() and cancel_btn.is_visible():
            cancel_btn.click()
            self.page.wait_for_timeout(300)
            print("✓ Cancelled filters")
        else:
            print("✗ Could not find Cancel button")

    def open_code_accelerate_target(self, base_url: str) -> bool:
        """Navigate to Code Accelerate > Episode List."""
        try:
            self.page.goto(f"{base_url}/episode-list", wait_until="networkidle")
            self.page.wait_for_timeout(1000)
            
            # Verify we're on the right page
            if self._code_accelerate_filter_available():
                print("✓ Navigated to Code Accelerate > Episode List")
                return True
            
            # Try alternate navigation
            for link in self.TARGET_LINKS:
                try:
                    element = self.page.locator(link).first
                    if element.count() and element.is_visible():
                        element.click()
                        self.page.wait_for_load_state("networkidle", timeout=5000)
                        return True
                except Exception:
                    continue
            
            print("✗ Could not navigate to Code Accelerate > Episode List")
            return False
        except Exception as exc:
            print(f"Error navigating to Episode List: {exc}")
            return False


def run_code_accelerate_episode_list_filter_search(
    username: str, password: str, filter_name: str | None = None
) -> None:
    """Main function to run Code Accelerate Episode List filter automation."""
    from config.settings import Settings

    settings = Settings(env=os.getenv("ENV", "dev"))
    headless = settings.headless
    headless_env = os.getenv("HEADLESS")
    if headless_env is not None:
        headless = headless_env.lower() in ("1", "true", "yes")

    filters_to_run = [filter_name] if filter_name else CodeAccelerateEpisodeListFilterPage.DEFAULT_FILTERS
    known_filters = CodeAccelerateEpisodeListFilterPage.FILTERS
    unknown_filters = [name for name in filters_to_run if name not in known_filters]
    if unknown_filters:
        available = ", ".join(sorted(known_filters))
        raise ValueError(f"Unknown filter name: {unknown_filters[0]}. Available filters: {available}")

    with sync_playwright() as playwright:
        browser_type = getattr(playwright, settings.browser)
        browser = browser_type.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()
        try:
            login_page = LoginPage(page)
            filters_page = CodeAccelerateEpisodeListFilterPage(page)

            print("Navigating to login page...")
            login_page.open_login_page(settings.base_url)
            login_page.wait_for_page_load()

            print("Performing login...")
            _login_with_retry(login_page, username, password)

            print("Opening Code Accelerate > Episode List...")
            if not filters_page.open_code_accelerate_target(settings.base_url):
                filters_page.capture_debug_artifacts("code_accelerate_episode_list_filter_navigation_failure")
                raise AssertionError("Could not open Code Accelerate > Episode List page")

            # Open filter panel if needed
            filters_page.page.wait_for_timeout(500)

            for current_filter in filters_to_run:
                print(f"\nApplying {current_filter} filter...")
                try:
                    filters_page.apply_named_filter(current_filter)
                    print(f"[OK] {current_filter} filter applied")
                except Exception as exc:
                    print(f"[ERROR] Could not apply {current_filter}: {exc}")
                    filters_page.capture_debug_artifacts(f"code_accelerate_filter_error_{current_filter}")

            print("\nClicking Apply button...")
            filters_page.click_apply_button()

            print("\n✓ Code Accelerate Episode List filter automation completed successfully!")

        except Exception as exc:
            print(f"\n✗ Error during filter automation: {exc}")
            filters_page.capture_debug_artifacts("code_accelerate_episode_list_filter_failure")
            raise
        finally:
            browser.close()


if __name__ == "__main__":
    import getpass

    username = input("Enter username: ").strip()
    password = getpass.getpass("Enter password: ").strip()

    try:
        run_code_accelerate_episode_list_filter_search(username, password)
    except Exception as exc:
        print(f"Filter automation failed: {exc}")
        sys.exit(1)
