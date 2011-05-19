Feature: Environment Object Business Rules
    In order to support multiple environments
    As an Administrator
    I should support the business rules for the Environment Object

    Scenario: Environment - Creation
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        And an environment with name "Walter's Lab" does not exist
        when I create a new environmenttype with name "Brickhouse"
        when I create a new environment with that name of type "Brickhouse"
        Then an environment with that name exists

    Scenario: Environment - types
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        And I create a new group environmenttype with name "Desktop"
        and I create a new group environmenttype with name "Mobile"
        and I create a new environmenttype with name "Language"
        and I create a new environmenttype with name "OS"
        when I create a new environment with name "English" of type "Language"
        when I create a new environment with name "French" of type "Language"
        when I create a new environment with name "OS X" of type "OS"
        when I create a new environment with name "Linux Ubuntu" of type "OS"
        Then at least the following environments exist:
            | name         | type     |
            | English      | Language |
            | French       | Language |
            | OS X         | OS       |
            | Linux Ubuntu | OS       |

    Scenario: Environment Group

    Scenario: Add an environmentgroup to a testrun
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
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
        When I add the following environmentgroups to the testrun with that name:
            | name    |
            | EnvGrp1 |
        Then that testrun has the following environmentgroups:
            | name |
            | EnvGrp1 |

    Scenario: Modify a test run's environment groups twice
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
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
        And I add the following environmentgroups to the testrun with that name:
            | name    |
            | EnvGrp1 |
        When I add the following environmentgroups to the testrun with that name:
            | name    |
            | EnvGrp1 |
        Then that testrun has the following environmentgroups:
            | name |
            | EnvGrp1 |

    Scenario: Modify a test cycle's environment groups twice
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        And when I create the following new testcycles:
            | name          | description               | product name | startDate  | endDate    | communityAuthoringAllowed | communityAccessAllowed |
            | Baroque Cycle | Ahh, the cycle of life... | Cortexiphan  | 2011/02/02 | 2012/02/02 | true                      | true                   |
        And I create a new environmenttype with name "EnvType1"
        And I create a new environment with name "Env1" of type "EnvType1"
        And I create a new group environmenttype with name "GrpEnvType1"
        And I create a new environmentgroup with name "EnvGrp1" of type "GrpEnvType1"
        And I add the following environments to the environmentgroup with that name:
            | name |
            | Env1 |
        And I add the following environmentgroups to the testcycle with name "Baroque Cycle":
            | name    |
            | EnvGrp1 |
        When I add the following environmentgroups to the testcycle with that name:
            | name    |
            | EnvGrp1 |
        Then that testcycle has the following environmentgroups:
            | name |
            | EnvGrp1 |

    Scenario: Modify a product's environment groups twice
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        And I create a new environmenttype with name "EnvType1"
        And I create a new environment with name "Env1" of type "EnvType1"
        And I create a new group environmenttype with name "GrpEnvType1"
        And I create a new environmentgroup with name "EnvGrp1" of type "GrpEnvType1"
        And I add the following environments to the environmentgroup with that name:
            | name |
            | Env1 |
        And I add the following environmentgroups to the product with name "Cortexiphan":
            | name    |
            | EnvGrp1 |
        When I add the following environmentgroups to the product with that name:
            | name    |
            | EnvGrp1 |
        Then that product has the following environmentgroups:
            | name |
            | EnvGrp1 |
