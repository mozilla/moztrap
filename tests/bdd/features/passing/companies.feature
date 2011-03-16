Feature: Company Administration
    In order to support multiple companies
    As an Administrator
    I want to be able to administer company entries

    Scenario: Find a company by its companyId
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        Then I can fetch the company with name "Massive Dynamic" by its id

    Scenario: Query Companies
        Given I create the following new companies:
            | name              | phone        | address          | city   | zip     | url     | country name   |
            | Flexible Dent     | 123-432-4321 | 4432 Malta St.   | fefefe | d3333   | nun     | United States  |
            | Slashing Lace     | 234-432-4321 | 443 Chiefly Ave. | fefefe | d3333   | nun     | Afganistan     |
            | Flexible Yogurt   | 345-432-4321 | Falta Ave        | fefefe | d3333   | nun     | Italy          |
            | Devious Flexible  | 456-432-4321 | Chiefly St.      | fefefe | d3333   | nun     | France         |
            | Stopping Flexible | 567-432-4321 | Reeves Blvd      | fefefe | d3333   | nun     | Germany        |
        Then a search for all companies returns at least these results:
            | name              | phone        | address          | city   | zip     | url     | country name   |
            | Flexible Dent     | 123-432-4321 | 4432 Malta St.   | fefefe | d3333   | nun     | United States  |
            | Slashing Lace     | 234-432-4321 | 443 Chiefly Ave. | fefefe | d3333   | nun     | Afganistan     |
            | Flexible Yogurt   | 345-432-4321 | Falta Ave        | fefefe | d3333   | nun     | Italy          |
            | Devious Flexible  | 456-432-4321 | Chiefly St.      | fefefe | d3333   | nun     | France         |
            | Stopping Flexible | 567-432-4321 | Reeves Blvd      | fefefe | d3333   | nun     | Germany        |



