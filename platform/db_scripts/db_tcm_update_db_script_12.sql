use tcm;

ALTER TABLE TestRunResult ADD (testSuiteId INT);

ALTER TABLE TestRunTestCaseAssignment ADD (testSuiteId INT);

