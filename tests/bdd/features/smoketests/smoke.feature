Feature: Smoke Tests
    In order to perform small, quick tests of the TCM
    As a tester
    I want to be able to run short, simple tests
 
    Scenario: Check company1 exists
        Check that company "company1" exists
        and that company "macho face" does not exist       

    Scenario: Check that a user exists or not
        Check that user "admin admin" is registered
        and that user "Nowhere Man" is not registered
        
    Scenario: Check that a product exists or not
        Check that product "VMK test product" exists
        and that product "Macro Fab" does not exist