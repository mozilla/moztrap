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


-- Add parent columns to speed up searches.
ALTER TABLE
    ProductComponent ADD (companyId INT NOT NULL);
update ProductComponent
set companyId = (select companyId from Product tc where tc.productId = productId limit 1)
;

ALTER TABLE
    TestCase ADD (companyId INT NOT NULL);
update TestCase
set companyId = (select companyId from Product tc where tc.productId = productId limit 1)
;

ALTER TABLE
    TestCaseVersion ADD (companyId INT NOT NULL);
update TestCaseVersion
set companyId = (select companyId from Product tc where tc.productId = productId limit 1)
;

ALTER TABLE
    TestCycle ADD (companyId INT NOT NULL);
update TestCycle
set companyId = (select companyId from Product tc where tc.productId = productId limit 1)
;

ALTER TABLE
    TestPlan ADD (companyId INT NOT NULL);
update TestPlan
set companyId = (select companyId from Product tc where tc.productId = productId limit 1)
;

ALTER TABLE
    TestRun ADD (companyId INT NOT NULL);
update TestRun
set companyId = (select companyId from Product tc where tc.productId = productId limit 1)
;

ALTER TABLE
    TestRunResult ADD (testCycleId INT NOT NULL);
ALTER TABLE
    TestRunResult ADD (companyId INT NOT NULL);
update TestRunResult
set companyId = (select companyId from Product tc where tc.productId = productId limit 1)
;
update TestRunResult
set testCycleId = (select testCycleId from TestRun tc where tc.testRunId = testRunId limit 1)
;

ALTER TABLE
    TestRunTestCase ADD (testCycleId INT NOT NULL);
ALTER TABLE
    TestRunTestCase ADD (productId INT NOT NULL);
ALTER TABLE
    TestRunTestCase ADD (companyId INT NOT NULL);
update TestRunTestCase
set testCycleId = (select testCycleId from TestRun tc where tc.testRunId = testRunId limit 1)
;
update TestRunTestCase
set productId = (select productId from TestCycle tc where tc.testCycleId = testCycleId limit 1)
,companyId = (select companyId from TestCycle tc where tc.testCycleId = testCycleId limit 1)
;

ALTER TABLE
    TestRunTestCaseAssignment ADD (testCycleId INT NOT NULL);
ALTER TABLE
    TestRunTestCaseAssignment ADD (companyId INT NOT NULL);
update TestRunTestCaseAssignment
set testCycleId = (select testCycleId from TestRun tc where tc.testRunId = testRunId limit 1)
;
update TestRunTestCaseAssignment
set productId = (select productId from TestCycle tc where tc.testCycleId = testCycleId limit 1)
,companyId = (select companyId from TestCycle tc where tc.testCycleId = testCycleId limit 1)
;

ALTER TABLE
    TestSuite ADD (companyId INT NOT NULL);
update TestSuite
set companyId = (select companyId from Product tc where tc.productId = productId limit 1)
;

-- add description to Attachment
ALTER TABLE
    Attachment ADD (description TEXT);

-- create new table
CREATE TABLE `ProductVersion` (
  `productVersionId` int(11) NOT NULL AUTO_INCREMENT,
  `productId` int(11) NOT NULL,
  `name` varchar(255) NOT NULL COMMENT 'Name of ProductVersion.',
  `description` text COMMENT 'Detailed description of ProductVersion',
  `createdBy` int(11) NOT NULL,
  `createDate` datetime NOT NULL,
  `lastChangedBy` int(11) NOT NULL,
  `lastChangeDate` datetime NOT NULL,
  `version` int(11) NOT NULL DEFAULT '0',
  `companyId` int(11) NOT NULL,
  PRIMARY KEY (`productVersionId`),
  KEY `fk_ProductVersion_Product1` (`productId`),
  CONSTRAINT `fk_ProductVersion_Product1` FOREIGN KEY (`productId`) REFERENCES `Product` (`productId`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;    

INSERT
INTO
    ProductVersion
    (
        productId,
        companyId,
        name,
        description,
        createdBy,
        createDate,
        lastChangedBy,
        lastChangeDate,
        version
    )
SELECT
    productId,
    companyId,
    name,
    description,
    createdBy,
    createDate,
    lastChangedBy,
    lastChangeDate,
    version
FROM
    Product;

ALTER TABLE    
	TestRun  ADD (productVersionId INT);
	
ALTER TABLE    
	TestCycle  ADD (productVersionId INT);
	
update TestCycle
set productVersionId = (select productVersionId from ProductVersion tc where tc.productId = productId limit 1)
;

