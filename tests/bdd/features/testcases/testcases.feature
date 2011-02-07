Feature: Test Cases

    Scenario: Create and delete a Testcase
        Given a testcase with name "Come on fhqwhgads" does not exist
        when I create a new testcase with that name
        then a testcase with that name exists
        and when I delete the testcase with that name
        then a testcase with that name does not exist
        
    Scenario: Create a Testcase with steps
        Given a testcase with name "Come on fhqwhgads" does not exist
        when I create a new testcase with that name
        then a testcase with that name exists
        and when I add steps to that testcase with these values:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
            | Flockery  | 2          | 2                  | Go that way    | They went that way    |
            | Chockery  | 3          | 4                  | Go my way      | They went my way      |
            | Trockery  | 4          | 1                  | Go the highway | They went the highway |
            | Blockery  | 5          | 25                 | Just go away   | They went away        |
        then that testcase has steps with these values:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
            | Flockery  | 2          | 2                  | Go that way    | They went that way    |
            | Chockery  | 3          | 4                  | Go my way      | They went my way      |
            | Trockery  | 4          | 1                  | Go the highway | They went the highway |
            | Blockery  | 5          | 25                 | Just go away   | They went away        |
        

        
