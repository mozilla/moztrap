Feature: Staging area for Tests
    in order to do a small test
    as a test developer
    I need to test one scenario at a time

    Scenario: Get list of roles ascending an descending
        Given I create the seed company and product
        And I create a new role with name "Improvisationalist" with the following permissions:
            | permissionCode               |
            | PERMISSION_TEST_CASE_EDIT    |
            | PERMISSION_TEST_CASE_APPROVE |
        And I create a new role with name "StephenColberationalist" with the following permissions:
            | permissionCode               |
            | PERMISSION_TEST_CASE_EDIT    |
            | PERMISSION_TEST_CASE_APPROVE |
        And I create a new role with name "Approvationalist" with the following permissions:
            | permissionCode               |
            | PERMISSION_TEST_CASE_EDIT    |
            | PERMISSION_TEST_CASE_APPROVE |
        Then "ASC" role searches list "Approvationalist" before "StephenColberationalist"
        and "DESC" role searches list "StephenColberationalist" before "Approvationalist"
