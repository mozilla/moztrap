Feature: User Administration
    In order to update an existing user
    As an Administrator
    I want to be able to change user values

    Scenario: Create a new user, activate, then deactivate, then reactivate that user
        Given user with name "Jedi Jones" does not exist
        When I create a new user with that name
        Then the user with that name exists
        And the user with that name is inactive
        and when I activate the user with that name
        then the user with that name is active
        And when I deactivate the user with that name
        Then the user with that name is disabled
        And when I activate the user with that name
        Then the user with that name is active

    Scenario: Assign a Role to a User
        Given the user with name "Admin Admin" is active
        And the role of "CHIPPER" exists
        And user with name "Jedi Roller" does not already have the role of "CHIPPER"
        When I add role of "CHIPPER" to user "Jedi Roller"
        Then user with name "Jedi Roller" has the role of "CHIPPER"
        
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
    
    Scenario: Prevented from creating a new user with conflicting email
        Given user with email "admin@utest.com" exists
        Then I am prevented from creating new user with email "admin@utest.com"

    Scenario: Prevented from creating a new user with conflicting screenname
        Given user with screenname "adminadmin" exists
        Then I am prevented from creating new user with screenname "adminadmin"
    