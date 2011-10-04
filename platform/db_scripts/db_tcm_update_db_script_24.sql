USE tcm;

set foreign_key_checks =0;

ALTER TABLE
    Tag CHANGE tag name VARCHAR(45) NOT NULL COMMENT
    'Short text associated with the entity.';

ALTER TABLE
    tcm.TestCaseTag DROP FOREIGN KEY fk_TestCaseTag_TestCase1;
ALTER TABLE
    tcm.TestCaseTag CHANGE testCaseId testCaseVersionId INT NOT NULL COMMENT
    'Associated test case id.';
ALTER TABLE
    tcm.TestCaseTag ADD CONSTRAINT fk1_TestCaseVersion FOREIGN KEY (testCaseVersionId) REFERENCES
    tcm.TestCaseVersion (testCaseVersionId);
