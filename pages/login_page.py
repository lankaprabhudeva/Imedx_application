import re

from playwright.sync_api import TimeoutError
from pages.base_page import BasePage


class LoginPage(BasePage):
    # Updated locators for iMedx application
    USERNAME_INPUT = 'input[type="email"], input[name="username"], input[id*="user"], input[placeholder*="mail"]'
    PASSWORD_INPUT = 'input[type="password"]'
    LOGIN_BUTTON = 'button:has-text("Login"), button[type="submit"], button.Login-btn, button:has-text("Sign In")'
    ERROR_MESSAGE = '.error-message, [role="alert"], .alert-error, [class*="error"]'
    DASHBOARD_HEADER = 'h1, [role="heading"], [class*="dashboard"], [class*="welcome"]'
    LOADING_SPINNER = '[class*="spinner"], [class*="loading"], .loader'

    def open_login_page(self, base_url: str):
        """Navigate to the login page"""
        self.navigate(base_url)
        self.page.wait_for_selector('form.login-form', timeout=20000)
        page_title = self.page.title()
        print(f"Page Title: {page_title}")

    def _enable_element(self, element):
        try:
            element.evaluate('el => { el.removeAttribute("disabled"); el.disabled = false; }')
        except Exception:
            pass

    def _fill_input(self, selector: str, value: str):
        element = self.page.locator(selector).first
        element.wait_for(state='attached', timeout=20000)
        self._enable_element(element)
        try:
            element.scroll_into_view_if_needed()
        except Exception:
            pass
        try:
            element.click(force=True)
        except Exception:
            pass
        try:
            element.fill(value, force=True)
        except Exception:
            element.evaluate(
                "(el, value) => { el.value = value; el.dispatchEvent(new Event('input', { bubbles: true })); el.dispatchEvent(new Event('change', { bubbles: true })); }",
                value,
            )
        try:
            element.press('Tab')
        except Exception:
            pass
        self.page.wait_for_timeout(500)

    def login(self, username: str, password: str):
        """Fill in credentials and submit login form"""
        print(f"Attempting login with username: {username}")

        username_selector = 'input#username, input[name="username"], input[id*="user"], input[placeholder*="mail"]'
        password_selector = 'input#password, input[type="password"], input[name="password"], input[id*="pass"]'

        self._fill_input(username_selector, username)
        self._fill_input(password_selector, password)

        login_button = self.page.locator(self.LOGIN_BUTTON).first
        try:
            login_button.wait_for(state='attached', timeout=10000)
            self._enable_element(login_button)
            login_button.scroll_into_view_if_needed()
            login_button.click(force=True)
        except Exception:
            try:
                self.page.evaluate(
                    "() => { const form = document.querySelector('form.login-form'); if (form) { form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true })); form.requestSubmit?.(); } }",
                )
            except Exception:
                self.page.keyboard.press('Enter')

        # Wait for login result
        try:
            self.page.wait_for_load_state('networkidle', timeout=20000)
        except TimeoutError:
            self.page.wait_for_timeout(2000)

    def verify_login_success(self):
        """Verify successful login"""
        current_url = self.page.url
        print(f"Current URL after login: {current_url}")

        try:
            self.page.wait_for_selector('form.login-form', state='detached', timeout=15000)
        except TimeoutError:
            pass

        if self.page.locator('form.login-form').is_visible():
            raise AssertionError('Login form is still visible after the login attempt')

        if 'login' in current_url.lower():
            raise AssertionError('Still on login URL after the login attempt')

    def verify_login_error(self):
        """Verify error message appears on failed login"""
        self.assert_visible(self.ERROR_MESSAGE)

    def wait_for_page_load(self, timeout: int = 5000):
        """Wait for page to fully load"""
        self.page.wait_for_load_state('networkidle', timeout=timeout)

    def get_current_url(self) -> str:
        """Get current page URL"""
        return self.page.url
