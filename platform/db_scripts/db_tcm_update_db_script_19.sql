/**
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * 
 * @author Vadim Kisen
 *
 * copyright 2011 by uTest 
 */
set foreign_key_checks = 0;

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
