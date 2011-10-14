

set foreign_key_checks =0;

ALTER TABLE
    Tag CHANGE tag name VARCHAR(45) NOT NULL COMMENT
    'Short text associated with the entity.';

ALTER TABLE
    TestCaseTag DROP FOREIGN KEY fk_TestCaseTag_TestCase1;
ALTER TABLE
    TestCaseTag CHANGE testCaseId testCaseVersionId INT NOT NULL COMMENT
    'Associated test case id.';
ALTER TABLE
    TestCaseTag ADD CONSTRAINT fk1_TestCaseVersion FOREIGN KEY (testCaseVersionId) REFERENCES
    TestCaseVersion (testCaseVersionId);
