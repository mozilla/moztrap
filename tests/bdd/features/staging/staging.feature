Feature: Staging area for Tests

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
