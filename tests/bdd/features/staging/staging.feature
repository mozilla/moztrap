Feature: Staging area for Tests
    in order to do a small test
    as a test developer
    I need to test one scenario at a time

    Scenario: Create a Testcycle and Testrun then delete them
        Given I create a new product with name "Continuum Transfunctioner"
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
