Feature: Smoke Tests
    In order to perform small, quick tests of the TCM
    As a tester
    I want to be able to run short, simple tests
 
    Scenario: Check company1 exists
        Check that company with name "company1" exists
        and that company with name "macho face" does not exist       

    Scenario: Check that a user exists or not
        Check that user with name "admin admin" exists
        and that user with name "Nowhere Man" does not exist
        
    Scenario: Check that a product exists or not
        Check that product with name "VMK test product" exists
        and that product with name "Macro Fab" does not exist

    Scenario: Create and delete a new user
        Given a user with name "Jimmy Smitz" does not exist
        When I create a new user with name "Jimmy Smitz"
        Then that user with name "Jimmy Smitz" exists
        and when I delete the user with name "Jimmy Smitz"
        Then that user with name "Jimmy Smitz" does not exist
        
    Scenario: Add a new company
        When I add a new company with name "Massive Dynamic"
        Then that company with name "Massive Dynamic" exists