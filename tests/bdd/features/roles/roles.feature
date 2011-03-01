Feature: Users Roles
    In order to manage testing roles
    As Users
    We should implement Role management

    Scenario: Create roles, and ensure they show in the list of all roles
        Given I create the seed company and product
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
        Given I create the seed company and product
        And I create a new role with name "Approvationalist" with the following permissions:
            | permissionCode               |
            | PERMISSION_TEST_CASE_EDIT    |
            | PERMISSION_TEST_CASE_APPROVE |
        Then I can find the role with that name by id        
        
    Scenario: Get list of roles
        Given at least these roles exist:
            | description |
            | Frame       |
            | Apple       |
            | Zipper      |
        Then "ASC" role searches list "Apple" before "Zipper"
        and "DESC" role searches list "Zipper" before "Apple"
        
    Scenario: Create a new Role and add Permission
        Given I am logged in as user "Jedi Admin"
        and user "Jedi Admin" has the role of "ADMINISTRATOR"
        When I create a new role of "Creationator"
        and add permission of "Spammer" to the role of "Creationator"
        Then role of "Creationator" has permission of "Spammer"

    
   