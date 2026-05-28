Feature: Re-assign Unassigned Episodes
  As a user
  I want to reassign an unassigned episode from HIM Workspace
  So that episodes are routed to the correct coder queue

  Scenario: Open the Re-assign popup from an unassigned episode
    Given user logs into the application
    When user clicks on the breadcrumb menu
    And user clicks on "HIM Workspace"
    And user clicks on "Unassigned Episodes"
    And user selects an episode checkbox
    Then "Re-assign" button should be displayed

    When user clicks on the "Re-assign" button
    Then re-assignment popup should be displayed

  Scenario: Re-assign an unassigned episode successfully
    Given user logs into the application
    When user clicks on the breadcrumb menu
    And user clicks on "HIM Workspace"
    And user clicks on "Unassigned Episodes"
    And user selects the third episode checkbox
    Then "Re-assign" button should be displayed

    When user clicks on the "Re-assign" button
    Then re-assignment popup should be displayed

    When user selects a value from the Queue dropdown
    And user selects the first option from the Coder dropdown
    And user clicks on "Confirm Assignment"
    Then episode should be reassigned successfully
