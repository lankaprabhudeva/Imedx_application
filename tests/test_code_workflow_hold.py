import pytest
from pages.login_page import LoginPage
from pages.unassignepisode_page import UnassignedEpisodePage
from pages.coder_workspace_page import CoderWorkspacePage


class TestCodeWorkflowHoldFlow:
    def test_repeat_on_hold_and_confirm_drg(self, page, app_settings):
        login_page = LoginPage(page)
        unassigned = UnassignedEpisodePage(page)
        workspace = CoderWorkspacePage(page)

        # Login and navigate to the code workflow area
        login_page.open_login_page(app_settings.base_url)
        login_page.login("Sai", "Imedx@123")

        assert unassigned.open_code_workflow() or unassigned.open_him_workspace(), "Could not open Code Workflow/HIM Workspace"
        assert unassigned.open_coder_workspace(), "Could not open Coder Workspace"

        # Find the first outstanding episode, open it, and use Code Assist
        episode_id = unassigned.open_outstanding_episode()
        assert episode_id, "No outstanding episode ID was captured"

        assert workspace.open_code_assist(), "Could not open Code Assist"
        assert workspace.add_principal_diagnosis("Q87.19"), "Could not add principal diagnosis"
        assert workspace.put_on_hold(), "Could not put episode on hold"

        # Return to the breadcrumb and re-open the same episode twice
        assert workspace.click_breadcrumb_code_workflow() or unassigned.open_code_workflow(), "Could not return to Code Workflow breadcrumb"
        assert unassigned.open_coder_workspace(), "Could not open Coder Workspace again"
        assert workspace.search_episode_by_id(episode_id), "Could not search episode by ID"
        assert workspace.open_episode_by_id(episode_id), "Could not open episode from search results"

        assert workspace.add_additional_code("B83.8"), "Could not add additional code"
        assert workspace.put_on_hold(), "Could not put episode on hold a second time"

        assert workspace.click_breadcrumb_code_workflow() or unassigned.open_code_workflow(), "Could not return to Code Workflow breadcrumb a second time"
        assert unassigned.open_coder_workspace(), "Could not open Coder Workspace again"
        assert workspace.search_episode_by_id(episode_id), "Could not search episode by ID again"
        assert workspace.open_episode_by_id(episode_id), "Could not open episode from search results again"

        assert workspace.confirm_drg(), "Could not confirm DRG"
