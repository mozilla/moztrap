Feature: Smoke Tests
    In order to perform small, quick tests of the TCM
    As a tester
    I want to be able to run short, simple tests
 
    Scenario: Check company1 exists
        Check that company with name "company1" exists
        and that company with name "macho face" does not exist       

    Scenario: Check company1 exists
        Check that company with name "company1" exists
        and that company with name "macho face" does not exist
        when I create a new company with name "macho face"
        then a company with name "macho face" exists
        and when I delete the company with that name
        then a company with that name does not exist      
        
    Scenario: Check that a user exists or not
        Check that user with name "admin admin" exists
        and that user with name "Nowhere Man" does not exist
        
    Scenario: Create and then deactivate a new user
        Given a user with name "Nowhere Man" does not exist
        When I create a new user with that name
        Then a user with that name exists
        and the user with that name is inactive
        and when I activate the user with that name
        Then the user with that name is active
        and when I deactivate the user with that name
        Then the user with that name is disabled
        
    Scenario: Check that a product exists or not
        Check that product with name "VMK test product" exists
        and that product with name "Macro Fab" does not exist

    Scenario: Try creating and deleting a Product
        Given a product with name "Camera Pencil Sharpener" does not exist
        when I create a new product with that name
        then a product with that name exists
        and when I delete the product with that name
        then the product with that name does not exist

    Scenario: Try creating and deleting a Test Case
        Given a testcase with name "Come on fhqwhgads" does not exist
        when I create a new testcase with that name
        then a testcase with that name exists
        and when I delete the testcase with that name
        then a testcase with that name does not exist
        
    Scenario: Try creating and deleting an Environment
        Given an environment with name "Come on fhqwhgads" does not exist
        when I create a new environment with that name of type operating
        then an environment with that name exists

