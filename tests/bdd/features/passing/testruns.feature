Feature: Test Runs

    Scenario: Verify results of a testrun
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        When I create a new user with name "Capn Admin"
        And I activate the user with that name
        And I create a new role with name "Approvationalist" with the following permissions:
            | permissionCode               |
            | PERMISSION_TEST_CASE_EDIT    |
            | PERMISSION_TEST_CASE_APPROVE |
            | PERMISSION_TEST_RUN_ASSIGNMENT_EXECUTE |
        And I add the role with name "Approvationalist" to the user with that name
        When the user with that name creates a new testcase with name "Passing tc"
        And when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
        When the user with that name creates a new testcase with name "Another Passing tc"
        And when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
        When the user with that name creates a new testcase with name "Failing tc"
        And when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
        When the user with that name creates a new testcase with name "Skipper"
        And when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
        When the user with that name creates a new testcase with name "Invalidisimo"
        And when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
        Then when I create a new user with name "Joe Tester"
        And I activate the user with that name
        And I add the role with name "Approvationalist" to the user with that name
        And when the user with name "Joe Tester" approves the following testcases:
            | name               |
            | Passing tc         |
            | Another Passing tc |
            | Failing tc         |
            | Skipper            |
            | Invalidisimo       |
        And I activate the following testcases
            | name               |
            | Passing tc         |
            | Another Passing tc |
            | Failing tc         |
            | Skipper            |
            | Invalidisimo       |
        And I create the following new testsuites:
            | name          | description               | product name | useLatestVersions |
            | Sweet Suite   | Ahh, the cycle of life... | Cortexiphan  | true              |
        And I add the following testcases to the testsuite with name "Sweet Suite":
            | name               |
            | Passing tc         |
            | Another Passing tc |
            | Failing tc         |
            | Skipper            |
            | Invalidisimo       |
        And I activate the testsuite with name "Sweet Suite"
        And when I create the following new testcycles:
            | name          | description               | product name | startDate  | endDate    | communityAuthoringAllowed | communityAccessAllowed |
            | Baroque Cycle | Ahh, the cycle of life... | Cortexiphan  | 2011/02/02 | 2012/02/02 | true                      | true                   |
        And when I create a new testrun with name "Running Man" with testcycle "Baroque Cycle"
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
        And I add the following environmentgroups to the testrun with that name:
            | name    |
            | EnvGrp1 |
        And when I add the following testsuites to the testrun with that name
            | name    |
            | Sweet Suite  |
        And I activate the testcycle with name "Baroque Cycle"
        And I activate the testrun with that name
        And I assign the following testcases to the user with name "Joe Tester" for the testrun with name "Running Man"
            | name               |
            | Passing tc         |
            | Another Passing tc |
            | Failing tc         |
            | Skipper            |
            | Invalidisimo       |
        And the user with that name marks the following testcase result statuses for the testrun with that name
            | name               | status      |
            | Passing tc         | Passed      |
            | Another Passing tc | Passed      |
            | Failing tc         | Failed      |
            | Skipper            | Skipped     |
            | Invalidisimo       | Invalidated |
        Then that testrun has the following result status summary counts:
            | name        | count |
            | Passed      | 2     |
            | Failed      | 1     |
            | Skipped     | 1     |
            | Invalidated | 1     |
        Then the following testcases have the following result statuses for that testrun
            | name               | status      |
            | Passing tc         | Passed      |
            | Another Passing tc | Passed      |
            | Failing tc         | Failed      |
            | Skipper            | Skipped     |
            | Invalidisimo       | Invalidated |

    Scenario: Fetch a testrun result by its ID
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        When I create a new user with name "Capn Admin"
        And I activate the user with that name
        And I create a new role with name "Approvationalist" with the following permissions:
            | permissionCode               |
            | PERMISSION_TEST_CASE_EDIT    |
            | PERMISSION_TEST_CASE_APPROVE |
            | PERMISSION_TEST_RUN_ASSIGNMENT_EXECUTE |
        And I add the role with name "Approvationalist" to the user with that name
        When the user with that name creates a new testcase with name "Passing tc"
        And when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
        Then when I create a new user with name "Joe Tester"
        And I activate the user with that name
        And I add the role with name "Approvationalist" to the user with that name
        And when the user with name "Joe Tester" approves the following testcases:
            | name               |
            | Passing tc         |
        And I activate the following testcases
            | name               |
            | Passing tc         |
        And I create the following new testsuites:
            | name          | description               | product name | useLatestVersions |
            | Sweet Suite   | Ahh, the cycle of life... | Cortexiphan  | true              |
        And I add the following testcases to the testsuite with name "Sweet Suite":
            | name               |
            | Passing tc         |
        And I activate the testsuite with name "Sweet Suite"
        And when I create the following new testcycles:
            | name          | description               | product name | startDate  | endDate    | communityAuthoringAllowed | communityAccessAllowed |
            | Baroque Cycle | Ahh, the cycle of life... | Cortexiphan  | 2011/02/02 | 2012/02/02 | true                      | true                   |
        And when I create a new testrun with name "Running Man" with testcycle "Baroque Cycle"
        And I create a new environmenttype with name "EnvType1"
        And I create a new environment with name "Env1" of type "EnvType1"
        And I create a new group environmenttype with name "GrpEnvType1"
        And I create a new environmentgroup with name "EnvGrp1" of type "GrpEnvType1"
        And I add the following environments to the environmentgroup with that name:
            | name |
            | Env1 |
        And I add the following users to the testrun with that name:
            | name       |
            | Joe Tester |
        And I add the following environmentgroups to the testrun with that name:
            | name    |
            | EnvGrp1 |
        And when I add the following testsuites to the testrun with that name
            | name         |
            | Sweet Suite  |
        And I activate the testcycle with name "Baroque Cycle"
        And I activate the testrun with that name
        And I assign the following testcases to the user with name "Joe Tester" for the testrun with name "Running Man"
            | name               |
            | Passing tc         |
        Then I can fetch the following testcase results for that testrun by their ids
            | name               |
            | Passing tc         |

    Scenario: Mark a test result Approved
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        When I create a new user with name "Capn Admin"
        And I activate the user with that name
        And I create a new role with name "Approvationalist" with the following permissions:
            | permissionCode               |
            | PERMISSION_TEST_CASE_EDIT    |
            | PERMISSION_TEST_CASE_APPROVE |
            | PERMISSION_TEST_RUN_ASSIGNMENT_EXECUTE |
        And I add the role with name "Approvationalist" to the user with that name
        When the user with that name creates a new testcase with name "Passing tc"
        And when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
        Then when I create a new user with name "Joe Tester"
        And I activate the user with that name
        And I add the role with name "Approvationalist" to the user with that name
        And when the user with name "Joe Tester" approves the following testcases:
            | name               |
            | Passing tc         |
        And I activate the following testcases
            | name               |
            | Passing tc         |
        And I create the following new testsuites:
            | name          | description               | product name | useLatestVersions |
            | Sweet Suite   | Ahh, the cycle of life... | Cortexiphan  | true              |
        And I add the following testcases to the testsuite with name "Sweet Suite":
            | name               |
            | Passing tc         |
        And I activate the testsuite with name "Sweet Suite"
        And when I create the following new testcycles:
            | name          | description               | product name | startDate  | endDate    | communityAuthoringAllowed | communityAccessAllowed |
            | Baroque Cycle | Ahh, the cycle of life... | Cortexiphan  | 2011/02/02 | 2012/02/02 | true                      | true                   |
        And when I create a new testrun with name "Running Man" with testcycle "Baroque Cycle"
        And I create a new environmenttype with name "EnvType1"
        And I create a new environment with name "Env1" of type "EnvType1"
        And I create a new group environmenttype with name "GrpEnvType1"
        And I create a new environmentgroup with name "EnvGrp1" of type "GrpEnvType1"
        And I add the following environments to the environmentgroup with that name:
            | name |
            | Env1 |
        And I add the following users to the testrun with that name:
            | name       |
            | Joe Tester |
        And I add the following environmentgroups to the testrun with that name:
            | name    |
            | EnvGrp1 |
        And when I add the following testsuites to the testrun with that name
            | name         |
            | Sweet Suite  |
        And I activate the testcycle with name "Baroque Cycle"
        And I activate the testrun with that name
        And I assign the following testcases to the user with name "Joe Tester" for the testrun with name "Running Man"
            | name               |
            | Passing tc         |
        And the user with that name marks the following testcase result statuses for the testrun with that name
            | name               | status      |
            | Passing tc         | Passed      |
        And I approve the following testcase results for that testrun
            | name               |
            | Passing tc         |
        Then the results for that testrun have the following approval statuses:
            | name               | status   |
            | Passing tc         | Approved |


    Scenario: Approve all test results of a testrun (Bug 644306)
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        When I create a new user with name "Capn Admin"
        And I activate the user with that name
        And I create a new role with name "Approvationalist" with the following permissions:
            | permissionCode               |
            | PERMISSION_TEST_CASE_EDIT    |
            | PERMISSION_TEST_CASE_APPROVE |
            | PERMISSION_TEST_RUN_ASSIGNMENT_EXECUTE |
        And I add the role with name "Approvationalist" to the user with that name
        When the user with that name creates a new testcase with name "Passing tc"
        And when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
        When the user with that name creates a new testcase with name "Another Passing tc"
        And when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
        When the user with that name creates a new testcase with name "Failing tc"
        And when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
        When the user with that name creates a new testcase with name "Skipper tc"
        And when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
        When the user with that name creates a new testcase with name "Invalidisimo"
        And when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
        Then when I create a new user with name "Joe Tester"
        And I activate the user with that name
        And I add the role with name "Approvationalist" to the user with that name
        And when the user with name "Joe Tester" approves the following testcases:
            | name               |
            | Passing tc         |
            | Another Passing tc |
            | Failing tc         |
            | Skipper tc         |
            | Invalidisimo       |
        And I activate the following testcases
            | name               |
            | Passing tc         |
            | Another Passing tc |
            | Failing tc         |
            | Skipper tc         |
            | Invalidisimo       |
        And I create the following new testsuites:
            | name          | description               | product name | useLatestVersions |
            | Sweet Suite   | Ahh, the cycle of life... | Cortexiphan  | true              |
        And I add the following testcases to the testsuite with name "Sweet Suite":
            | name               |
            | Passing tc         |
            | Another Passing tc |
            | Failing tc         |
            | Skipper tc         |
            | Invalidisimo       |
        And I activate the testsuite with name "Sweet Suite"
        And when I create the following new testcycles:
            | name          | description               | product name | startDate  | endDate    | communityAuthoringAllowed | communityAccessAllowed |
            | Baroque Cycle | Ahh, the cycle of life... | Cortexiphan  | 2011/02/02 | 2012/02/02 | true                      | true                   |
        And when I create a new testrun with name "Running Man" with testcycle "Baroque Cycle"
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
        And I add the following environmentgroups to the testrun with that name:
            | name    |
            | EnvGrp1 |
        And when I add the following testsuites to the testrun with that name
            | name    |
            | Sweet Suite  |
        And I activate the testcycle with name "Baroque Cycle"
        And I activate the testrun with that name
        And I assign the following testcases to the user with name "Joe Tester" for the testrun with name "Running Man"
            | name               |
            | Passing tc         |
            | Another Passing tc |
            | Failing tc         |
            | Skipper tc         |
            | Invalidisimo       |
        And the user with that name marks the following testcase result statuses for the testrun with that name
            | name               | status      |
            | Passing tc         | Passed      |
            | Another Passing tc | Passed      |
            | Failing tc         | Failed      |
            | Skipper tc         | Skipped     |
            | Invalidisimo       | Invalidated |
        And I approve all the results for that testrun
        Then the results for that testrun have the following approval statuses:
            | name               | status   |
            | Passing tc         | Approved |
            | Another Passing tc | Approved |
            | Failing tc         | Approved |
            | Skipper tc         | Approved |
            | Invalidisimo       | Approved |

    Scenario: Get environmentgroups of a testrun
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        When I create the following new testcycles:
            | name          | description               | product name | startDate  | endDate    | communityAuthoringAllowed | communityAccessAllowed |
            | Baroque Cycle | Ahh, the cycle of life... | Cortexiphan  | 2011/02/02 | 2012/02/02 | true                      | true                   |
        And when I create a new testrun with name "Running Man" with testcycle "Baroque Cycle"
        And I create a new environmenttype with name "EnvType1"
        And I create a new environment with name "Env1" of type "EnvType1"
        And I create a new group environmenttype with name "GrpEnvType1"
        And I create the following new environmentgroups
            | name     | description  | environmenttype name |
            | EnvGrp1 | group1       | GrpEnvType1          |
            | EnvGrp2 | group2       | GrpEnvType1          |
            | EnvGrp3 | group3       | GrpEnvType1          |
            | EnvGrp4 | group4       | GrpEnvType1          |
        And I add the following environmentgroups to the testrun with name "Running Man":
            | name    |
            | EnvGrp1 |
            | EnvGrp2 |
            | EnvGrp3 |
            | EnvGrp4 |
        Then the testrun with name "Running Man" has the following environmentgroups:
            | name    |
            | EnvGrp1 |
            | EnvGrp2 |
            | EnvGrp3 |
            | EnvGrp4 |

    Scenario: Ensure environmentgroups added to testrun are not added to parent testcycle
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        When I create the following new testcycles:
            | name          | description               | product name | startDate  | endDate    | communityAuthoringAllowed | communityAccessAllowed |
            | Baroque Cycle | Ahh, the cycle of life... | Cortexiphan  | 2011/02/02 | 2012/02/02 | true                      | true                   |
        And when I create a new testrun with name "Running Man" with testcycle "Baroque Cycle"
        And I create a new environmenttype with name "EnvType1"
        And I create a new environment with name "Env1" of type "EnvType1"
        And I create a new group environmenttype with name "GrpEnvType1"
        And I create the following new environmentgroups
            | name     | description  | environmenttype name |
            | EnvGrp1 | group1       | GrpEnvType1          |
            | EnvGrp2 | group2       | GrpEnvType1          |
            | EnvGrp3 | group3       | GrpEnvType1          |
            | EnvGrp4 | group4       | GrpEnvType1          |
        And I add the following environmentgroups to the testrun with name "Running Man":
            | name    |
            | EnvGrp1 |
            | EnvGrp2 |
            | EnvGrp3 |
            | EnvGrp4 |
        Then the testrun with name "Running Man" has the following environmentgroups:
            | name    |
            | EnvGrp1 |
            | EnvGrp2 |
            | EnvGrp3 |
            | EnvGrp4 |
        Then the testcycle with name "Baroque Cycle" has no environmentgroups


    Scenario: Add team members to a Testrun
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        When I create a new user with name "Capn Admin"
        And I activate the user with that name
        And I create a new role with name "Approvationalist" with the following permissions:
            | permissionCode               |
            | PERMISSION_TEST_CASE_EDIT    |
            | PERMISSION_TEST_CASE_APPROVE |
            | PERMISSION_TEST_RUN_ASSIGNMENT_EXECUTE |
        And I add the role with name "Approvationalist" to the user with that name
        When the user with that name creates a new testcase with name "Passing tc"
        And when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
        Then when I create a new user with name "Joe Tester"
        And I activate the user with that name
        And I add the role with name "Approvationalist" to the user with that name
        And when I create the following new testcycles:
            | name          | description               | product name | startDate  | endDate    | communityAuthoringAllowed | communityAccessAllowed |
            | Baroque Cycle | Ahh, the cycle of life... | Cortexiphan  | 2011/02/02 | 2012/02/02 | true                      | true                   |
        And when I create a new testrun with name "Running Man" with testcycle "Baroque Cycle"
        And I add the following users to the testrun with that name:
            | name         |
            | Joe Tester |
        Then the testrun with name "Running Man" has the following team members:
            | name         |
            | Joe Tester |

    Scenario: Add a testsuite to a testrun without an environment set (bug 641129)
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
        And when I add the following testsuites to the testrun with that name
            | name         |
            | Sweet Suite  |
        And I activate the testcycle with name "Baroque Cycle"
        And I activate the testrun with that name

    Scenario: Add team member to testcycle, it's reflected in the child testrun
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        When I create a new user with name "Capn Admin"
        And I activate the user with that name
        And I create a new role with name "Approvationalist" with the following permissions:
            | permissionCode               |
            | PERMISSION_TEST_CASE_EDIT    |
            | PERMISSION_TEST_CASE_APPROVE |
            | PERMISSION_TEST_RUN_ASSIGNMENT_EXECUTE |
        And I add the role with name "Approvationalist" to the user with that name
        When the user with that name creates a new testcase with name "Passing tc"
        And when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
        Then when I create a new user with name "Joe Tester"
        And I activate the user with that name
        And I add the role with name "Approvationalist" to the user with that name
        And when I create the following new testcycles:
            | name          | description               | product name | startDate  | endDate    | communityAuthoringAllowed | communityAccessAllowed |
            | Baroque Cycle | Ahh, the cycle of life... | Cortexiphan  | 2011/02/02 | 2012/02/02 | true                      | true                   |
        And I add the following users to the testcycle with name "Baroque Cycle":
            | name       |
            | Joe Tester |
        And when I create a new testrun with name "Running Man" with testcycle "Baroque Cycle"
        Then the testrun with name "Running Man" has the following team members:
            | name       |
            | Joe Tester |

    Scenario: Add team member to testcycle after testrun is created.  Team member not in testrun
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        When I create a new user with name "Capn Admin"
        And I activate the user with that name
        And I create a new role with name "Approvationalist" with the following permissions:
            | permissionCode               |
            | PERMISSION_TEST_CASE_EDIT    |
            | PERMISSION_TEST_CASE_APPROVE |
            | PERMISSION_TEST_RUN_ASSIGNMENT_EXECUTE |
        And I add the role with name "Approvationalist" to the user with that name
        When the user with that name creates a new testcase with name "Passing tc"
        And when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
        Then when I create a new user with name "Joe Tester"
        And I activate the user with that name
        And I add the role with name "Approvationalist" to the user with that name
        And when I create the following new testcycles:
            | name          | description               | product name | startDate  | endDate    | communityAuthoringAllowed | communityAccessAllowed |
            | Baroque Cycle | Ahh, the cycle of life... | Cortexiphan  | 2011/02/02 | 2012/02/02 | true                      | true                   |
        And when I create a new testrun with name "Running Man" with testcycle "Baroque Cycle"
        And I add the following users to the testcycle with name "Baroque Cycle":
            | name       |
            | Joe Tester |
        Then the testrun with name "Running Man" has the following team members:

