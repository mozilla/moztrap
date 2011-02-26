Feature: Staging area for Tests
    in order to do a small test
    as a test developer
    I need to test one scenario at a time

    Scenario: Find a company by its companyId
        Given I create the seed company and product
        Then I can fetch the company with name "Massive Dynamic" by its id

