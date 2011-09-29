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
USE  tcm;
set foreign_key_checks = 0;

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

