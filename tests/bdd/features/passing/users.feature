Feature: User Administration
    In order to update an existing user
    As an Administrator
    I want to be able to change user values

    Scenario: Change user's email
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        And I create a new user with name "Walter Bishop"
        When I change the email to "newemail@me.com" for the user with that name
        Then the user with that name has these values:
            | firstName | lastName | email           | screenName    | company name    |
            | Walter    | Bishop   | newemail@me.com | WalterBishop | Massive Dynamic |

    Scenario: Confirm an email address
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        And I create a new user with name "Olivia Dunham"
        And the user with that name is inactive
        When I confirm the email for the user with that name
        Then the user with that name is active
        And when I change the email to "flip@flop.net" for the user with that name
        Then the user with that name is inactive
        And when I confirm the email for the user with that name
        Then the user with that name is active

    Scenario: Change user's password
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        And I create a new user with name "Walter Bishop"
        When I change the password to "newpassword" for the user with that name
        And when I log in user with these credentials:
            | email                    | password    |
            | WalterBishop@mozilla.com | newpassword |
        Then I am logged in as the user with that name

    Scenario: Get specific User by id
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        And I create a new user with name "Olivia Dunham"
        Then I can get that newly created user by id

    Scenario: Update User information
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        And I create a new user with name "Walter Bishop"
        Then the user with that name has these values:
            | firstName | lastName | company name    |
            | Walter    | Bishop   | Massive Dynamic |
        And I create a new company with name "Ace Max Detectives"
        When I update the user with that name to have these values:
            | firstName | lastName  | company name       |
            | Walterman | Bishopman | Ace Max Detectives |
        Then that user has these values:
            | firstName | lastName  | company name       |
            | Walterman | Bishopman | Ace Max Detectives |
