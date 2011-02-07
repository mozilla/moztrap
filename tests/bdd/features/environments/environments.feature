Feature: Environment Object Business Rules
    In order to support multiple environments
    As an Administrator
    I should support the business rules for the Environment Object
    
    Scenario: Environment - Creation
        Given environment with name "Walter's Lab" does not exist
        when I create a new environment with that name
        Then an environment with that name exists

    Scenario: Environment - types 
        Given I create a new environmenttype group with name "Desktop"
        and I create a new environmenttype group with name "Mobile"
        and I create a new environmenttype with name "Language"
        and I create a new environmenttype with name "OS"
        when I create a new environment with name "English" of type Language
        when I create a new environment with name "French" of type Language
        when I create a new environment with name "OS X" of type OS
        when I create a new environment with name "Linux Ubuntu" of type OS

    Scenario: Environment - Add to Product 
        Given I create a new environment with name "Walter's Lab"
        and Given I create a new product with name "Continuum Transfunctioner"
        And the product with that name does not have the environment with that name 
        When I add the environment with name "Walter's Lab" to the product with that name
        Then product "Continuum Transfunctioner" has environment "Walter's Lab" 

    Scenario: Environment - Remove from Product
        Given I am logged in as user "Jedi Creator"
        And I have the role of "PRODUCT_EDITOR"
        And Environment "Walter's Lab" exists
        And Product "Continuum Transfunctioner" exists
        And product "Continuum Transfunctioner" has environment "Walter's Lab" 
        When I remove environment "Walter's Lab" from product "Continuum Transfunctioner"
        Then product "Continuum Transfunctioner" does not have environment "Walter's Lab" 

    Scenario: Environment - Add to Test Case 
        Given I am logged in as user "Jedi Creator"
        And I have the role of "TEST_EDITOR"
        And Environment "Walter's Lab" exists
        And test case "Wazzon Chokey?" exists
        And test case "Wazzon Chokey?" does not have environment "Walter's Lab" 
        When I add environment "Walter's Lab" to test case "Wazzon Chokey?"
        Then test case "Wazzon Chokey?" has environment "Walter's Lab" 

    Scenario: Environment - Remove from Test Case
        Given I am logged in as user "Jedi Creator"
        And I have the role of "TEST_EDITOR"
        And Environment "Walter's Lab" exists
        And test case "Wazzon Chokey?" exists
        Then test case "Wazzon Chokey?" has environment "Walter's Lab" 
        When I remove environment "Walter's Lab" from test case "Wazzon Chokey?"
        Then test case "Wazzon Chokey?" does not have environment "Walter's Lab" 

    Scenario: Environment - Add to Test Cycle
        Not Implemented

    Scenario: Environment - Remove from Test Cycle
        Not Implemented

    Scenario: Environment - Create Test Run Result
        Not Implemented

    Scenario: Environment Type - Creation
        Given I am logged in as user "Jedi Creator"
        And I have the role of "ENVIRONMENT_CREATOR"
        And environment type "Laboratory" does not exist
        when I add a new environment type with name "Laboratory"
        Then environment type "Laboratory" exists
        