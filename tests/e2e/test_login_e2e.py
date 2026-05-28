from pages.login_page import LoginPage
from pathlib import Path
import pytest


REPORTS_DIR = Path("reports/e2e")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def _screenshot(page, name: str):
    path = REPORTS_DIR / f"{name}.png"
    page.screenshot(path=str(path))
    return path


def test_e2e_valid_login(page, app_settings):
    login_page = LoginPage(page)
    try:
        login_page.open_login_page(app_settings.base_url)
        login_page.login("Sai", "Imedx@123")
        login_page.verify_login_success()
    except Exception:
        _screenshot(page, "valid_login_failure")
        raise


def test_e2e_invalid_login(page, app_settings):
    login_page = LoginPage(page)
    try:
        login_page.open_login_page(app_settings.base_url)
        login_page.login("wrong_user", "wrong_password")
        login_page.verify_login_error()
    except Exception:
        _screenshot(page, "invalid_login_failure")
        raise
