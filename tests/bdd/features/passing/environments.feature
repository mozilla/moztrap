Feature: Environment Object Business Rules
    In order to support multiple environments
    As an Administrator
    I should support the business rules for the Environment Object
    
    Scenario: Environment - Creation
        Given I create the seed company and product
        And an environment with name "Walter's Lab" does not exist
        when I create a new environmenttype with name "Brickhouse"
        when I create a new environment with that name of type "Brickhouse"
        Then an environment with that name exists