Scenario: Testrun results have environment after being run
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        When I create a new user with name "Capn Admin"
        And I activate the user with that name
        And I create a new role with name "Approvationalist" with the following permissions:
            | permissionCode               |
            | PERMISSION_TEST_CASE_EDIT    |
            | PERMISSION_TEST_CASE_APPROVE |
            | PERMISSION_TEST_RUN_ASSIGNMENT_EXECUTE |
        And I add the role with name "Approvationalist" to the user with that name
        When the user with that name creates a new testcase with name "Passing tc"
        And when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
        When the user with that name creates a new testcase with name "Another Passing tc"
        And when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
        When the user with that name creates a new testcase with name "Failing tc"
        And when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
        When the user with that name creates a new testcase with name "Skipper"
        And when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
        When the user with that name creates a new testcase with name "Invalidisimo"
        And when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
        Then when I create a new user with name "Joe Tester"
        And I activate the user with that name
        And I add the role with name "Approvationalist" to the user with that name
        And when the user with name "Joe Tester" approves the following testcases:
            | name               |
            | Passing tc         |
            | Another Passing tc |
            | Failing tc         |
            | Skipper            |
            | Invalidisimo       |
        And I activate the following testcases
            | name               |
            | Passing tc         |
            | Another Passing tc |
            | Failing tc         |
            | Skipper            |
            | Invalidisimo       |
        And I create the following new testsuites:
            | name          | description               | product name | useLatestVersions |
            | Sweet Suite   | Ahh, the cycle of life... | Cortexiphan  | true              |
        And I add the following testcases to the testsuite with name "Sweet Suite":
            | name               |
            | Passing tc         |
            | Another Passing tc |
            | Failing tc         |
            | Skipper            |
            | Invalidisimo       |
        And I activate the testsuite with name "Sweet Suite"
        And when I create the following new testcycles:
            | name          | description               | product name | startDate  | endDate    | communityAuthoringAllowed | communityAccessAllowed |
            | Baroque Cycle | Ahh, the cycle of life... | Cortexiphan  | 2011/02/02 | 2012/02/02 | true                      | true                   |
        And when I create a new testrun with name "Running Man" with testcycle "Baroque Cycle"
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
        And I add the following environmentgroups to the testrun with that name:
            | name    |
            | EnvGrp1 |
        And when I add the following testsuites to the testrun with that name
            | name    |
            | Sweet Suite  |
        And I activate the testcycle with name "Baroque Cycle"
        And I activate the testrun with that name
        And I assign the following testcases to the user with name "Joe Tester" for the testrun with name "Running Man"
            | name               |
            | Passing tc         |
            | Another Passing tc |
            | Failing tc         |
            | Skipper            |
            | Invalidisimo       |
        And the user with that name marks the following testcase result statuses for the testrun with that name
            | name               | status      |
            | Passing tc         | Passed      |
            | Another Passing tc | Passed      |
            | Failing tc         | Failed      |
            | Skipper            | Skipped     |
            | Invalidisimo       | Invalidated |
        Then the following testcases have the following environments for that testrun
            | name               | environment |
            | Passing tc         | Env1        |

    Scenario: Ensure environmentgroups set on Testrun don't modify parent Testcycle environmentgroups
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        And I create a new environmenttype with name "EnvType1"
        And I create a new environment with name "Env1" of type "EnvType1"
        And I create a new group environmenttype with name "GrpEnvType1"
        And I create the following new environmentgroups
            | name     | description  | environmenttype name |
            | EnvGrp1 | group1       | GrpEnvType1          |
            | EnvGrp2 | group2       | GrpEnvType1          |
        And I add the following environmentgroups to the product with name "Cortexiphan":
            | name    |
            | EnvGrp1 |
            | EnvGrp2 |
        Then the product with name "Cortexiphan" has the following environmentgroups:
            | name    |
            | EnvGrp1 |
            | EnvGrp2 |
        When I create the following new testcycles:
            | name          | description               | product name | startDate  | endDate    | communityAuthoringAllowed | communityAccessAllowed |
            | Baroque Cycle | Ahh, the cycle of life... | Cortexiphan  | 2011/02/02 | 2012/02/02 | true                      | true                   |
        And when I create a new testrun with name "Running Man" with testcycle "Baroque Cycle"
        And the testrun with name "Running Man" has the following environmentgroups:
            | name    |
            | EnvGrp1 |
            | EnvGrp2 |
        And when I add the following environmentgroups to the testrun with name "Running Man":
            | name    |
            | EnvGrp1 |
        Then that testrun has the following environmentgroups:
            | name    |
            | EnvGrp1 |
        And the testcycle with name "Baroque Cycle" has the following environmentgroups:
            | name    |
            | EnvGrp1 |
            | EnvGrp2 |
        And the product with name "Cortexiphan" has the following environmentgroups:
            | name    |
            | EnvGrp1 |
            | EnvGrp2 |

    Scenario: Retest one passing result after it was run once, specifying tester
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        When I create a new user with name "Capn Admin"
        And I activate the user with that name
        And I create a new role with name "Approvationalist" with the following permissions:
            | permissionCode               |
            | PERMISSION_TEST_CASE_EDIT    |
            | PERMISSION_TEST_CASE_APPROVE |
            | PERMISSION_TEST_RUN_ASSIGNMENT_EXECUTE |
        And I add the role with name "Approvationalist" to the user with that name
        When the user with that name creates a new testcase with name "Passing tc"
        And when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
        When the user with that name creates a new testcase with name "Another Passing tc"
        And when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
        When the user with that name creates a new testcase with name "Failing tc"
        And when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
        When the user with that name creates a new testcase with name "Invalidisimo"
        And when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
        Then when I create a new user with name "Joe Tester"
        And I activate the user with that name
        And I add the role with name "Approvationalist" to the user with that name
        And when the user with name "Joe Tester" approves the following testcases:
            | name               |
            | Passing tc         |
            | Another Passing tc |
            | Failing tc         |
            | Invalidisimo       |
        And I activate the following testcases
            | name               |
            | Passing tc         |
            | Another Passing tc |
            | Failing tc         |
            | Invalidisimo       |
        And I create the following new testsuites:
            | name          | description               | product name | useLatestVersions |
            | Sweet Suite   | Ahh, the cycle of life... | Cortexiphan  | true              |
        And I add the following testcases to the testsuite with name "Sweet Suite":
            | name               |
            | Passing tc         |
            | Another Passing tc |
            | Failing tc         |
            | Invalidisimo       |
        And I activate the testsuite with name "Sweet Suite"
        And when I create the following new testcycles:
            | name          | description               | product name | startDate  | endDate    | communityAuthoringAllowed | communityAccessAllowed |
            | Baroque Cycle | Ahh, the cycle of life... | Cortexiphan  | 2011/02/02 | 2012/02/02 | true                      | true                   |
        And when I create a new testrun with name "Running Man" with testcycle "Baroque Cycle"
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
        And I add the following environmentgroups to the testrun with that name:
            | name    |
            | EnvGrp1 |
        And when I add the following testsuites to the testrun with that name
            | name    |
            | Sweet Suite  |
        And I activate the testcycle with name "Baroque Cycle"
        And I activate the testrun with that name
        And I assign the following testcases to the user with name "Joe Tester" for the testrun with name "Running Man"
            | name               |
            | Passing tc         |
            | Another Passing tc |
            | Failing tc         |
            | Invalidisimo       |
        And the user with that name marks the following testcase result statuses for the testrun with that name
            | name               | status      |
            | Passing tc         | Passed      |
            | Another Passing tc | Passed      |
            | Failing tc         | Failed      |
            | Invalidisimo       | Invalidated |
        When I call retest on the following testcases for that testrun:
            | name               | user name   |
            | Passing tc         | Joe Tester  |
        Then the following testcases have pending result statuses for that testrun
            | name               |
            | Passing tc         |

    Scenario: Retest one passing result after it was run once, don't specify tester
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        When I create a new user with name "Capn Admin"
        And I activate the user with that name
        And I create a new role with name "Approvationalist" with the following permissions:
            | permissionCode               |
            | PERMISSION_TEST_CASE_EDIT    |
            | PERMISSION_TEST_CASE_APPROVE |
            | PERMISSION_TEST_RUN_ASSIGNMENT_EXECUTE |
        And I add the role with name "Approvationalist" to the user with that name
        When the user with that name creates a new testcase with name "Passing tc"
        And when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
        When the user with that name creates a new testcase with name "Another Passing tc"
        And when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
        When the user with that name creates a new testcase with name "Failing tc"
        And when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
        When the user with that name creates a new testcase with name "Invalidisimo"
        And when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
        Then when I create a new user with name "Joe Tester"
        And I activate the user with that name
        And I add the role with name "Approvationalist" to the user with that name
        And when the user with name "Joe Tester" approves the following testcases:
            | name               |
            | Passing tc         |
            | Another Passing tc |
            | Failing tc         |
            | Invalidisimo       |
        And I activate the following testcases
            | name               |
            | Passing tc         |
            | Another Passing tc |
            | Failing tc         |
            | Invalidisimo       |
        And I create the following new testsuites:
            | name          | description               | product name | useLatestVersions |
            | Sweet Suite   | Ahh, the cycle of life... | Cortexiphan  | true              |
        And I add the following testcases to the testsuite with name "Sweet Suite":
            | name               |
            | Passing tc         |
            | Another Passing tc |
            | Failing tc         |
            | Invalidisimo       |
        And I activate the testsuite with name "Sweet Suite"
        And when I create the following new testcycles:
            | name          | description               | product name | startDate  | endDate    | communityAuthoringAllowed | communityAccessAllowed |
            | Baroque Cycle | Ahh, the cycle of life... | Cortexiphan  | 2011/02/02 | 2012/02/02 | true                      | true                   |
        And when I create a new testrun with name "Running Man" with testcycle "Baroque Cycle"
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
        And I add the following environmentgroups to the testrun with that name:
            | name    |
            | EnvGrp1 |
        And when I add the following testsuites to the testrun with that name
            | name    |
            | Sweet Suite  |
        And I activate the testcycle with name "Baroque Cycle"
        And I activate the testrun with that name
        And I assign the following testcases to the user with name "Joe Tester" for the testrun with name "Running Man"
            | name               |
            | Passing tc         |
            | Another Passing tc |
            | Failing tc         |
            | Invalidisimo       |
        And the user with that name marks the following testcase result statuses for the testrun with that name
            | name               | status      |
            | Passing tc         | Passed      |
            | Another Passing tc | Passed      |
            | Failing tc         | Failed      |
            | Invalidisimo       | Invalidated |
        When I call retest on the following testcases for that testrun:
            | name               |
            | Passing tc         |
        Then the following testcases have pending result statuses for that testrun
            | name               |
            | Passing tc         |

    Scenario: Retest a testrun, after it was run once - retest all cases - don't retest Invalid cases
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        When I create a new user with name "Capn Admin"
        And I activate the user with that name
        And I create a new role with name "Approvationalist" with the following permissions:
            | permissionCode               |
            | PERMISSION_TEST_CASE_EDIT    |
            | PERMISSION_TEST_CASE_APPROVE |
            | PERMISSION_TEST_RUN_ASSIGNMENT_EXECUTE |
        And I add the role with name "Approvationalist" to the user with that name
        When the user with that name creates a new testcase with name "Passing tc"
        And when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
        When the user with that name creates a new testcase with name "Another Passing tc"
        And when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
        When the user with that name creates a new testcase with name "Failing tc"
        And when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
        When the user with that name creates a new testcase with name "Invalidisimo"
        And when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
        Then when I create a new user with name "Joe Tester"
        And I activate the user with that name
        And I add the role with name "Approvationalist" to the user with that name
        And when the user with name "Joe Tester" approves the following testcases:
            | name               |
            | Passing tc         |
            | Another Passing tc |
            | Failing tc         |
            | Invalidisimo       |
        And I activate the following testcases
            | name               |
            | Passing tc         |
            | Another Passing tc |
            | Failing tc         |
            | Invalidisimo       |
        And I create the following new testsuites:
            | name          | description               | product name | useLatestVersions |
            | Sweet Suite   | Ahh, the cycle of life... | Cortexiphan  | true              |
        And I add the following testcases to the testsuite with name "Sweet Suite":
            | name               |
            | Passing tc         |
            | Another Passing tc |
            | Failing tc         |
            | Invalidisimo       |
        And I activate the testsuite with name "Sweet Suite"
        And when I create the following new testcycles:
            | name          | description               | product name | startDate  | endDate    | communityAuthoringAllowed | communityAccessAllowed |
            | Baroque Cycle | Ahh, the cycle of life... | Cortexiphan  | 2011/02/02 | 2012/02/02 | true                      | true                   |
        And when I create a new testrun with name "Running Man" with testcycle "Baroque Cycle"
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
        And I add the following environmentgroups to the testrun with that name:
            | name    |
            | EnvGrp1 |
        And when I add the following testsuites to the testrun with that name
            | name    |
            | Sweet Suite  |
        And I activate the testcycle with name "Baroque Cycle"
        And I activate the testrun with that name
        And I assign the following testcases to the user with name "Joe Tester" for the testrun with name "Running Man"
            | name               |
            | Passing tc         |
            | Another Passing tc |
            | Failing tc         |
            | Invalidisimo       |
        And the user with that name marks the following testcase result statuses for the testrun with that name
            | name               | status      |
            | Passing tc         | Passed      |
            | Another Passing tc | Passed      |
            | Failing tc         | Failed      |
            | Invalidisimo       | Invalidated |
        When I call retest all for that testrun
        Then the following testcases have pending result statuses for that testrun
            | name               |
            | Passing tc         |
            | Another Passing tc |
            | Failing tc         |

    Scenario: Retest a testrun, after it was run once - retest only failing cases - don't retest Invalid cases
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        When I create a new user with name "Capn Admin"
        And I activate the user with that name
        And I create a new role with name "Approvationalist" with the following permissions:
            | permissionCode               |
            | PERMISSION_TEST_CASE_EDIT    |
            | PERMISSION_TEST_CASE_APPROVE |
            | PERMISSION_TEST_RUN_ASSIGNMENT_EXECUTE |
        And I add the role with name "Approvationalist" to the user with that name
        When the user with that name creates a new testcase with name "Passing tc"
        And when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
        When the user with that name creates a new testcase with name "Another Passing tc"
        And when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
        When the user with that name creates a new testcase with name "Failing tc"
        And when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
        When the user with that name creates a new testcase with name "Invalidisimo"
        And when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
        Then when I create a new user with name "Joe Tester"
        And I activate the user with that name
        And I add the role with name "Approvationalist" to the user with that name
        And when the user with name "Joe Tester" approves the following testcases:
            | name               |
            | Passing tc         |
            | Another Passing tc |
            | Failing tc         |
            | Invalidisimo       |
        And I activate the following testcases
            | name               |
            | Passing tc         |
            | Another Passing tc |
            | Failing tc         |
            | Invalidisimo       |
        And I create the following new testsuites:
            | name          | description               | product name | useLatestVersions |
            | Sweet Suite   | Ahh, the cycle of life... | Cortexiphan  | true              |
        And I add the following testcases to the testsuite with name "Sweet Suite":
            | name               |
            | Passing tc         |
            | Another Passing tc |
            | Failing tc         |
            | Invalidisimo       |
        And I activate the testsuite with name "Sweet Suite"
        And when I create the following new testcycles:
            | name          | description               | product name | startDate  | endDate    | communityAuthoringAllowed | communityAccessAllowed |
            | Baroque Cycle | Ahh, the cycle of life... | Cortexiphan  | 2011/02/02 | 2012/02/02 | true                      | true                   |
        And when I create a new testrun with name "Running Man" with testcycle "Baroque Cycle"
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
        And I add the following environmentgroups to the testrun with that name:
            | name    |
            | EnvGrp1 |
        And when I add the following testsuites to the testrun with that name
            | name    |
            | Sweet Suite  |
        And I activate the testcycle with name "Baroque Cycle"
        And I activate the testrun with that name
        And I assign the following testcases to the user with name "Joe Tester" for the testrun with name "Running Man"
            | name               |
            | Passing tc         |
            | Another Passing tc |
            | Failing tc         |
            | Invalidisimo       |
        And the user with that name marks the following testcase result statuses for the testrun with that name
            | name               | status      |
            | Passing tc         | Passed      |
            | Another Passing tc | Passed      |
            | Failing tc         | Failed      |
            | Invalidisimo       | Invalidated |
        When I call retest only failed for that testrun
        Then the following testcases have pending result statuses for that testrun
            | name               |
            | Failing tc         |
