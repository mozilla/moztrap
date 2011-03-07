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

    Scenario: Environment - types
        Given I create the seed company and product
        And I create a new group environmenttype with name "Desktop"
        and I create a new group environmenttype with name "Mobile"
        and I create a new environmenttype with name "Language"
        and I create a new environmenttype with name "OS"
        when I create a new environment with name "English" of type "Language"
        when I create a new environment with name "French" of type "Language"
        when I create a new environment with name "OS X" of type "OS"
        when I create a new environment with name "Linux Ubuntu" of type "OS"
        Then at least the following environments exist:
            | name         | type     |
            | English      | Language |
            | French       | Language |
            | OS X         | OS       |
            | Linux Ubuntu | OS       |

