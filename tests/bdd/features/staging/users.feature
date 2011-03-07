Feature: User Administration
    In order to update an existing user
    As an Administrator
    I want to be able to change user values


    Scenario: Log in and out as user: (Bug 636586)
        Given I create the seed company and product
        And I create a new user with name "Walter Bishop"
        When I log in user with that name
        Then I am logged in as the user with that name
        And when I log out the user with that name
        Then that user is not logged in

    Scenario: Update User information (Bug 638935)
        Given I create the seed company and product
        And I create a new user with name "Walter Bishop"
        And I create a new company with name "Ace Max Detectives"
        When I update the user with that name to have these values:
            | firstName | lastName | email               | screenName | company name       |
            | Walter    | Bishop   | doctor@horrible.com | drHorrible | Ace Max Detectives |
        Then the user with that name has these values:
            | firstName | lastName | email               | screenName | company name       |
            | Walter    | Bishop   | doctor@horrible.com | drHorrible | Massive Dynamic    |


    Scenario: Get specific User by id
    Scenario: Search for Users

    Scenario: Check the Assignments of a User
        Given user "Jedi Assigned" has active status "true"
        Then verify that user "Jedi Assigned" has these assignments:
            | name                 |
            | What the cat dragged in     |
            | Where I put the keys        |

    Scenario: Prevented from creating a new user with conflicting email
        Given user with email "admin@utest.com" exists
        Then I am prevented from creating new user with email "admin@utest.com"

    Scenario: Prevented from creating a new user with conflicting screenname
        Given user with screenname "adminadmin" exists
        Then I am prevented from creating new user with screenname "adminadmin"
