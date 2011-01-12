Feature: Company Administration
    In order to support multiple companies
    As an Administrator
    I want to be able to administer company entries
    
    Scenario: Create a new Company
        Given I am logged in as user "Jedi Creator"
        And user "Jedi Creator" has the role of "COMPANY_CREATOR"
        And company "Massive Dynamic" does not exist
        when I add a new company with name "Massive Dynamic"
        Then company "Massive Dynamic" exists

    Scenario: Query Companies
        When I search all Companies
        Then these companies exist   	



