Feature: Users Test Cases
    In order to work with test cases
    As Users
    We'll implement Test Case management

    Scenario: Create a new Test Case
        Given I am logged in as user "Jedi Creator"
        and user "Jedi Creator" has the role of "TEST_CREATOR"
        When I submit a new test case with name "Testing mic #1.  Isn't this a lot of fun." 
        Then a test case with name "Testing mic #1.  Isn't this a lot of fun." exists
        
        
