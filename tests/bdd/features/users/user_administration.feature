Feature: User Administration
    In order to update an existing user
    As an Administrator
    I want to be able to change user values


    Scenario: Assign a Role to a User
        Given I create the role of
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
    