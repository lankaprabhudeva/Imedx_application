import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CWD = Path.cwd()
for path in (ROOT, CWD):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from pages.codingcomplete import CodingCompletePage


class MissingNotesPage(CodingCompletePage):
    """Workflow for sending a coding-complete episode to Missing Notes."""

    MY_ACTIONS_BUTTON = 'button:has-text("My Actions"), button[aria-label="My Actions"]'
    MISSING_NOTES_PANEL_SELECTORS = [
        (
            '.dropdown-submenu-myactions:has(a.submenu-title:has-text("Missing Notes")) '
            '> .submenu-menu.dropdown-menu.show'
        ),
        (
            '.dropdown-submenu-myactions:has(.submenu-title:has-text("Missing Notes")) '
            '.submenu-menu.dropdown-menu.show'
        ),
        '[role="dialog"]:has-text("Missing Notes")',
        '[role="dialog"]:has-text("Missing notes")',
    ]
    MISSING_NOTES_ACTION_SELECTORS = [
        '.submenu-title:has-text("Missing Notes")',
        '.submenu-title:has-text("Missing notes")',
        'a.dropdown-item:has-text("Missing Notes")',
        'a.dropdown-item:has-text("Missing notes")',
        '[role="button"]:has-text("Missing Notes")',
        '[role="button"]:has-text("Missing notes")',
        '[role="menuitem"]:has-text("Missing Notes")',
        '[role="menuitem"]:has-text("Missing notes")',
    ]
    SEND_BUTTON_SELECTORS = [
        'button:has-text("Send")',
        'button:has-text("Submit")',
        'button:has-text("Save")',
        'role=button[name="Send"]',
        '.send-to-review-btn',
    ]
    SEARCH_SELECTORS = [
        'input[placeholder*="Search"]',
        'input[aria-label*="Search"]',
        'input[type="search"]',
        'input[type="text"]',
    ]

    def send_missing_notes(self, note_types: list[str]) -> bool:
        """Open My Actions > Missing Notes, select every note type, and send."""
        note_types = [note.strip() for note in note_types if note and note.strip()]
        if not note_types:
            print('  ! No missing note types provided')
            return False

        if not self._open_my_actions_missing_notes():
            print('  ! My Actions Missing Notes panel did not open')
            return False

        selected_note_types = self._select_missing_notes_with_real_clicks(note_types)
        missing_note_types = [
            note_type
            for note_type in note_types
            if not self._note_type_was_matched(note_type, selected_note_types)
        ]

        for selected_note_type in selected_note_types:
            print(f'  [OK] Missing note type selected: {selected_note_type}')

        if missing_note_types:
            print(f'  ! Missing note type not selected: {", ".join(missing_note_types)}')
            return False

        if not self._click_send_missing_notes():
            print('  ! Missing Notes Send button not clicked')
            return False

        if not self._wait_for_missing_notes_sent_status(note_types):
            print('  ! Missing Notes sent confirmation/status not detected')
            return False

        episode_identifier = self.completed_episode_identifier or 'Unknown Episode'
        print(
            '  [OK] Episode sent to Missing Notes for '
            f'{", ".join(note_types)}. Episode Identifier: {episode_identifier}'
        )
        return True

    def _select_missing_notes_with_real_clicks(self, note_types: list[str]) -> list[str]:
        selected_labels = []

        for note_type in note_types:
            panel = self._missing_notes_panel()
            if not panel:
                if not self._open_my_actions_missing_notes():
                    continue
                panel = self._missing_notes_panel()
                if not panel:
                    continue

            row = self._find_missing_note_row(panel, note_type)
            if not row:
                continue

            label_text = self._get_row_text(row) or note_type
            checkbox = row.locator('input[type="checkbox"]').first

            try:
                checkbox.scroll_into_view_if_needed(timeout=2000)
                if not checkbox.is_checked(timeout=1000):
                    checkbox.click(force=True, timeout=3000)
                self._safe_wait(300)
                if not checkbox.is_checked(timeout=1000):
                    checkbox.check(force=True, timeout=3000)
                self._safe_wait(300)
                if checkbox.is_checked(timeout=1000):
                    selected_labels.append(label_text.strip())
            except Exception:
                try:
                    row.click(force=True, timeout=3000)
                    self._safe_wait(300)
                    if checkbox.is_checked(timeout=1000):
                        selected_labels.append(label_text.strip())
                except Exception:
                    continue

        return selected_labels

    def _find_missing_note_row(self, panel, note_type: str):
        requested_variants = [
            self._normalize_note_type(variant)
            for variant in self._note_type_variants(note_type)
        ]

        try:
            rows = panel.locator('.missing_notest_checkbox, .form-check')
            for index in range(rows.count()):
                row = rows.nth(index)
                if not row.is_visible():
                    continue

                row_text = self._get_row_text(row)
                normalized_row_text = self._normalize_note_type(row_text)
                if any(
                    normalized_row_text == requested
                    or normalized_row_text in requested
                    or requested in normalized_row_text
                    for requested in requested_variants
                ):
                    return row
        except Exception:
            pass

        return None

    def _get_row_text(self, row) -> str:
        try:
            label = row.locator('label').first
            if label and label.count() > 0:
                text = label.inner_text(timeout=1000).strip()
                if text:
                    return text
        except Exception:
            pass

        try:
            return row.inner_text(timeout=1000).strip()
        except Exception:
            return ''

    def _note_type_was_matched(self, requested_note_type: str, selected_note_types: list[str]) -> bool:
        requested_variants = {
            self._normalize_note_type(variant)
            for variant in self._note_type_variants(requested_note_type)
        }
        selected_variants = {
            self._normalize_note_type(selected_note_type)
            for selected_note_type in selected_note_types
        }
        return any(
            requested == selected
            or requested in selected
            or selected in requested
            for requested in requested_variants
            for selected in selected_variants
        )

    def _normalize_note_type(self, note_type: str) -> str:
        normalized = re.sub(r'[^a-z0-9]+', '', note_type.lower())
        return normalized[:-1] if normalized.endswith('s') else normalized

    def _open_my_actions_missing_notes(self) -> bool:
        for attempt in range(3):
            try:
                self.page.evaluate('window.scrollTo(0, 0)')
                self._safe_wait(300)
            except Exception:
                pass

            if self._click_my_actions_button():
                if self._select_missing_notes_action():
                    print('  [OK] My Actions Missing Notes panel opened')
                    return True

            self._safe_wait(500)

        print('  ! Missing Notes confirmation not shown before timeout')
        return False

    def _click_my_actions_button(self) -> bool:
        selectors = [
            self.MY_ACTIONS_BUTTON,
            'button:has(span[aria-label="My Actions"])',
            'button:has-text("My Actions")',
            'span[aria-label="My Actions"]',
            'text=My Actions',
        ]

        for selector in selectors:
            try:
                items = self.page.locator(selector)
                for index in range(items.count()):
                    item = items.nth(index)
                    if not item.is_visible():
                        continue

                    target = item
                    try:
                        if selector.startswith('span') or selector == 'text=My Actions':
                            target = item.locator('xpath=ancestor::button[1]')
                    except Exception:
                        target = item

                    target.scroll_into_view_if_needed()
                    self._safe_wait(200)

                    for click_attempt in range(3):
                        try:
                            if click_attempt == 0:
                                target.click(force=True)
                            elif click_attempt == 1:
                                box = target.bounding_box(timeout=1000)
                                if box:
                                    self.page.mouse.click(
                                        box['x'] + box['width'] / 2,
                                        box['y'] + box['height'] / 2,
                                    )
                            else:
                                target.evaluate(
                                    """element => {
                                        for (const eventName of [
                                            'pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click'
                                        ]) {
                                            element.dispatchEvent(new MouseEvent(eventName, {
                                                bubbles: true,
                                                cancelable: true,
                                                view: window
                                            }));
                                        }
                                        element.click();
                                    }"""
                                )
                        except Exception:
                            continue

                        self._safe_wait(900)
                        if self._my_actions_menu_opened():
                            return True
            except Exception:
                continue

        return False

    def _my_actions_menu_opened(self) -> bool:
        selectors = [
            '.dropdown-menu.show',
            '[role="menu"]',
            'text=View audit log',
            'text=Sending for billing',
        ]
        selectors.extend(self.MISSING_NOTES_ACTION_SELECTORS)

        for selector in selectors:
            try:
                items = self.page.locator(selector)
                for index in range(items.count()):
                    if items.nth(index).is_visible():
                        return True
            except Exception:
                continue

        return False

    def _select_missing_notes_action(self) -> bool:
        for selector in self.MISSING_NOTES_ACTION_SELECTORS:
            try:
                items = self.page.locator(selector)
                for index in range(items.count()):
                    item = items.nth(index)
                    if not item.is_visible():
                        continue

                    item.scroll_into_view_if_needed()
                    try:
                        item.hover()
                    except Exception:
                        pass
                    self._safe_wait(700)

                    if self._missing_notes_panel_is_visible():
                        return True

                    try:
                        item.click(force=True)
                    except Exception:
                        pass
                    self._safe_wait(900)

                    if self._missing_notes_panel_is_visible():
                        return True
            except Exception:
                continue

        return False

    def _missing_notes_panel_is_visible(self) -> bool:
        return bool(self._missing_notes_panel())

    def _missing_notes_panel(self):
        for selector in self.MISSING_NOTES_PANEL_SELECTORS:
            try:
                panels = self.page.locator(selector)
                for index in range(panels.count()):
                    panel = panels.nth(index)
                    if panel.is_visible() and self._panel_has_missing_notes_controls(panel):
                        return panel
            except Exception:
                continue

        return None

    def _panel_has_missing_notes_controls(self, panel) -> bool:
        has_checkbox = False
        has_send = False

        for selector in ['input[type="checkbox"]', '[role="checkbox"]']:
            try:
                item = panel.locator(selector).first
                if item and item.is_visible():
                    has_checkbox = True
                    break
            except Exception:
                continue

        for selector in self.SEND_BUTTON_SELECTORS:
            try:
                item = panel.locator(selector).first
                if item and item.is_visible():
                    has_send = True
                    break
            except Exception:
                continue

        return has_checkbox or has_send

    def _search_and_select_missing_note(self, note_type: str) -> bool:
        panel = self._missing_notes_panel()
        if not panel:
            return False

        if self._select_missing_note_in_missing_notes_submenu(note_type):
            return True

        for candidate in self._note_type_variants(note_type):
            self._search_missing_note(panel, candidate)

            if self._select_missing_note_checkbox(panel, candidate, expected_note_type=note_type):
                return True

            if self._select_missing_note_with_dom(panel, candidate):
                return True

        return False

    def _select_missing_note_in_missing_notes_submenu(self, note_type: str) -> bool:
        try:
            selected_label = self.page.evaluate(
                """noteType => {
                    const normalize = value => value
                        .toLowerCase()
                        .replace(/[^a-z0-9]+/g, '')
                        .replace(/s$/g, '');
                    const wanted = normalize(noteType);
                    const submenus = Array.from(document.querySelectorAll('.dropdown-submenu-myactions'));
                    const missingNotes = submenus.find(menu => {
                        const title = menu.querySelector('.submenu-title');
                        return title && title.textContent.toLowerCase().includes('missing notes');
                    });
                    if (!missingNotes) return '';

                    const rows = Array.from(
                        missingNotes.querySelectorAll('.missing_notest_checkbox, .form-check')
                    );
                    const row = rows.find(candidate => {
                        const label = candidate.querySelector('label') || candidate;
                        const text = label.textContent || '';
                        const normalizedText = normalize(text);
                        return normalizedText === wanted
                            || normalizedText.includes(wanted)
                            || wanted.includes(normalizedText);
                    });
                    if (!row) return '';

                    const checkbox = row.querySelector('input[type="checkbox"]')
                        || row.closest('.form-check')?.querySelector('input[type="checkbox"]')
                        || row.parentElement?.querySelector('input[type="checkbox"]');
                    const label = row.querySelector('label') || row;
                    if (!checkbox) return '';

                    checkbox.scrollIntoView({ block: 'center', inline: 'center' });
                    if (!checkbox.checked) {
                        checkbox.click();
                    }
                    if (!checkbox.checked && label) {
                        label.click();
                    }
                    if (!checkbox.checked) {
                        const setter = Object.getOwnPropertyDescriptor(
                            HTMLInputElement.prototype,
                            'checked'
                        ).set;
                        setter.call(checkbox, true);
                        checkbox.dispatchEvent(new MouseEvent('click', { bubbles: true }));
                        checkbox.dispatchEvent(new Event('input', { bubbles: true }));
                        checkbox.dispatchEvent(new Event('change', { bubbles: true }));
                    }

                    return checkbox.checked ? (label.textContent || noteType).trim() : '';
                }""",
                note_type,
            )
            if selected_label:
                print(f'  [OK] Matched Missing Notes option: {selected_label}')
                return True
        except Exception:
            pass

        return False

    def _note_type_variants(self, note_type: str) -> list[str]:
        variants = []
        cleaned = note_type.strip()
        if cleaned:
            variants.append(cleaned)

        if cleaned.lower().endswith(' notes'):
            variants.append(cleaned[:-1])
        elif cleaned.lower().endswith(' note'):
            variants.append(f'{cleaned}s')

        if cleaned.lower().endswith(' reports'):
            variants.append(cleaned[:-1])
        elif cleaned.lower().endswith(' report'):
            variants.append(f'{cleaned}s')

        return list(dict.fromkeys(variants))

    def _search_missing_note(self, panel, note_type: str) -> None:
        for selector in self.SEARCH_SELECTORS:
            try:
                search = panel.locator(selector).first
                if search and search.is_visible() and search.is_enabled():
                    search.scroll_into_view_if_needed()
                    search.click(force=True)
                    search.fill(note_type)
                    self._safe_wait(500)
                    return
            except Exception:
                continue

    def _select_missing_note_checkbox(
        self,
        panel,
        note_type: str,
        expected_note_type: str | None = None,
    ) -> bool:
        selectors = [
            f'label:has-text("{note_type}") input[type="checkbox"]',
            f'.dropdown-item:has-text("{note_type}") input[type="checkbox"]',
            f'div:has-text("{note_type}") input[type="checkbox"]',
            f'tr:has-text("{note_type}") input[type="checkbox"]',
            f'[role="row"]:has-text("{note_type}") input[type="checkbox"]',
            f'text={note_type}',
        ]

        for selector in selectors:
            try:
                items = panel.locator(selector)
                for index in range(items.count()):
                    item = items.nth(index)
                    if not item.is_visible():
                        continue

                    item.scroll_into_view_if_needed()
                    if 'input[type="checkbox"]' in selector:
                        self._check_checkbox(item)
                    else:
                        row = item.locator(
                            'xpath=ancestor-or-self::*[.//input[@type="checkbox"]][1]'
                        )
                        checkbox = row.locator('input[type="checkbox"]').first
                        if checkbox and checkbox.count() > 0:
                            self._check_checkbox(checkbox)
                        else:
                            item.click(force=True)

                    self._safe_wait(300)
                    if self._missing_note_is_checked(panel, expected_note_type or note_type):
                        return True
            except Exception:
                continue

        return False

    def _select_missing_note_with_dom(self, panel, note_type: str, timeout: int = 10000) -> bool:
        start = time.time()
        while time.time() - start < timeout / 1000:
            try:
                selected = panel.evaluate(
                    """(element, noteType) => {
                        const wanted = noteType.toLowerCase();
                        const normalize = value => value
                            .toLowerCase()
                            .replace(/[^a-z0-9]+/g, '')
                            .replace(/s$/g, '');
                        const normalizedWanted = normalize(noteType);
                        const boxes = Array.from(
                            element.querySelectorAll('input[type="checkbox"], [role="checkbox"]')
                        );
                        const checkbox = boxes.find(input => {
                            const row = input.closest('label, .dropdown-item, tr, [role="row"], div');
                            if (!row) return false;
                            const text = row.textContent.toLowerCase();
                            const normalizedText = normalize(text);
                            return text.includes(wanted)
                                || normalizedText.includes(normalizedWanted)
                                || normalizedWanted.includes(normalizedText);
                        });
                        if (!checkbox) return false;

                        checkbox.scrollIntoView({ block: 'center', inline: 'center' });
                        const setter = Object.getOwnPropertyDescriptor(
                            HTMLInputElement.prototype,
                            'checked'
                        ).set;
                        setter.call(checkbox, true);
                        checkbox.dispatchEvent(new MouseEvent('click', { bubbles: true }));
                        checkbox.dispatchEvent(new Event('input', { bubbles: true }));
                        checkbox.dispatchEvent(new Event('change', { bubbles: true }));
                        return checkbox.checked;
                    }""",
                    note_type,
                )
                if selected:
                    return True
            except Exception:
                pass

            self._safe_wait(300)

        return False

    def _missing_note_is_checked(self, panel, note_type: str) -> bool:
        try:
            checked = panel.locator(f'div:has-text("{note_type}") input[type="checkbox"]:checked')
            if checked.count() > 0:
                return True
        except Exception:
            pass

        try:
            return bool(
                self.page.evaluate(
                    """noteType => {
                        const wanted = noteType.toLowerCase();
                        const normalize = value => value
                            .toLowerCase()
                            .replace(/[^a-z0-9]+/g, '')
                            .replace(/s$/g, '');
                        const normalizedWanted = normalize(noteType);
                        return Array.from(document.querySelectorAll('input[type="checkbox"]:checked'))
                            .some(input => {
                                const row = input.closest('label, .dropdown-item, tr, [role="row"], div');
                                if (!row) return false;
                                const text = row.textContent.toLowerCase();
                                const normalizedText = normalize(text);
                                return text.includes(wanted)
                                    || normalizedText.includes(normalizedWanted)
                                    || normalizedWanted.includes(normalizedText);
                            });
                    }""",
                    note_type,
                )
            )
        except Exception:
            return False

    def _check_checkbox(self, checkbox) -> None:
        try:
            checkbox.scroll_into_view_if_needed(timeout=1000)
            checkbox.check(force=True, timeout=2000)
            return
        except Exception:
            pass

        try:
            checkbox.click(force=True, timeout=2000)
            return
        except Exception:
            pass

        checkbox.evaluate(
            """element => {
                const setter = Object.getOwnPropertyDescriptor(
                    HTMLInputElement.prototype,
                    'checked'
                ).set;
                setter.call(element, true);
                element.dispatchEvent(new Event('input', { bubbles: true }));
                element.dispatchEvent(new Event('change', { bubbles: true }));
            }"""
        )

    def _click_send_missing_notes(self) -> bool:
        panel = self._missing_notes_panel()
        if not panel:
            return False

        for selector in self.SEND_BUTTON_SELECTORS:
            try:
                buttons = panel.locator(selector)
                for index in range(buttons.count()):
                    button = buttons.nth(index)
                    if not button.is_visible():
                        continue
                    if not button.is_enabled():
                        continue

                    button.scroll_into_view_if_needed()
                    button.click()
                    try:
                        self.page.wait_for_load_state('networkidle', timeout=5000)
                    except Exception:
                        pass
                    self._safe_wait(1000)
                    print('  [OK] Missing Notes Send clicked')
                    return True
            except Exception:
                continue

        return False

    def _wait_for_missing_notes_sent_status(
        self,
        note_types: list[str],
        timeout: int = 60000,
    ) -> bool:
        start = time.time()
        success_patterns = [
            'Missing Notes',
            'Missing notes',
            'sent',
            'success',
            'successfully',
        ]
        success_patterns.extend(note_types)

        while time.time() - start < timeout / 1000:
            self.wait_for_loading_overlay(1000)

            try:
                toast = self.page.locator(
                    '.Toastify__toast--success, .Toastify__toast-body, [role="alert"]'
                )
                for index in range(toast.count()):
                    item = toast.nth(index)
                    if item.is_visible():
                        text = item.inner_text(timeout=1000)
                        if any(pattern.lower() in text.lower() for pattern in success_patterns):
                            print('  [OK] Missing Notes status detected')
                            return True
            except Exception:
                pass

            try:
                if not self._missing_notes_panel_is_visible():
                    print('  [OK] Missing Notes panel closed')
                    return True
            except Exception:
                pass

            self._safe_wait(1000)

        return False


