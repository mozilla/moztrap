Feature: Environment Object Business Rules
    In order to support multiple environments
    As an Administrator
    I should support the business rules for the Environment Object
    
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

    Scenario: Environment - Add to Product 
        Given I create the seed company and product
        And I create a new environmenttype with name "Brickhouse"
        And I create a new environment with name "Walter's Lab" of type "Brickhouse"
        And the product with name "Cortexiphan" does not have the environment with that name 
        When I add the environment with name "Walter's Lab" to the product with that name
        Then product "Continuum Transfunctioner" has environment "Walter's Lab" 

    Scenario: Environment - Remove from Product
        Given I create the seed company and product
        Not yet implemented
        And I am logged in as user "Jedi Creator"
        And I have the role of "PRODUCT_EDITOR"
        And Environment "Walter's Lab" exists
        And Product "Continuum Transfunctioner" exists
        And product "Continuum Transfunctioner" has environment "Walter's Lab" 
        When I remove environment "Walter's Lab" from product "Continuum Transfunctioner"
        Then product "Continuum Transfunctioner" does not have environment "Walter's Lab" 

    Scenario: Environment - Add to Test Case 
        Not Implemented
    
    Scenario: Environment - Remove from Test Case
        Not Implemented

    Scenario: Environment - Add to Test Cycle
        Not Implemented

    Scenario: Environment - Remove from Test Cycle
        Not Implemented

    Scenario: Environment - Create Test Run Result
        Not Implemented

    Scenario: Environment Type - Creation
        Not Implemented
        