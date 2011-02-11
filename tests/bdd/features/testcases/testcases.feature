Feature: Test Cases

    Scenario: Create and approve a Testcase with steps
        Given a testcase with name "Come on fhqwhgads" does not exist
        when I create a new testcase with that name
        then a testcase with that name exists
        and when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
            | Flockery  | 2          | 2                  | Go that way    | They went that way    |
            | Chockery  | 3          | 4                  | Go my way      | They went my way      |
            | Trockery  | 4          | 1                  | Go the highway | They went the highway |
            | Blockery  | 5          | 25                 | Just go away   | They went away        |
        then the testcase with that name has steps with these values:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
            | Flockery  | 2          | 2                  | Go that way    | They went that way    |
            | Chockery  | 3          | 4                  | Go my way      | They went my way      |
            | Trockery  | 4          | 1                  | Go the highway | They went the highway |
            | Blockery  | 5          | 25                 | Just go away   | They went away        |
        and when I approve that testcase
        then that testcase has status of approved
        
    Scenario: add a testcase to a testrun
        Not implemented yet

    Scenario: Create a Testcycle and Testrun and verify the testrun is in the testcycle
        Given a testcycle with name "Baroque Cycle" does not exist
        when I create a new testcycle with that name
        then a testcycle with that name exists
        and when I create a new testrun with name "Running Man" with testcycle "Baroque Cycle"
        then a testrun with that name exists
        and the testcycle with name "Baroque Cycle" has the testrun with name "Running Man"
        
        

        
