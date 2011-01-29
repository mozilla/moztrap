Feature: Smoke Tests
    In order to test my steps
    As a Lettuce developer
    I want to be able to run test snippets to test the framework
 
    Scenario: Try creating and deleting a Product
        Given a product with name "Camera Pencil Sharpener" does not exist
        when I create a new product with that name
        then a product with that name exists
        and when I delete the product with that name
        then a product with that name does not exist