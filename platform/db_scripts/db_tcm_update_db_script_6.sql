use tcm;

ALTER TABLE ApprovalStatusLocale CHANGE description name VARCHAR(255) NOT NULL;
ALTER TABLE CountryLocale CHANGE description name VARCHAR(255) NOT NULL;
ALTER TABLE Locale CHANGE description name VARCHAR(255) NOT NULL;
ALTER TABLE TestCaseStatusLocale CHANGE description name VARCHAR(255) NOT NULL;
ALTER TABLE TestCycleStatusLocale CHANGE description name VARCHAR(255) NOT NULL;
ALTER TABLE TestPlanStatusLocale CHANGE description name VARCHAR(255) NOT NULL;
ALTER TABLE TestRunResultStatusLocale CHANGE description name VARCHAR(255) NOT NULL;
ALTER TABLE TestRunStatusLocale CHANGE description name VARCHAR(255) NOT NULL;
ALTER TABLE TestSuiteStatusLocale CHANGE description name VARCHAR(255) NOT NULL;
ALTER TABLE UserStatusLocale CHANGE description name VARCHAR(255) NOT NULL;

ALTER TABLE Environment DROP COLUMN originalId;
ALTER TABLE EnvironmentGroup DROP COLUMN testerProfileEnvironmentId;
ALTER TABLE EnvironmentGroup DROP COLUMN testerProfileId;
ALTER TABLE EnvironmentProfile DROP COLUMN testerProfileId;