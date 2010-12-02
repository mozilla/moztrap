Feature: Users Roles
    In order to manage testing roles
    As Users
    We should implement Role management

    Scenario: Get list of roles
        Given at least these roles exist:
            | description |
            | Frame       |
            | Apple       |
            | Zipper      |
        Then "ASC" role searches list "Apple" before "Zipper"
        and "DESC" role searches list "Zipper" before "Apple"
        
    Scenario: Create a new Role and add Permission
        Given I am logged in as user "Jedi Admin"
        and user "Jedi Admin" has the role of "ADMINISTRATOR"
        When I create a new role of "Creationator"
        and add permission of "Spammer" to the role of "Creationator"
        Then role of "Creationator" has permission of "Spammer"

    
   