def get_missing_note_types_from_args() -> list[str]:
    raw_values = []
    if len(sys.argv) > 1:
        raw_values.extend(sys.argv[1:])

    env_values = os.getenv('MISSING_NOTE_TYPES', '')
    if env_values:
        raw_values.append(env_values)

    if not raw_values:
        return []

    note_types = []
    for raw_value in raw_values:
        note_types.extend(
            note.strip()
            for note in raw_value.split(',')
            if note and note.strip()
        )

    return note_types


if __name__ == '__main__':
    import traceback
    from playwright.sync_api import sync_playwright
    from pages.login_page import LoginPage
    from pages.unassignepisode_page import UnassignedEpisodePage
    from config.settings import Settings

    settings = Settings(env=os.getenv('ENV', 'dev'))
    base_url = settings.base_url
    headless = settings.headless
    headless_env = os.getenv('HEADLESS')
    if headless_env is not None:
        headless = headless_env.lower() in ('1', 'true', 'yes')

    missing_note_types = get_missing_note_types_from_args()
    if not missing_note_types:
        print(
            'ERROR: Please provide Missing Notes values dynamically, for example: '
            'python pages/Missing_notes.py "Discharge Summary,Operation Report"'
        )
        sys.exit(2)

    exit_code = [0]

    with sync_playwright() as playwright:
        browser_type = getattr(playwright, settings.browser)
        browser = browser_type.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()

        try:
            login = LoginPage(page)
            nav = UnassignedEpisodePage(page)
            missing_notes = MissingNotesPage(page)

            def fail_step(msg: str, exc: Exception | None = None):
                print(f'ERROR: {msg}')
                if exc:
                    traceback.print_exception(type(exc), exc, exc.__traceback__)

                ts = int(time.time())
                debug_dir = Path('reports/e2e/debug')
                debug_dir.mkdir(parents=True, exist_ok=True)
                screenshot_path = debug_dir / f'missing_notes_failure_{ts}.png'
                html_path = debug_dir / f'missing_notes_failure_{ts}.html'

                try:
                    page.screenshot(path=str(screenshot_path), full_page=True)
                    html_path.write_text(page.content(), encoding='utf-8')
                    print(f'Wrote debug files: {screenshot_path} {html_path}')
                except Exception:
                    pass

                exit_code[0] = 2

            print('Navigating to base URL...')
            page.goto(base_url)

            print('Performing login...')
            try:
                login.login(
                    os.getenv('IMEDX_USERNAME', 'Sai'),
                    os.getenv('IMEDX_PASSWORD', 'Imedx@123'),
                )
                login.verify_login_success()
                print('  [OK] Login successful')
            except Exception as e:
                fail_step('Login failed', e)
                raise

            def open_coder_workspace_from_base(reason: str):
                print(reason)
                try:
                    page.goto(base_url, wait_until='domcontentloaded')
                    try:
                        page.wait_for_load_state('networkidle', timeout=5000)
                    except Exception:
                        pass
                    opened = nav.open_code_workflow() or nav.open_him_workspace()
                    if not opened:
                        raise AssertionError('Could not open Code Workflow or HIM Workspace')
                    if not nav.open_coder_workspace():
                        raise AssertionError('Could not open Coder Workspace')
                    print('  [OK] Coder Workspace opened')
                except Exception as e:
                    fail_step('Navigation to Coder Workspace failed', e)
                    raise

            def run_missing_notes_scenario(name: str, open_coding_panel):
                print(f'\nStarting {name} Missing Notes scenario...')

                print('Applying Outstanding Status filter...')
                try:
                    if not missing_notes.apply_outstanding_filter():
                        raise AssertionError('Outstanding Status filter was not applied')
                    print('  [OK] Outstanding Status filter applied')
                except Exception as e:
                    fail_step(f'Applying Outstanding Status filter failed for {name}', e)
                    raise

                print('Opening first outstanding episode...')
                try:
                    if not missing_notes.open_first_outstanding_episode():
                        raise AssertionError('open_first_outstanding_episode returned False')
                    print('  [OK] Outstanding episode opened')
                except Exception as e:
                    fail_step(f'Opening outstanding episode failed for {name}', e)
                    raise

                print(f'Opening {name} coding panel...')
                try:
                    if not open_coding_panel():
                        raise AssertionError(f'Opening {name} returned False')
                    missing_notes.close_popup_if_visible()
                    print(f'  [OK] {name} coding panel opened')
                except Exception as e:
                    fail_step(f'Opening {name} coding panel failed', e)
                    raise

                print('Entering principal, additional diagnosis, and procedure codes...')
                try:
                    if not missing_notes.enter_coding_codes(
                        principal_code='Z51.1',
                        additional_codes=[
                            'M8010/3',
                            'J18.2',
                            'F44.4',
                            'F99',
                            'R10.4',
                            'R68.8',
                        ],
                        procedure_codes=[
                            '96199-00',
                        ],
                    ):
                        raise AssertionError('enter_coding_codes returned False')
                    print('  [OK] All requested diagnosis and procedure codes entered')
                except Exception as e:
                    fail_step(f'Entering diagnosis/procedure codes failed for {name}', e)
                    raise

                print('Confirming DRG...')
                try:
                    if not missing_notes.confirm_drg():
                        raise AssertionError('confirm_drg returned False')
                    print('  [OK] DRG confirmed')
                except Exception as e:
                    fail_step(f'Confirm DRG failed for {name}', e)
                    raise

                print('Clicking Coding Complete...')
                try:
                    if not missing_notes.complete_coding():
                        raise AssertionError('complete_coding returned False')
                    print('  [OK] Coding Complete clicked')
                except Exception as e:
                    fail_step(f'Clicking Coding Complete failed for {name}', e)
                    raise

                print(
                    'Sending Missing Notes from My Actions for: '
                    f'{", ".join(missing_note_types)}'
                )
                try:
                    if not missing_notes.send_missing_notes(missing_note_types):
                        raise AssertionError('send_missing_notes returned False')
                    print('  [OK] Missing Notes sent')
                except Exception as e:
                    fail_step(f'Sending Missing Notes failed for {name}', e)
                    raise

                print(f'  [OK] {name} Missing Notes scenario completed')

            open_coder_workspace_from_base('Opening Code Workflow/Coder Workspace...')
            run_missing_notes_scenario('Code Assist', missing_notes.open_code_assist)

            open_coder_workspace_from_base(
                '\nReopening Code Workflow/Coder Workspace after Code Assist Missing Notes completion...'
            )
            run_missing_notes_scenario('Code Accelerate', missing_notes.open_code_accelerate_panel)

            print('\nMissing Notes run finished')
        except Exception:
            if exit_code[0] == 0:
                exit_code[0] = 1
        finally:
            try:
                context.close()
                browser.close()
            except Exception:
                pass

    if exit_code[0] != 0:
        print(f'Exiting with code {exit_code[0]}')
        sys.exit(exit_code[0])
