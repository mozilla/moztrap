Feature: User Administration
    In order to update an existing user
    As an Administrator
    I want to be able to change user values

    Scenario: Change user's email
        Given I create the seed company and product
        And I create a new user with name "Walter Bishop"
        When I change the email to "brick@brack.net" for the user with that name
        Then the user with that name has these values:
            | firstName | lastName | email           | screenName    | company name    |
            | Walter    | Bishop   | brick@brack.net | WalterBishop | Massive Dynamic |

    Scenario: Change user's password
        Given I create the seed company and product
        And I create a new user with name "Walter Bishop"
        When I change the password to "cortexiphan" for the user with that name
        And when I log in user with these credentials:
            | email                    | password    |
            | WalterBishop@mozilla.com | cortexiphan |
        Then I am logged in as the user with that name
