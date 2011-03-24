Feature: Verify results of tests

    Scenario: Create the seed testcycle, testrun and testcase, mark one test as passing and verify result
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        When I create a new user with name "Capn Admin"
        And I activate the user with that name
        And I create a new role with name "Approvationalist" with the following permissions:
            | permissionCode               |
            | PERMISSION_TEST_CASE_EDIT    |
            | PERMISSION_TEST_CASE_APPROVE |
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
        And when I create the following new testcycles:
            | name          | description               | product name | startDate  | endDate    | communityAuthoringAllowed | communityAccessAllowed |
            | Baroque Cycle | Ahh, the cycle of life... | Cortexiphan  | 2011/02/02 | 2012/02/02 | true                      | true                   |
        And when I create a new testrun with name "Running Man" with testcycle "Baroque Cycle"
        And I activate the testcycle with name "Baroque Cycle"
        And I activate the testrun with that name
        And I create a new environmenttype with name "EnvType1"
        And I create a new environment with name "Env1" of type "EnvType1"
        And I create a new group environmenttype with name "GrpEnvType1"
        And I create a new environmentgroup with name "EnvGrp1" of type "GrpEnvType1"
        And I add the following environments to the environmentgroup with that name:
            | name |
            | Env1 |
        And I add the following users to the testrun with that name:
            | name         |
            | Joe Tester |
        And when I add the following testcases to the testrun with that name
            | testcase        |
            | Check the Gizmo |
        And I add the following environmentgroups to the testrun with that name:
            | name    |
            | EnvGrp1 |
        And I the user with name "Joe Tester" sets the following testcase statuses for the testrun with that name
            | testcase        | status |
            | Check the Gizmo | pass   |
