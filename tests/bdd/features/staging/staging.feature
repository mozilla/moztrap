Feature: Staging area for Tests
    in order to do a small test
    as a test developer
    I need to test one scenario at a time

    Scenario: create a company
        create the following new companies:
            | name    | phone        | address | city   | zip     | url     | country name   |
            | smell   | fff-432-4321 | fefefe  | fefefe | d3333   | nun     | United States  |
        create the following new products:
            | name    | description   | company name    | 
            | flipper   | fff-432-4321 | smell  | 

    Scenario: Test the thing
        Given I create the seed company and product
        and I create a new user with name "Flipper snot"

