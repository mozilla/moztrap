Feature: Smoke Tests
    In order to test my steps
    As a Lettuce developer
    I want to be able to run test snippets to test the framework
 
    Scenario: Create and unregister a new user
        Given a user with name "Jimmy Smitz" does not exist
        When I create a new user with that name
        Then a user with that name exists
        and the user with that name is inactive
        and when I activate the user with that name
        Then the user with that name is active
        and when I deactivate the user with that name
        Then the user with that name is disabled
