Feature: Test Cases

    Scenario: Create and approve a Testcase with steps
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        When I create a new user with name "Capn Admin"
        and I activate the user with that name
        And I create a new role with name "Approvationalist" with the following permissions:
            | permissionCode               |
            | PERMISSION_TEST_CASE_EDIT    |
            | PERMISSION_TEST_CASE_APPROVE |
        Then the role with that name has the following permissions:
            | permissionCode               |
            | PERMISSION_TEST_CASE_APPROVE |
            | PERMISSION_TEST_CASE_EDIT    |
        And I add the role with name "Approvationalist" to the user with that name
        Then the user with that name has the role with that name
        And a testcase with name "Come on fhqwhgads" does not exist
        when the user with that name creates a new testcase with that name
        then a testcase with that name exists
        and when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
            | Flockery  | 2          | 2                  | Go that way    | They went that way    |
            | Chockery  | 3          | 4                  | Go my way      | They went my way      |
            | Trockery  | 4          | 1                  | Go the highway | They went the highway |
            | Blockery  | 5          | 25                 | Just go away   | They went away        |
        then the testcase with that name has these steps:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
            | Flockery  | 2          | 2                  | Go that way    | They went that way    |
            | Chockery  | 3          | 4                  | Go my way      | They went my way      |
            | Trockery  | 4          | 1                  | Go the highway | They went the highway |
            | Blockery  | 5          | 25                 | Just go away   | They went away        |
        Then when I create a new user with name "Joe Approver"
        and I activate the user with that name
        And I add the role with name "Approvationalist" to the user with that name
        and when the user with name "Joe Approver" approves the testcase with that name
        then the testcase with that name has approval status of Active

    Scenario: add a testcase to a testrun

    Scenario: Create a Testcycle and Testrun and verify the testrun is in the testcycle
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
        and the testcycle with name "Baroque Cycle" has the testrun with name "Running Man"


    Scenario: Add a testsuite to a testrun
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        And I create a new user with name "Capn Admin"
        And I activate the user with that name
        And I create a new role with name "Approvationalist" with the following permissions:
            | permissionCode               |
            | PERMISSION_TEST_CASE_EDIT    |
            | PERMISSION_TEST_CASE_APPROVE |
            | PERMISSION_TEST_RUN_ASSIGNMENT_EXECUTE |
        And I add the role with name "Approvationalist" to the user with that name
        When the user with that name creates a new testcase with name "Check the Gizmo"
        And when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
            | Flockery  | 2          | 2                  | Go that way    | They went that way    |
            | Chockery  | 3          | 4                  | Go my way      | They went my way      |
            | Trockery  | 4          | 1                  | Go the highway | They went the highway |
            | Blockery  | 5          | 25                 | Just go away   | They went away        |
        Then when I create a new user with name "Joe Tester"
        And I activate the user with that name
        And I add the role with name "Approvationalist" to the user with that name
        And when the user with name "Joe Tester" approves the testcase with that name
        And I activate the testcase with that name
        And I create the following new testsuites:
            | name          | description               | product name | useLatestVersions |
            | Sweet Suite   | Ahh, the cycle of life... | Cortexiphan  | true              |
        And I add the following testcases to the testsuite with name "Sweet Suite":
            | name            |
            | Check the Gizmo |
        And I activate the testsuite with name "Sweet Suite"
        And when I create the following new testcycles:
            | name          | description               | product name | startDate  | endDate    | communityAuthoringAllowed | communityAccessAllowed |
            | Baroque Cycle | Ahh, the cycle of life... | Cortexiphan  | 2011/02/02 | 2012/02/02 | true                      | true                   |
        And when I create a new testrun with name "Running Man" with testcycle "Baroque Cycle"
        And when I add the following testsuites to the testrun with that name
            | name        |
            | Sweet Suite |
        Then that testrun has the following testsuites
            | name        |
            | Sweet Suite |
        And that testrun has the following included testcases
            | name            |
            | Check the Gizmo |


