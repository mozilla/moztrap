Feature: Testbed for Tests
    in order to do a small test
    as a test developer
    I need to test one scenario at a time

    Scenario: Create a Testcycle and Testrun then delete them
        Given a testcycle with name "Baroque Cycle" does not exist
        when I create a new testcycle with that name
        then a testcycle with that name exists
        and when I create a new testrun with name "Running Man" with testcycle "Baroque Cycle"
        then a testrun with that name exists
        and the testcycle with name "Baroque Cycle" has the testrun with name "Running Man"
