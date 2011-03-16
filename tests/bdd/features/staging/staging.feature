Feature: Staging area for Tests
    in order to do a small test
    as a test developer
    I need to test one scenario at a time

    Scenario: Add an environmentgroup to a testrun
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        And I add the following components to that product:
            | name     | description      |
            | chunk    | The chunky part  |
            | squish   | The squishy part |
        And I create the following new testcycles:
            | name          | description               | product name | startDate  | endDate    | communityAuthoringAllowed | communityAccessAllowed |
            | Baroque Cycle | Ahh, the cycle of life... | Cortexiphan  | 2011/02/02 | 2012/02/02 | true                      | true                   |
        And I create a new testrun with name "Running Man" with testcycle "Baroque Cycle"
        Then that testrun has the following components:
            | name     | description      |
            | chunk    | The chunky part  |
            | squish   | The squishy part |



