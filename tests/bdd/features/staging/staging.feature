Feature: Staging area for Tests
    in order to do a small test
    as a test developer
    I need to test one scenario at a time

    Scenario: Add testruns to testcycle and verify
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        And when I create the following new testcycles:
            | name          | description               | product name | startDate  | endDate    | communityAuthoringAllowed | communityAccessAllowed |
            | Baroque Cycle | Ahh, the cycle of life... | Cortexiphan  | 2011/02/02 | 2012/02/02 | true                      | true                   |
        And when I create a new testrun with name "Running Man" with testcycle "Baroque Cycle"
        And when I create a new testrun with name "Running Woman" with testcycle "Baroque Cycle"
        And when I create a new testrun with name "Running Girl" with testcycle "Baroque Cycle"
        And when I create a new testrun with name "Running Boy" with testcycle "Baroque Cycle"
        Then the testcycle with name "Baroque Cycle" has the following testruns:
            | name          |
            | Running Man   |
            | Running Woman |
            | Running Girl  |
            | Running Boy   |


