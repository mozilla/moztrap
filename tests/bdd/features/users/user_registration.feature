Feature: New Users
    In order to have a user base
    As a User
    I want to be able to register

    Scenario: Register a new user
        Given user "Jedi Jones" is not registered
        When create new user named "Jedi Jones"
        Then user "Jedi Jones" is registered
        And user "Jedi Jones" has active status "false"
        
    
    