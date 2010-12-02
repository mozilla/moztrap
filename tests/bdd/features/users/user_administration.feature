Feature: User Administration
    In order to update an existing user
    As an Administrator
    I want to be able to change user values

    Scenario: Activate a Non Active user
        Given user "Jedi NotActive" is registered
        And user "Jedi NotActive" has active status "false"
        When I activate user "Jedi NotActive"
        Then user "Jedi NotActive" has active status "true"

    Scenario: Deactivate an Active user
        Given user "Jedi Active" is registered
        And user "Jedi Active" has active status "true"
        When I activate user "Jedi Active"
        Then user "Jedi Active" has active status "false"

    Scenario: Assign a Role to a User
        Given user "Jedi Roller" has active status "true"
        And the role of "CHIPPER" exists
        And user "Jedi Roller" does not already have the role of "CHIPPER"
        When I add role of "CHIPPER" to user "Jedi Roller"
        Then user "Jedi Roller" has the role of "CHIPPER"
        
    Scenario: Delete a role from a User
    
    Scenario: Check Roles of a User
        Given user "Jedi Roller" has active status "true"
    	Then verify that user "Jedi Roller" has these roles:
            | description |
            | SMASHER     |
            | MASHER      |

    	
    Scenario: Check the Assignments of a User
        Given user "Jedi Assigned" has active status "true"
    	Then verify that user "Jedi Assigned" has these assignments:
            | name                 |
            | What the cat dragged in     |
            | Where I put the keys        |

    Scenario: Update User information
    Scenario: Change User's password
    Scenario: Get specific User by id
    Scenario: Search for Users
    
    