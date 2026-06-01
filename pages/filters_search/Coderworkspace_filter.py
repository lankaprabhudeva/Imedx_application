from __future__ import annotations

import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from playwright.sync_api import Page, expect, sync_playwright

from pages.base_page import BasePage
from pages.unassignepisode_page import UnassignedEpisodePage


@dataclass(frozen=True)
class FilterDefinition:
    label: str
    value: str | list[str]
    kind: str = "text"


class UnassignedEpisodesFilterPage(BasePage):
    """Filter helpers for the Unassigned Episodes page."""

    DYNAMIC_OPTION = "__dynamic_option__"

    FILTER_TOGGLE = (
        'button:has-text("Filter"), '
        'button:has-text("Filters"), '
        '[aria-label*="Filter"], '
        '[data-testid*="filter"], '
        '.workflow-coder-table-header span:has(svg), '
        '.workflow-coder-table-header button:has(svg), '
        'svg:has(path[d^="M440-120"]), '
        'path[d^="M440-120"]'
    )
    APPLY_FILTERS = 'button:has-text("Apply"), button:has-text("Search"), button:has-text("Submit")'
    CLEAR_ALL = [
        'button:has-text("Clear All")',
        'button:has-text("Reset")',
        'button:has-text("Clear")',
        'text=Clear All',
        'text=Reset',
    ]
    TABLE_ROWS = 'tbody tr, [role="row"], .workflow-list-row, .episode-list-row'

    FILTERS = {
        "episode_identifier": FilterDefinition("Episode Identifier", "1", "multi_select"),
        "mrn": FilterDefinition("MRN", "1", "multi_select"),
        "admission_date_from": FilterDefinition("Admission Date From", "01/01/2025", "date"),
        "admission_date_to": FilterDefinition("Admission Date To", "31/12/2026", "date"),
        "separation_date_from": FilterDefinition("Separation Date From", "01/01/2025", "date"),
        "separation_date_to": FilterDefinition("Separation Date To", "31/12/2026", "date"),
        "specialty": FilterDefinition("Speciality", DYNAMIC_OPTION, "multi_select"),
        "queue": FilterDefinition("Queue", DYNAMIC_OPTION, "multi_select"),
        "coders": FilterDefinition("Coders", DYNAMIC_OPTION, "multi_select"),
        "user_specific": FilterDefinition("User Specific", "False", "select"),
        "priority": FilterDefinition("Priority", DYNAMIC_OPTION, "multi_select"),
        "status": FilterDefinition("Status", DYNAMIC_OPTION, "multi_select"),
        "health_fund_contract": FilterDefinition("Health Fund Contract", DYNAMIC_OPTION, "multi_select"),
        "los_operator": FilterDefinition("LOS Operator", DYNAMIC_OPTION, "select_each"),
        "los": FilterDefinition("Length of Stay (LOS)", "1", "text"),
        "provisional_drg": FilterDefinition("Provisional DRG", DYNAMIC_OPTION, "multi_select"),
    }
    FILTER_GROUPS = {
        "admission_date_range": ["admission_date_from", "admission_date_to"],
        "separation_date_range": ["separation_date_from", "separation_date_to"],
    }
    DEFAULT_FILTERS = [
        "episode_identifier",
        "mrn",
        "admission_date_range",
        "separation_date_range",
        "specialty",
        "user_specific",
        "queue",
        "priority",
        "status",
        "health_fund_contract",
        "los_operator",
        "los",
        "provisional_drg",
    ]

    def open_unassigned_episodes(self, base_url: str | None = None) -> bool:
        nav = UnassignedEpisodePage(self.page)

        if base_url:
            try:
                self.page.goto(base_url, wait_until="domcontentloaded")
                try:
                    self.page.wait_for_load_state("networkidle", timeout=5000)
                except Exception:
                    pass
            except Exception:
                pass

        opened_workflow = nav.open_code_workflow() or nav.open_him_workspace()
        if not opened_workflow:
            try:
                if base_url:
                    self.page.goto(base_url.rstrip("/") + "/Code-Workflow", wait_until="domcontentloaded")
                    try:
                        self.page.wait_for_load_state("networkidle", timeout=5000)
                    except Exception:
                        pass
                    opened_workflow = True
            except Exception:
                opened_workflow = False

        if not opened_workflow:
            return False

        if not nav.open_coder_workspace():
            return False

        if nav.open_unassigned_episodes():
            return True

        return self._coder_workspace_filter_available()

    def capture_debug_artifacts(self, prefix: str) -> None:
        debug_dir = Path("reports/e2e/debug")
        debug_dir.mkdir(parents=True, exist_ok=True)
        ts = int(time.time())
        screenshot_path = debug_dir / f"{prefix}_{ts}.png"
        html_path = debug_dir / f"{prefix}_{ts}.html"

        try:
            self.page.screenshot(path=str(screenshot_path), full_page=True)
            html_path.write_text(self.page.content(), encoding="utf-8")
            print(f"Wrote debug files: {screenshot_path} {html_path}")
        except Exception:
            pass

    def open_filter_panel(self) -> None:
        if self._filter_card_count() > 0:
            return

        for toggle in self._visible_filter_toggles():
            try:
                toggle.scroll_into_view_if_needed()
                toggle.click(force=True)
                self.page.wait_for_timeout(700)
                if self._filter_card_count() > 0:
                    return
            except Exception:
                continue

        self.capture_debug_artifacts("unassigned_episodes_filter_toggle_not_found")
        raise AssertionError("Filter panel did not open on Coder Workspace")

    def apply_named_filter(self, filter_name: str) -> None:
        if filter_name in self.FILTER_GROUPS:
            self.apply_filter_group(filter_name)
            return

        definition = self.FILTERS[filter_name]
        if definition.kind == "multi_select":
            self.apply_each_multi_select_option(definition)
            return
        if definition.kind == "select_each":
            self.apply_each_select_option(definition)
            return

        self.open_filter_panel()

        self._apply_definition(definition)

        self.apply_filters()
        self.wait_for_results()

    def apply_filter_group(self, group_name: str) -> None:
        self.open_filter_panel()

        for filter_name in self.FILTER_GROUPS[group_name]:
            self._apply_definition(self.FILTERS[filter_name])

        self.apply_filters()
        self.wait_for_results()

    def apply_each_multi_select_option(self, definition: FilterDefinition) -> None:
        seed = None if definition.value == self.DYNAMIC_OPTION else str(definition.value)
        options = self._collect_multi_select_options(definition.label, seed)

        for index, option_text in enumerate(options):
            self.open_filter_panel()
            print(f"  Selecting {definition.label}: {option_text}")
            self._select_single_multi_option(definition.label, option_text)
            self.apply_filters()
            self.wait_for_results()

            if index < len(options) - 1:
                self.clear_all_filters()

    def apply_each_select_option(self, definition: FilterDefinition) -> None:
        seed = None if definition.value == self.DYNAMIC_OPTION else str(definition.value)
        options = self._collect_select_options(definition.label, seed)

        for index, option_text in enumerate(options):
            self.open_filter_panel()
            print(f"  Selecting {definition.label}: {option_text}")
            self.select_filter_value(definition.label, option_text)
            if definition.label == "LOS Operator":
                self.fill_los_value_for_operator(option_text)
            self.apply_filters()
            self.wait_for_results()

            if index < len(options) - 1:
                self.clear_all_filters()

    def _apply_definition(self, definition: FilterDefinition) -> None:
        if definition.kind == "multi_select":
            self.select_multi_filter_values(definition.label, definition.value)
        elif definition.kind == "select_each":
            self.select_filter_value(definition.label, str(definition.value))
        elif definition.kind == "select":
            self.select_filter_value(definition.label, str(definition.value))
        else:
            self.fill_filter_value(definition.label, str(definition.value))

    def fill_filter_value(self, label: str, value: str) -> None:
        self._enable_dependent_filter(label)
        self._fill_filter_field(label, value)

    def _fill_filter_field(self, label: str, value: str) -> None:
        card = self._filter_card(label)
        field = card.locator('input:not([type="hidden"]), textarea').first
        expect(field).to_be_visible(timeout=10000)
        if not field.is_enabled():
            self.capture_debug_artifacts(f"unassigned_episodes_filter_field_disabled_{self._safe_name(label)}")
            raise AssertionError(f"Filter field is disabled for label: {label}")
        field.fill(value)

    def fill_los_value_for_operator(self, operator_text: str) -> None:
        if "between" in operator_text.casefold():
            self._fill_filter_field("LOS From", "1")
            self._fill_filter_field("LOS To", "10")
            return

        self._fill_filter_field("Length of Stay (LOS)", str(self.FILTERS["los"].value))

    def _collect_multi_select_options(self, label: str, seed: str | None = None) -> list[str]:
        self.open_filter_panel()
        self._enable_dependent_filter(label)
        card = self._filter_card(label)
        control = self._select_control(card)
        if not control:
            self.capture_debug_artifacts(f"unassigned_episodes_filter_multiselect_not_found_{self._safe_name(label)}")
            raise AssertionError(f"Filter multi-select not found for label: {label}")
        if not self._control_is_enabled(control):
            self.capture_debug_artifacts(f"unassigned_episodes_filter_multiselect_disabled_{self._safe_name(label)}")
            raise AssertionError(f"Filter multi-select is disabled for label: {label}")

        control.click(force=True)
        # Dynamic dropdowns (no seed) need extra time for the API call to return
        wait_ms = 1500 if seed is None else 300
        self.page.wait_for_timeout(wait_ms)

        if seed:
            editable_input = self._select_input(card)
            if editable_input:
                try:
                    editable_input.fill(seed)
                except Exception:
                    self.page.keyboard.type(seed)
            else:
                self.page.keyboard.type(seed)
            self.page.wait_for_timeout(700)

        options = self._visible_dropdown_option_texts()
        self._close_open_dropdown()
        if not options:
            self.capture_debug_artifacts(f"unassigned_episodes_no_dropdown_options_{self._safe_name(label)}")
            raise AssertionError(f"No dropdown options available for label: {label}")
        return options

    def _collect_select_options(self, label: str, seed: str | None = None) -> list[str]:
        self.open_filter_panel()
        self._enable_dependent_filter(label)
        card = self._filter_card(label)
        control = self._select_control(card)
        if not control:
            self.capture_debug_artifacts(f"unassigned_episodes_filter_select_not_found_{self._safe_name(label)}")
            raise AssertionError(f"Filter select not found for label: {label}")
        if not self._control_is_enabled(control):
            self.capture_debug_artifacts(f"unassigned_episodes_filter_select_disabled_{self._safe_name(label)}")
            raise AssertionError(f"Filter select is disabled for label: {label}")

        control.click(force=True)
        self.page.wait_for_timeout(500)

        if seed:
            editable_input = self._select_input(card)
            if editable_input:
                try:
                    editable_input.fill(seed)
                except Exception:
                    self.page.keyboard.type(seed)
            else:
                self.page.keyboard.type(seed)
            self.page.wait_for_timeout(500)

        options = self._visible_dropdown_option_texts()
        self._close_open_dropdown()
        if not options:
            self.capture_debug_artifacts(f"unassigned_episodes_no_dropdown_options_{self._safe_name(label)}")
            raise AssertionError(f"No dropdown options available for label: {label}")
        return options

    def _select_single_multi_option(self, label: str, option_text: str) -> None:
        self._enable_dependent_filter(label)
        card = self._filter_card(label)
        control = self._select_control(card)
        if not control:
            self.capture_debug_artifacts(f"unassigned_episodes_filter_multiselect_not_found_{self._safe_name(label)}")
            raise AssertionError(f"Filter multi-select not found for label: {label}")

        control.click(force=True)
        self.page.wait_for_timeout(300)

        editable_input = self._select_input(card)
        if editable_input:
            try:
                editable_input.fill(option_text)
            except Exception:
                self.page.keyboard.type(option_text)
            self.page.wait_for_timeout(500)

        self._click_dropdown_option(option_text, fallback_to_first=False)
        self._close_open_dropdown()

    def select_filter_value(self, label: str, value: str) -> None:
        self._enable_dependent_filter(label)
        card = self._filter_card(label)
        control = self._select_control(card)
        if not control:
            self.capture_debug_artifacts(f"unassigned_episodes_filter_select_not_found_{self._safe_name(label)}")
            raise AssertionError(f"Filter select not found for label: {label}")
        if not self._control_is_enabled(control):
            self.capture_debug_artifacts(f"unassigned_episodes_filter_select_disabled_{self._safe_name(label)}")
            raise AssertionError(f"Filter select is disabled for label: {label}")
        control.click(force=True)

        editable_input = self._select_input(card)
        if editable_input:
            try:
                editable_input.fill(value)
            except Exception:
                self.page.keyboard.type(value)

        self._click_dropdown_option(value, fallback_to_first=False, fallback_to_enter=False)
        self.page.wait_for_timeout(300)
        if not self._card_has_selected_value(card, value):
            self.capture_debug_artifacts(f"unassigned_episodes_filter_select_value_not_set_{self._safe_name(label)}")
            raise AssertionError(f"Filter select value was not set for label: {label}, value: {value}")

    def select_multi_filter_values(self, label: str, values: str | list[str]) -> None:
        self._enable_dependent_filter(label)
        card = self._filter_card(label)
        value_list = values if isinstance(values, list) else [values]

        for value in value_list:
            dynamic_option = value == self.DYNAMIC_OPTION
            control = self._select_control(card)
            if not control:
                self.capture_debug_artifacts(f"unassigned_episodes_filter_multiselect_not_found_{self._safe_name(label)}")
                raise AssertionError(f"Filter multi-select not found for label: {label}")
            if not self._control_is_enabled(control):
                self.capture_debug_artifacts(f"unassigned_episodes_filter_multiselect_disabled_{self._safe_name(label)}")
                raise AssertionError(f"Filter multi-select is disabled for label: {label}")

            control.click(force=True)
            self.page.wait_for_timeout(300)

            editable_input = self._select_input(card)
            if editable_input and not dynamic_option:
                try:
                    editable_input.fill(str(value))
                except Exception:
                    self.page.keyboard.type(str(value))
            elif not dynamic_option:
                self.page.keyboard.type(str(value))

            self.page.wait_for_timeout(700)
            if dynamic_option:
                self._click_first_dropdown_option(label)
            else:
                self._click_dropdown_option(str(value), fallback_to_first=True)
            self._close_open_dropdown()
            self.page.wait_for_timeout(300)

    def apply_filters(self) -> None:
        self._close_open_dropdown()
        apply_button = self.page.locator(self.APPLY_FILTERS).first
        expect(apply_button).to_be_visible(timeout=10000)
        try:
            apply_button.click(timeout=5000)
        except Exception:
            self._close_open_dropdown()
            apply_button.click(force=True)

    def clear_all_filters(self) -> None:
        self.open_filter_panel()
        clear_button = self._visible_first(self.CLEAR_ALL)
        if not clear_button:
            self.capture_debug_artifacts("unassigned_episodes_clear_filters_not_found")
            raise AssertionError("Clear All/Reset button not found")
        clear_button.click()
        self.wait_for_results()

    def wait_for_results(self) -> None:
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(1000)
        deadline = time.time() + 15
        while time.time() < deadline:
            if self._results_loaded():
                return
            self.page.wait_for_timeout(500)

        self.capture_debug_artifacts("unassigned_episodes_filter_results_not_loaded")
        raise AssertionError("Filter results did not load")

    def _results_loaded(self) -> bool:
        checks = [
            self.page.locator(self.TABLE_ROWS).first,
            self.page.get_by_text(re.compile(r"Total Episodes:\s*\d+", re.I)).first,
            self.page.get_by_text(re.compile(r"No\s+(records|data|episodes)|No results", re.I)).first,
            self.page.get_by_text(re.compile(r"Episode Identifier", re.I)).first,
        ]
        for check in checks:
            try:
                if check.count() > 0 and check.is_visible():
                    return True
            except Exception:
                continue
        return False

    def _filter_card(self, label: str):
        label_pattern = self._label_pattern(label)
        cards = self.page.locator('.workflow-him-filter-card, .workflow-filter-card, .filter-card, .cs-filter-field')
        for index in range(cards.count()):
            card = cards.nth(index)
            try:
                if card.is_visible() and self._card_matches_label(card, label, label_pattern):
                    return card
            except Exception:
                continue

        label_candidates = [
            self.page.locator('label').filter(has_text=label_pattern),
            self.page.get_by_text(label_pattern),
        ]
        for labels in label_candidates:
            try:
                for index in range(labels.count()):
                    label_element = labels.nth(index)
                    if not label_element.is_visible():
                        continue
                    card = label_element.locator('xpath=ancestor::*[contains(@class, "filter")][1]')
                    if card.count() > 0 and card.first.is_visible():
                        return card.first
                    fallback = label_element.locator('xpath=ancestor::div[1]')
                    if fallback.count() > 0 and fallback.first.is_visible():
                        return fallback.first
            except Exception:
                continue

        self.capture_debug_artifacts(f"unassigned_episodes_filter_card_not_found_{self._safe_name(label)}")
        raise AssertionError(f'Filter card not found for label: {label}')

    def _card_matches_label(self, card, label: str, label_pattern: re.Pattern) -> bool:
        try:
            text = card.inner_text(timeout=1000)
        except Exception:
            return False

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if label in ("User Specific", "Queue"):
            return any(label_pattern.fullmatch(line) for line in lines)

        return label_pattern.search(text) is not None

    def _filter_card_count(self) -> int:
        cards = self.page.locator('.workflow-him-filter-card, .workflow-filter-card, .filter-card, .cs-filter-field')
        visible_count = 0
        for index in range(cards.count()):
            try:
                if cards.nth(index).is_visible():
                    visible_count += 1
            except Exception:
                continue
        return visible_count

    def _visible_first(self, selectors):
        for selector in selectors:
            try:
                items = self.page.locator(selector)
                for index in range(items.count()):
                    item = items.nth(index)
                    if item.is_visible():
                        return item
            except Exception:
                continue
        return None

    def _select_control(self, card):
        selectors = [
            '.react-select__control',
            '.react-select__value-container',
            'div[class*="control"]',
            '[role="combobox"]',
            'input[role="combobox"]',
        ]
        for selector in selectors:
            try:
                items = card.locator(selector)
                for index in range(items.count()):
                    item = items.nth(index)
                    if item.is_visible():
                        return item
            except Exception:
                continue
        return None

    def _select_input(self, card):
        selectors = [
            'input[role="combobox"]:not([disabled])',
            'input:not([type="hidden"]):not([disabled])',
        ]
        for selector in selectors:
            try:
                items = card.locator(selector)
                for index in range(items.count()):
                    item = items.nth(index)
                    if item.is_visible():
                        return item
            except Exception:
                continue
        return None

    def _control_is_enabled(self, control) -> bool:
        try:
            if not control.is_enabled():
                return False
        except Exception:
            return False

        try:
            class_name = control.get_attribute("class") or ""
            aria_disabled = control.get_attribute("aria-disabled") or ""
            if "disabled" in class_name.lower() or aria_disabled.lower() == "true":
                return False
        except Exception:
            pass

        try:
            disabled_ancestor = control.locator(
                'xpath=ancestor-or-self::*[contains(translate(@class, "DISABLED", "disabled"), "disabled") or @aria-disabled="true" or @disabled][1]'
            )
            if disabled_ancestor.count() > 0:
                return False
        except Exception:
            pass

        return True

    def _card_has_selected_value(self, card, value: str) -> bool:
        try:
            text = card.inner_text(timeout=1000)
        except Exception:
            return False

        normalized_value = value.strip()
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not normalized_value:
            return False

        normalized_value_lower = normalized_value.casefold()
        lines_lower = [line.casefold() for line in lines]
        text_lower = text.casefold()
        if normalized_value_lower in lines_lower:
            return True

        if re.search(r"\w", normalized_value):
            return normalized_value_lower in text_lower

        return normalized_value_lower in text_lower

    def _click_dropdown_option(self, value: str, fallback_to_first: bool = False, fallback_to_enter: bool = True) -> None:
        exact_pattern = re.compile(rf"^{re.escape(value)}$", re.I)
        contains_pattern = re.compile(re.escape(value), re.I)
        option_selectors = [
            ('role_exact', exact_pattern),
            ('role_contains', contains_pattern),
            ('text_exact', exact_pattern),
            ('text_contains', contains_pattern),
        ]
        if fallback_to_first:
            option_selectors.append(('css_first', None))

        for strategy, pattern in option_selectors:
            try:
                if strategy == 'role_exact':
                    option = self.page.get_by_role("option", name=pattern).first
                elif strategy == 'role_contains':
                    option = self.page.get_by_role("option", name=pattern).first
                elif strategy == 'text_exact':
                    option = self.page.get_by_text(pattern).last
                elif strategy == 'text_contains':
                    option = self.page.get_by_text(pattern).last
                else:
                    option = self.page.locator('[role="option"], .react-select__option, div[id*="-option-"]').first

                if option.count() > 0 and option.is_visible():
                    option.click(force=True)
                    return
            except Exception:
                continue

        if fallback_to_enter:
            try:
                self.page.keyboard.press("Enter")
                return
            except Exception:
                pass

        raise AssertionError(f'Dropdown option not found for value: {value}')

    def _visible_dropdown_option_texts(self, timeout_ms: int = 5000) -> list[str]:
        selectors = [
            '[role="option"]',
            '.react-select__option',
            'div[id*="-option-"]',
        ]
        deadline = time.time() + timeout_ms / 1000

        while time.time() < deadline:
            option_texts = []
            seen = set()
            for selector in selectors:
                try:
                    options = self.page.locator(selector)
                    for index in range(options.count()):
                        option = options.nth(index)
                        if not option.is_visible():
                            continue
                        text = option.inner_text(timeout=500).strip()
                        if not text or text in seen:
                            continue
                        seen.add(text)
                        option_texts.append(text)
                except Exception:
                    continue

                if option_texts:
                    return option_texts  # found options, return immediately

            self.page.wait_for_timeout(300)  # nothing yet, wait and retry

        return []  # timed out — caller handles the empty case

    def _click_first_dropdown_option(self, label: str) -> None:
        selectors = [
            '[role="option"]',
            '.react-select__option',
            'div[id*="-option-"]',
        ]
        for selector in selectors:
            try:
                options = self.page.locator(selector)
                for index in range(options.count()):
                    option = options.nth(index)
                    if option.is_visible():
                        option.click(force=True)
                        return
            except Exception:
                continue

        try:
            self.page.keyboard.press("ArrowDown")
            self.page.keyboard.press("Enter")
            return
        except Exception:
            pass

        self.capture_debug_artifacts(f"unassigned_episodes_no_dropdown_options_{self._safe_name(label)}")
        raise AssertionError(f"No dropdown options available for label: {label}")

    def _close_open_dropdown(self) -> None:
        try:
            options = self.page.locator('[role="option"], .react-select__option, div[id*="-option-"]')
            for index in range(options.count()):
                if options.nth(index).is_visible():
                    self.page.keyboard.press("Escape")
                    self.page.wait_for_timeout(200)
                    return
        except Exception:
            pass

    def _label_pattern(self, label: str) -> re.Pattern:
        if label.upper() == "MRN":
            return re.compile(r"\bMRN(?:/UR)?\b", re.I)
        if label.lower() in ("specialty", "speciality"):
            return re.compile(r"\bSpeciali[at]y\b", re.I)
        if label == "Length of Stay (LOS)":
            return re.compile(r"^Length of Stay \(LOS\)$", re.I)
        return re.compile(re.escape(label), re.I)

    def _safe_name(self, label: str) -> str:
        return re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_")

    def _enable_dependent_filter(self, label: str) -> None:
        prerequisites = {
            "Admission Date To": ("Admission Date From", self.FILTERS["admission_date_from"].value),
            "Separation Date To": ("Separation Date From", self.FILTERS["separation_date_from"].value),
        }
        if label in prerequisites:
            from_label, from_value = prerequisites[label]
            from_card = self._filter_card(from_label)
            from_field = from_card.locator('input:not([type="hidden"]), textarea').first
            expect(from_field).to_be_visible(timeout=10000)
            if from_field.is_enabled():
                from_field.fill(from_value)
                from_field.press("Tab")
                self.page.wait_for_timeout(500)
            return

        if label == "Queue":
            self._ensure_user_specific_set("False")
            self._wait_for_filter_enabled("Queue", timeout=8000)
            return

        if label == "Length of Stay (LOS)":
            self._select_dependency_value("LOS Operator", "=")
            self.page.wait_for_timeout(500)

    def _ensure_user_specific_set(self, value: str) -> None:
        """Guarantee User Specific has the given value selected before proceeding."""
        card = self._filter_card("User Specific")
        if self._card_has_selected_value(card, value):
            return

        control = self._select_control(card)
        if not control:
            raise AssertionError("User Specific select control not found")

        for _ in range(3):
            control.click(force=True)
            self.page.wait_for_timeout(500)
            try:
                self._click_dropdown_option(value, fallback_to_first=False, fallback_to_enter=False)
            except Exception:
                self._close_open_dropdown()
                self.page.wait_for_timeout(300)
                continue

            self.page.wait_for_timeout(700)
            card = self._filter_card("User Specific")
            if self._card_has_selected_value(card, value):
                return

        self.capture_debug_artifacts("unassigned_episodes_user_specific_dependency_not_set")
        raise AssertionError(f"Could not set User Specific to {value}")

    def _select_dependency_value(self, label: str, value: str) -> None:
        card = self._filter_card(label)
        current_text = ""
        try:
            current_text = card.inner_text(timeout=1000)
        except Exception:
            pass
        if value.lower() in current_text.lower():
            return

        control = self._select_control(card)
        if not control:
            raise AssertionError(f"Dependency select not found for label: {label}")
        control.click(force=True)
        self.page.wait_for_timeout(300)

        self._click_dropdown_option(value)
        self.page.wait_for_timeout(500)

    def _wait_for_filter_enabled(self, label: str, timeout: int = 5000) -> None:
        deadline = time.time() + timeout / 1000
        while time.time() < deadline:
            try:
                card = self._filter_card(label)
                control = self._select_control(card)
                if control and self._control_is_enabled(control):
                    return
            except Exception:
                pass
            self.page.wait_for_timeout(300)

        self.capture_debug_artifacts(f"unassigned_episodes_filter_still_disabled_{self._safe_name(label)}")
        raise AssertionError(f"Filter did not become enabled for label: {label}")

    def _visible_filter_toggle(self):
        toggles = self._visible_filter_toggles()
        return toggles[0] if toggles else None

    def _visible_filter_toggles(self):
        visible = []
        selectors = [selector.strip() for selector in self.FILTER_TOGGLE.split(",")]
        for selector in selectors:
            if not selector:
                continue
            try:
                items = self.page.locator(selector)
                for index in range(items.count()):
                    item = items.nth(index)
                    if item.is_visible():
                        visible.append(item)
            except Exception:
                continue
        return visible

    def _coder_workspace_filter_available(self) -> bool:
        checks = [
            self.page.get_by_text(re.compile(r"Coder Workspace", re.I)).first,
            self.page.get_by_placeholder(re.compile(r"Search by Episode ID", re.I)).first,
            self.page.get_by_text(re.compile(r"Episode Identifier|Total Episodes", re.I)).first,
        ]
        for check in checks:
            try:
                if check.count() > 0 and check.is_visible():
                    return self._visible_filter_toggle() is not None
            except Exception:
                continue
        return False


