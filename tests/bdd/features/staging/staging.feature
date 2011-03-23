Feature: Staging area for Tests
    in order to do a small test
    as a test developer
    I need to test one scenario at a time

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



