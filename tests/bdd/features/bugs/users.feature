Feature: Some bugs with regard to User Administration
    In order to update an existing user
    As an Administrator
    I want to be able to change user values


    Scenario: Log in and out as user, should no longer be logged in: (Bug 636586)
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        And I create a new user with name "Walter Bishop"
        When I log in user with that name
        Then I am logged in as the user with that name
        And when I log out the user with that name
        Then that user is not logged in

