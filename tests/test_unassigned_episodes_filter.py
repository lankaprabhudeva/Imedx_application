import json
from pathlib import Path

import pytest

from pages.login_page import LoginPage
from pages.filters_search import UnassignedEpisodesFilterPage


class TestUnassignedEpisodesFilters:
    """One test per Unassigned Episodes filter."""

    @pytest.fixture(scope="class")
    def test_data(self):
        data_file = Path("test_data/login_test_data.json")
        with open(data_file, "r") as f:
            return json.load(f)

    @pytest.fixture(autouse=True)
    def open_unassigned_episodes(self, page, app_settings, test_data):
        login_page = LoginPage(page)
        filters_page = UnassignedEpisodesFilterPage(page)

        login_page.open_login_page(app_settings.base_url)
        login_page.wait_for_page_load()
        login_page.login(test_data["valid_user"]["username"], test_data["valid_user"]["password"])
        page.wait_for_timeout(3000)

        assert filters_page.open_unassigned_episodes(), "Could not open Unassigned Episodes page"
        filters_page.open_filter_panel()
        return filters_page

    def test_episode_identifier_filter(self, open_unassigned_episodes):
        open_unassigned_episodes.apply_named_filter("episode_identifier")

    def test_mrn_filter(self, open_unassigned_episodes):
        open_unassigned_episodes.apply_named_filter("mrn")

    def test_admission_date_range_filter(self, open_unassigned_episodes):
        open_unassigned_episodes.apply_named_filter("admission_date_range")

    def test_separation_date_range_filter(self, open_unassigned_episodes):
        open_unassigned_episodes.apply_named_filter("separation_date_range")

    def test_specialty_filter(self, open_unassigned_episodes):
        open_unassigned_episodes.apply_named_filter("specialty")

    def test_queue_filter(self, open_unassigned_episodes):
        open_unassigned_episodes.apply_named_filter("queue")

    def test_user_specific_filter(self, open_unassigned_episodes):
        open_unassigned_episodes.apply_named_filter("user_specific")

    def test_priority_filter(self, open_unassigned_episodes):
        open_unassigned_episodes.apply_named_filter("priority")

    def test_status_filter(self, open_unassigned_episodes):
        open_unassigned_episodes.apply_named_filter("status")

    def test_health_fund_contract_filter(self, open_unassigned_episodes):
        open_unassigned_episodes.apply_named_filter("health_fund_contract")

    def test_los_filter(self, open_unassigned_episodes):
        open_unassigned_episodes.apply_named_filter("los")

    def test_los_operator_filter(self, open_unassigned_episodes):
        open_unassigned_episodes.apply_named_filter("los_operator")

    def test_provisional_drg_filter(self, open_unassigned_episodes):
        open_unassigned_episodes.apply_named_filter("provisional_drg")

    def test_clear_all_filter(self, open_unassigned_episodes):
        open_unassigned_episodes.apply_named_filter("status")
        open_unassigned_episodes.clear_all_filters()
