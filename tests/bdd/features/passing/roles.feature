Feature: Users Roles
    In order to manage testing roles
    As Users
    We should implement Role management

    Scenario: Create roles, and ensure they show in the list of all roles
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        And I create a new role with name "Approvationalist" with the following permissions:
            | permissionCode               |
            | PERMISSION_TEST_CASE_EDIT    |
            | PERMISSION_TEST_CASE_APPROVE |
        And I create a new role with name "Improvisationalist" with the following permissions:
            | permissionCode               |
            | PERMISSION_TEST_CASE_EDIT    |
            | PERMISSION_TEST_CASE_APPROVE |
        And I create a new role with name "Interrogationalist" with the following permissions:
            | permissionCode               |
            | PERMISSION_TEST_CASE_EDIT    |
            | PERMISSION_TEST_CASE_APPROVE |
        Then at least these roles exist:
            | name               |
            | Approvationalist   |
            | Improvisationalist |
            | Interrogationalist |
        and at least this role exists:
            | name               |
            | Approvationalist   |

    Scenario: Find role by id
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        And I create a new role with name "Approvationalist" with the following permissions:
            | permissionCode               |
            | PERMISSION_TEST_CASE_EDIT    |
            | PERMISSION_TEST_CASE_APPROVE |
        Then I can find the role with that name by id

    Scenario: Give a user multiple roles, then remove one, and add it back
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        And I create a new user with name "Walter Bishop"
        And I create a new role with name "Approvationalist" with the following permissions:
            | permissionCode               |
            | PERMISSION_TEST_CASE_EDIT    |
            | PERMISSION_TEST_CASE_APPROVE |
        And I create a new role with name "Improvisationalist" with the following permissions:
            | permissionCode               |
            | PERMISSION_TEST_CASE_EDIT    |
            | PERMISSION_TEST_CASE_APPROVE |
        And I create a new role with name "Interrogationalist" with the following permissions:
            | permissionCode               |
            | PERMISSION_TEST_CASE_EDIT    |
            | PERMISSION_TEST_CASE_APPROVE |
        When I add the following roles to the user with that name
            | name               |
            | Approvationalist   |
            | Improvisationalist |
            | Interrogationalist |
        Then the user with that name has exactly these roles:
            | name               |
            | Approvationalist   |
            | Improvisationalist |
            | Interrogationalist |
        And when I remove the role with name "Interrogationalist" from the user with that name
        Then the user with that name has exactly these roles:
            | name               |
            | Approvationalist   |
            | Improvisationalist |
        And when I add the role with that name to the user with that name
        Then the user with that name has exactly these roles:
            | name               |
            | Approvationalist   |
            | Improvisationalist |
            | Interrogationalist |

    Scenario: Give a user multiple roles, then replace with fewer
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        And I create a new user with name "Walter Bishop"
        And I create a new role with name "Approvationalist" with the following permissions:
            | permissionCode               |
            | PERMISSION_TEST_CASE_EDIT    |
            | PERMISSION_TEST_CASE_APPROVE |
        And I create a new role with name "Improvisationalist" with the following permissions:
            | permissionCode               |
            | PERMISSION_TEST_CASE_EDIT    |
            | PERMISSION_TEST_CASE_APPROVE |
        And I create a new role with name "Interrogationalist" with the following permissions:
            | permissionCode               |
            | PERMISSION_TEST_CASE_EDIT    |
            | PERMISSION_TEST_CASE_APPROVE |
        When I add the following roles to the user with that name
            | name               |
            | Approvationalist   |
            | Improvisationalist |
            | Interrogationalist |
        Then the user with that name has exactly these roles:
            | name               |
            | Approvationalist   |
            | Improvisationalist |
            | Interrogationalist |
        And when I replace the role list for the user with that name with these roles
            | name               |
            | Approvationalist   |
            | Interrogationalist |
        Then the user with that name has exactly these roles:
            | name               |
            | Approvationalist   |
            | Interrogationalist |

    Scenario: Get list of roles ascending an descending
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
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

    Scenario: Give a user a role and check permissions
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        And I create a new user with name "Walter Bishop"
        And I create a new role with name "Approvationalist" with the following permissions:
            | permissionCode               |
            | PERMISSION_TEST_CASE_EDIT    |
            | PERMISSION_TEST_CASE_APPROVE |
        When I add the following roles to the user with that name
            | name               |
            | Approvationalist   |
        Then the user with that name has exactly these permissions:
            | permissionCode                            |
            | PERMISSION_TEST_CASE_EDIT                 |
            | PERMISSION_TEST_CASE_APPROVE              |
            | PERMISSION_TEST_RUN_TEST_CASE_SELF_ASSIGN |

