Feature: Staging area for Tests
    in order to do a small test
    as a test developer
    I need to test one scenario at a time

    Scenario: Get specific User by id
        Given I create the seed company and product
        And I create a new user with name "Olivia Dunham"
        Then I can get that newly created user by id