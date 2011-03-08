Feature: Staging area for Tests
    in order to do a small test
    as a test developer
    I need to test one scenario at a time

    Scenario: Test the emailconfirm endpoint
        Given I create the seed company and product
        And I create a new user with name "Olivia Dunham"
        And the user with that name is inactive
        When I confirm the email for the user with that name
        Then the user with that name is active
        And when I change the email to "flip@flop.net" for the user with that name
        Then the user with that name is inactive
        And when I confirm the email for the user with that name
        Then the user with that name is active


