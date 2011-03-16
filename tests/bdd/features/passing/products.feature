Feature: Product Tests

    Scenario: Try creating and deleting a Product
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        And a product with name "Camera Pencil Sharpener" does not exist
        when I create a new product with that name
        then a product with that name exists
        and when I delete the product with that name
        then a product with that name does not exist