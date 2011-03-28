Feature: Test Cycles

    Scenario: Get summary results of a testcycle
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
        Then the testcycle with name "Baroque Cycle" has the following result status summary counts:
            | name        | count |
            | Passed      | 2     |
            | Failed      | 1     |
            | Invalidated | 1     |

    Scenario: Approve all test results of a testcycle (Bug 644306)
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
        And I approve all the results for that testcycle
        Then the results for that testrun have the following approval statuses:
            | name               | status   |
            | Passing tc         | Approved |
            | Another Passing tc | Approved |
            | Failing tc         | Approved |
            | Skipper tc         | Approved |
            | Invalidisimo       | Approved |

    Scenario: Get environmentgroups  of a testcycle
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
        And I add the following environmentgroups to the testcycle with name "Baroque Cycle":
            | name    |
            | EnvGrp1 |
            | EnvGrp2 |
            | EnvGrp3 |
            | EnvGrp4 |
        Then the testcycle with name "Baroque Cycle" has the following environmentgroups:
            | name    |
            | EnvGrp1 |
            | EnvGrp2 |
            | EnvGrp3 |
            | EnvGrp4 |

    Scenario: Add team member to testcycle
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
        Then the testcycle with name "Baroque Cycle" has the following team members:
            | name         |
            | Joe Tester |

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

    Scenario: Add team member to testrun, it's NOT reflected in the testcycle
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
        And I add the following users to the testrun with name "Running Man":
            | name       |
            | Joe Tester |
        Then the testcycle with name "Baroque Cycle" has no team members

    Scenario: Ensure environmentgroups set on Testcycle don't modify parent Product environmentgroups
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
        And the testcycle with name "Baroque Cycle" has the following environmentgroups:
            | name    |
            | EnvGrp1 |
            | EnvGrp2 |
        And when I add the following environmentgroups to the testcycle with name "Baroque Cycle":
            | name    |
            | EnvGrp1 |
        Then the testcycle with name "Baroque Cycle" has the following environmentgroups:
            | name    |
            | EnvGrp1 |
        And the product with name "Cortexiphan" has the following environmentgroups:
            | name    |
            | EnvGrp1 |
            | EnvGrp2 |

