Feature: User Administration
    In order to update an existing user
    As an Administrator
    I want to be able to change user values

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