def run_unassigned_episodes_filter_search(username: str, password: str, filter_name: str | None = None) -> None:
    from config.settings import Settings
    from pages.login_page import LoginPage

    settings = Settings(env=os.getenv("ENV", "dev"))
    headless = settings.headless
    headless_env = os.getenv("HEADLESS")
    if headless_env is not None:
        headless = headless_env.lower() in ("1", "true", "yes")

    filters_to_run = [filter_name] if filter_name else UnassignedEpisodesFilterPage.DEFAULT_FILTERS
    known_filters = set(UnassignedEpisodesFilterPage.FILTERS) | set(UnassignedEpisodesFilterPage.FILTER_GROUPS)
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
            filters_page = UnassignedEpisodesFilterPage(page)

            print("Navigating to login page...")
            login_page.open_login_page(settings.base_url)
            login_page.wait_for_page_load()

            print("Performing login...")
            login_page.login(username, password)
            page.wait_for_timeout(3000)

            print("Opening Unassigned Episodes...")
            if not filters_page.open_unassigned_episodes(settings.base_url):
                filters_page.capture_debug_artifacts("unassigned_episodes_filter_navigation_failure")
                raise AssertionError("Could not open Unassigned Episodes page")

            filters_page.open_filter_panel()

            for current_filter in filters_to_run:
                print(f"Applying {current_filter} filter...")
                filters_page.apply_named_filter(current_filter)
                print(f"[OK] {current_filter} filter applied")
                try:
                    filters_page.clear_all_filters()
                except Exception as exc:
                    print(f"Could not clear filters after {current_filter}: {exc}")

            print("Completed Unassigned Episodes filter search run")
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    username = os.getenv("IMEDX_USERNAME", "Sai")
    password = os.getenv("IMEDX_PASSWORD", "Imedx@123")
    selected_filter = os.getenv("IMEDX_FILTER_NAME")
    run_unassigned_episodes_filter_search(username, password, selected_filter)
