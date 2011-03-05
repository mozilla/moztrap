Feature: Staging area for Tests
    in order to do a small test
    as a test developer
    I need to test one scenario at a time

    Scenario: Log in and out as user
        Given I create the seed company and product
        And I create a new user with name "Walter Bishop"
        When I log in user with that name
        Then I am logged in as the user with that name
        And when I log out the user with that name
        Then that user is not logged in
        