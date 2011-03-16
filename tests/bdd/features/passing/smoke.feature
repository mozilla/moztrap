Feature: Smoke Tests
    In order to perform small, quick tests of the TCM
    As a tester
    I want to be able to run short, simple tests

    Scenario: Create and delete a company
        Given company with name "macho face" does not exist
        when I create a new company with name "macho face"
        then a company with name "macho face" exists
        and when I delete the company with that name
        then a company with that name does not exist

    Scenario: Create and then deactivate a new user
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        And a user with name "Nowhere Man" does not exist
        When I create a new user with that name
        Then a user with that name exists
        and the user with that name is inactive
        and when I activate the user with that name
        Then the user with that name is active
        and when I deactivate the user with that name
        Then the user with that name is disabled
        And when I activate the user with that name
        Then the user with that name is active


    Scenario: Create and delete a Product
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        And a product with name "Camera Pencil Sharpener" does not exist
        when I create a new product with that name
        then a product with that name exists
        and when I delete the product with that name
        then the product with that name does not exist

    Scenario: Create and delete an Environmenttype
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        And an environmenttype with name "Come on fhqwhgads" does not exist
        when I create a new environmenttype with that name
        then an environmenttype with that name exists
        and when I delete the environmenttype with that name
        then an environmenttype with that name does not exist

    Scenario: Create and delete an Environment
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        And I create a new environmenttype with name "Obfuscated"
        And an environment with name "Come on fhqwhgads" does not exist
        when I create a new environment with that name of type "Obfuscated"
        then an environment with that name exists
        and when I delete the environment with that name
        then an environment with that name does not exist

    Scenario: Create and delete a group Environmenttype
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        And an environmenttype with name "Come on fhqwhgads" does not exist
        when I create a new group environmenttype with that name of type operating
        then an environmenttype with that name exists
        and the environmenttype with that name is a group environmenttype
        and when I delete the environmenttype with that name
        then an environmenttype with that name does not exist

    Scenario: Create and delete a group Environmenttype
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        And an environmenttype with name "Come on fhqwhgads" does not exist
        when I create a new group environmenttype with that name of type operating
        then a group environmenttype with that name exists
        and when I delete the environmenttype with that name
        then an environmenttype with that name does not exist

    Scenario: Create and delete an Environmentgroup
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        And I create a new group environmenttype with name "Group Type Thing"
        and an environmentgroup with name "Come on fhqwhgads" does not exist
        When I create a new environmentgroup with that name of type "Group Type Thing"
        Then an environmentgroup with that name exists
        and when I delete the environmentgroup with that name
        then an environmentgroup with that name does not exist

    Scenario: Create and delete a tag
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        And a tag with tag "You are IT" does not exist
        when I create a new tag with that tag
        then a tag with that tag exists
        and when I delete the tag with that tag
        then a tag with that tag does not exist

    Scenario: Create and delete a Testcase
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        And a testcase with name "Come on fhqwhgads" does not exist
        when I create a new testcase with that name
        then a testcase with that name exists
        and when I delete the testcase with that name
        then a testcase with that name does not exist

    Scenario: Create and delete a Testsuite
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        And a testsuite with name "Time-Sweetened Honey" does not exist
        when I create a new testsuite with that name
        then a testsuite with that name exists
        and when I delete the testsuite with that name
        then a testsuite with that name does not exist

    Scenario: Create a Testcycle and Testrun then delete them
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        And I create a new product with name "Continuum Transfunctioner"
        And given a testcycle with name "Baroque Cycle" does not exist
        when I create the following new testcycles:
            | name          | description               | product name              | startDate  | endDate    | communityAuthoringAllowed | communityAccessAllowed |
            | Baroque Cycle | Ahh, the cycle of life... | Continuum Transfunctioner | 2011/02/02 | 2012/02/02 | true                      | true                   |
        then a testcycle with that name exists
        and when I create a new testrun with name "Running Man" with testcycle "Baroque Cycle"
        then a testrun with that name exists
        and when I delete the testrun with that name
        then the testrun with that name does not exist
        and when I delete the testcycle with that name
        then the testcycle with that name does not exist

