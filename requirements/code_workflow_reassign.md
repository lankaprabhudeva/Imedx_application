# Code Workflow Reassign Requirement

## User Story
As a coder, I want to reassign an unassigned episode in the Code Workflow page to coder `prabhu`, so that the episode is assigned correctly for coding review.

## Acceptance Criteria
- User can log in successfully with valid credentials.
- The user can navigate to the Code Workflow page after login.
- The user can open the HIM Workspace from Code Workflow.
- The user is redirected to the Unassigned Episodes page.
- The user can select an episode using its checkbox.
- The user can open the Reassign dialog.
- The user can type `prabhu` into the Coder dropdown or input.
- The user can click the Confirm/Confirm DRG button.
- The selected episode is reassigned successfully.

## Preconditions
- The test environment contains at least one unassigned episode.
- The application URL is configured in `config/environments.yaml`.
- The user credentials are valid: `Sai` / `Imedx@123`.

## Notes
- If no unassigned episodes exist, the E2E test should be skipped or environment data should be seeded.
- Use Playwright to navigate and operate on the DOM elements.

## Test Case
- `test_reassign_episode_to_coder_prabhu`
- Steps:
  1. Login with valid credentials
  2. Navigate to Code Workflow / HIM Workspace
  3. Navigate to Unassigned Episodes
  4. Select the first available episode
  5. Open the Reassign popup
  6. Choose coder `prabhu`
  7. Confirm the DRG reassignment

## Result
- The episode should be assigned to coder `prabhu`, and the flow should complete without errors.
