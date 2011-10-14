

drop view if exists TestCaseVersionView;
create view  TestCaseVersionView
as
select 
t.name
,t.maxAttachmentSizeInMBytes
,t.maxNumberOfAttachments
,t.testCycleId
, v.*
from TestCase t
join TestCaseVersion v on v.testCaseId = t.testCaseId;

drop view if exists TestRunTestCaseView;
create view  TestRunTestCaseView
as
select 
t.name
, v.description
, v.majorVersion
, v.minorVersion
, v.latestVersion
, v.testCaseStatusId
, v.approvalStatusId
, v.approvedBy
, v.approveDate
, v.automated
, v.automationUri
, trtc.*
from TestCase t
join TestCaseVersion v on v.testCaseId = t.testCaseId
join TestRunTestCase trtc on v.testCaseVersionId = trtc.testCaseVersionId;

-- view to join test suite included test case with test case and test case version
drop view if exists TestSuiteTestCaseView;
create view  TestSuiteTestCaseView
as
select 
t.name
, v.description
, v.companyId
, v.productId
, v.majorVersion
, v.minorVersion
, v.latestVersion
, v.testCaseStatusId
, v.approvalStatusId
, v.approvedBy
, v.approveDate
, v.automated
, v.automationUri
, trtc.*
from TestCase t
join TestCaseVersion v on v.testCaseId = t.testCaseId
join TestSuiteTestCase trtc on v.testCaseVersionId = trtc.testCaseVersionId;

drop view if exists EnvironmentView;
CREATE VIEW EnvironmentView
AS
select e.* , el.name, el.localeCode,  el.sortOrder
from EnvironmentLocale el 
join Environment e on e.environmentId = el.environmentId
;

drop view if exists EnvironmentTypeView;
CREATE VIEW EnvironmentTypeView
AS
select e.* , el.name, el.localeCode,  el.sortOrder
from EnvironmentTypeLocale el 
join EnvironmentType e on e.environmentTypeId = el.environmentTypeId
;

