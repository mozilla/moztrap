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

insert into EnvironmentType (environmentTypeId, parentEnvironmentTypeId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate, version) values (14, null, -22222, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00', 0);
insert into EnvironmentType (environmentTypeId, parentEnvironmentTypeId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate, version) values (15, 14, -22222, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00', 0);
insert into EnvironmentType (environmentTypeId, parentEnvironmentTypeId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate, version) values (21, 14, -22222, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00', 0);
insert into EnvironmentTypeLocale (environmentTypeLocaleId, environmentTypeId, name, localeCode, sortOrder, createdBy, createDate, lastChangedBy, lastChangeDate) values (14, 14, 'Operating System', 'en_US', 0, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00');
insert into EnvironmentTypeLocale (environmentTypeLocaleId, environmentTypeId, name, localeCode, sortOrder, createdBy, createDate, lastChangedBy, lastChangeDate) values (15, 15, 'Operating System Version', 'en_US', 0, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00');
insert into EnvironmentTypeLocale (environmentTypeLocaleId, environmentTypeId, name, localeCode, sortOrder, createdBy, createDate, lastChangedBy, lastChangeDate) values (21, 21, 'Web Browser', 'en_US', 0, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00');

insert into Environment (environmentId, environmentTypeId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate, version) values (2573, 14, -22222, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00', 0);
insert into Environment (environmentId, environmentTypeId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate, version) values (2574, 14, -22222, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00', 0);
insert into Environment (environmentId, environmentTypeId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate, version) values (2575, 14, -22222, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00', 0);
insert into Environment (environmentId, environmentTypeId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate, version) values (2577, 15, -22222, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00', 0);
insert into Environment (environmentId, environmentTypeId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate, version) values (2578, 15, -22222, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00', 0);
insert into Environment (environmentId, environmentTypeId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate, version) values (2579, 15, -22222, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00', 0);
insert into Environment (environmentId, environmentTypeId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate, version) values (2580, 15, -22222, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00', 0);
insert into Environment (environmentId, environmentTypeId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate, version) values (2581, 15, -22222, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00', 0);
insert into Environment (environmentId, environmentTypeId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate, version) values (2582, 15, -22222, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00', 0);
insert into Environment (environmentId, environmentTypeId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate, version) values (2583, 15, -22222, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00', 0);
insert into Environment (environmentId, environmentTypeId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate, version) values (2584, 15, -22222, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00', 0);
insert into Environment (environmentId, environmentTypeId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate, version) values (2585, 15, -22222, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00', 0);
insert into Environment (environmentId, environmentTypeId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate, version) values (2586, 15, -22222, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00', 0);
insert into Environment (environmentId, environmentTypeId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate, version) values (2587, 15, -22222, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00', 0);
insert into Environment (environmentId, environmentTypeId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate, version) values (2588, 15, -22222, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00', 0);
insert into Environment (environmentId, environmentTypeId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate, version) values (2589, 15, -22222, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00', 0);
insert into Environment (environmentId, environmentTypeId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate, version) values (2590, 15, -22222, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00', 0);
insert into Environment (environmentId, environmentTypeId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate, version) values (2591, 15, -22222, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00', 0);
insert into Environment (environmentId, environmentTypeId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate, version) values (3130, 21, -22222, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00', 0);
insert into Environment (environmentId, environmentTypeId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate, version) values (3131, 21, -22222, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00', 0);
insert into Environment (environmentId, environmentTypeId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate, version) values (3132, 21, -22222, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00', 0);
insert into Environment (environmentId, environmentTypeId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate, version) values (3133, 21, -22222, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00', 0);
insert into Environment (environmentId, environmentTypeId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate, version) values (3134, 21, -22222, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00', 0);
insert into Environment (environmentId, environmentTypeId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate, version) values (3135, 21, -22222, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00', 0);
insert into Environment (environmentId, environmentTypeId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate, version) values (3136, 21, -22222, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00', 0);
insert into Environment (environmentId, environmentTypeId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate, version) values (3137, 21, -22222, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00', 0);
insert into Environment (environmentId, environmentTypeId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate, version) values (3589, 15, -22222, 1, '2011-09-27 00:00:00', 1, '2010-09-27 00:00:00', 0);
insert into Environment (environmentId, environmentTypeId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate, version) values (3590, 15, -22222, 1, '2011-09-27 00:00:00', 1, '2010-09-27 00:00:00', 0);
insert into Environment (environmentId, environmentTypeId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate, version) values (3591, 15, -22222, 1, '2011-09-27 00:00:00', 1, '2010-09-27 00:00:00', 0);
insert into Environment (environmentId, environmentTypeId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate, version) values (3592, 15, -22222, 1, '2011-09-27 00:00:00', 1, '2010-09-27 00:00:00', 0);
insert into Environment (environmentId, environmentTypeId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate, version) values (3593, 15, -22222, 1, '2011-09-27 00:00:00', 1, '2010-09-27 00:00:00', 0);

insert into EnvironmentLocale (environmentLocaleId, environmentId, name, localeCode, sortOrder, createdBy, createDate, lastChangedBy, lastChangeDate) values (2522, 2573, 'Windows', 'en_US', 0, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00');
insert into EnvironmentLocale (environmentLocaleId, environmentId, name, localeCode, sortOrder, createdBy, createDate, lastChangedBy, lastChangeDate) values (2523, 2574, 'Linux', 'en_US', 0, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00');
insert into EnvironmentLocale (environmentLocaleId, environmentId, name, localeCode, sortOrder, createdBy, createDate, lastChangedBy, lastChangeDate) values (2524, 2575, 'MAC OS', 'en_US', 0, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00');
insert into EnvironmentLocale (environmentLocaleId, environmentId, name, localeCode, sortOrder, createdBy, createDate, lastChangedBy, lastChangeDate) values (2526, 2577, 'Vista', 'en_US', 0, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00');
insert into EnvironmentLocale (environmentLocaleId, environmentId, name, localeCode, sortOrder, createdBy, createDate, lastChangedBy, lastChangeDate) values (2527, 2578, 'XP', 'en_US', 0, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00');
insert into EnvironmentLocale (environmentLocaleId, environmentId, name, localeCode, sortOrder, createdBy, createDate, lastChangedBy, lastChangeDate) values (2528, 2579, '2003', 'en_US', 0, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00');
insert into EnvironmentLocale (environmentLocaleId, environmentId, name, localeCode, sortOrder, createdBy, createDate, lastChangedBy, lastChangeDate) values (2529, 2580, '2000', 'en_US', 0, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00');
insert into EnvironmentLocale (environmentLocaleId, environmentId, name, localeCode, sortOrder, createdBy, createDate, lastChangedBy, lastChangeDate) values (2530, 2581, '7', 'en_US', 0, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00');
insert into EnvironmentLocale (environmentLocaleId, environmentId, name, localeCode, sortOrder, createdBy, createDate, lastChangedBy, lastChangeDate) values (2531, 2582, 'OS X 10.6', 'en_US', 0, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00');
insert into EnvironmentLocale (environmentLocaleId, environmentId, name, localeCode, sortOrder, createdBy, createDate, lastChangedBy, lastChangeDate) values (2532, 2583, 'OS X 10.5', 'en_US', 0, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00');
insert into EnvironmentLocale (environmentLocaleId, environmentId, name, localeCode, sortOrder, createdBy, createDate, lastChangedBy, lastChangeDate) values (2533, 2584, 'OS X 10.4', 'en_US', 0, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00');
insert into EnvironmentLocale (environmentLocaleId, environmentId, name, localeCode, sortOrder, createdBy, createDate, lastChangedBy, lastChangeDate) values (2534, 2585, 'OS X 10.3', 'en_US', 0, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00');
insert into EnvironmentLocale (environmentLocaleId, environmentId, name, localeCode, sortOrder, createdBy, createDate, lastChangedBy, lastChangeDate) values (2535, 2586, 'Debian', 'en_US', 0, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00');
insert into EnvironmentLocale (environmentLocaleId, environmentId, name, localeCode, sortOrder, createdBy, createDate, lastChangedBy, lastChangeDate) values (2536, 2587, 'Ubuntu', 'en_US', 0, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00');
insert into EnvironmentLocale (environmentLocaleId, environmentId, name, localeCode, sortOrder, createdBy, createDate, lastChangedBy, lastChangeDate) values (2537, 2588, 'Xebian', 'en_US', 0, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00');
insert into EnvironmentLocale (environmentLocaleId, environmentId, name, localeCode, sortOrder, createdBy, createDate, lastChangedBy, lastChangeDate) values (2538, 2589, 'Vista 64-bit', 'en_US', 0, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00');
insert into EnvironmentLocale (environmentLocaleId, environmentId, name, localeCode, sortOrder, createdBy, createDate, lastChangedBy, lastChangeDate) values (2539, 2590, '7 64-bit', 'en_US', 0, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00');
insert into EnvironmentLocale (environmentLocaleId, environmentId, name, localeCode, sortOrder, createdBy, createDate, lastChangedBy, lastChangeDate) values (2540, 2591, 'XP 64-bit', 'en_US', 0, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00');
insert into EnvironmentLocale (environmentLocaleId, environmentId, name, localeCode, sortOrder, createdBy, createDate, lastChangedBy, lastChangeDate) values (3079, 3130, 'Chrome', 'en_US', 0, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00');
insert into EnvironmentLocale (environmentLocaleId, environmentId, name, localeCode, sortOrder, createdBy, createDate, lastChangedBy, lastChangeDate) values (3080, 3131, 'Firefox', 'en_US', 0, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00');
insert into EnvironmentLocale (environmentLocaleId, environmentId, name, localeCode, sortOrder, createdBy, createDate, lastChangedBy, lastChangeDate) values (3081, 3132, 'Internet Explorer 6', 'en_US', 0, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00');
insert into EnvironmentLocale (environmentLocaleId, environmentId, name, localeCode, sortOrder, createdBy, createDate, lastChangedBy, lastChangeDate) values (3082, 3133, 'Internet Explorer 7', 'en_US', 0, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00');
insert into EnvironmentLocale (environmentLocaleId, environmentId, name, localeCode, sortOrder, createdBy, createDate, lastChangedBy, lastChangeDate) values (3083, 3134, 'Internet Explorer 8', 'en_US', 0, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00');
insert into EnvironmentLocale (environmentLocaleId, environmentId, name, localeCode, sortOrder, createdBy, createDate, lastChangedBy, lastChangeDate) values (3084, 3135, 'Opera', 'en_US', 0, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00');
insert into EnvironmentLocale (environmentLocaleId, environmentId, name, localeCode, sortOrder, createdBy, createDate, lastChangedBy, lastChangeDate) values (3085, 3136, 'Safari', 'en_US', 0, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00');
insert into EnvironmentLocale (environmentLocaleId, environmentId, name, localeCode, sortOrder, createdBy, createDate, lastChangedBy, lastChangeDate) values (3086, 3137, 'Internet Explorer 9', 'en_US', 0, 1, '2010-11-03 00:00:00', 1, '2010-11-03 00:00:00');
insert into EnvironmentLocale (environmentLocaleId, environmentId, name, localeCode, sortOrder, createdBy, createDate, lastChangedBy, lastChangeDate) values (3238, 3589, 'OS X 10.7', 'en_US', 12, 1, '2011-09-27 00:00:00', 1, '2011-09-27 00:00:00');
insert into EnvironmentLocale (environmentLocaleId, environmentId, name, localeCode, sortOrder, createdBy, createDate, lastChangedBy, lastChangeDate) values (3239, 3590, 'CentOS', 'en_US', 0, 1, '2011-09-27 00:00:00', 1, '2011-09-27 00:00:00');
insert into EnvironmentLocale (environmentLocaleId, environmentId, name, localeCode, sortOrder, createdBy, createDate, lastChangedBy, lastChangeDate) values (3240, 3591, 'Chrome OS', 'en_US', 0, 1, '2011-09-27 00:00:00', 1, '2011-09-27 00:00:00');
insert into EnvironmentLocale (environmentLocaleId, environmentId, name, localeCode, sortOrder, createdBy, createDate, lastChangedBy, lastChangeDate) values (3241, 3592, 'Fedora', 'en_US', 0, 1, '2011-09-27 00:00:00', 1, '2011-09-27 00:00:00');
insert into EnvironmentLocale (environmentLocaleId, environmentId, name, localeCode, sortOrder, createdBy, createDate, lastChangedBy, lastChangeDate) values (3242, 3593, 'Mint', 'en_US', 0, 1, '2011-09-27 00:00:00', 1, '2011-09-27 00:00:00');

insert into ParentDependableEnvironment (environmentId, parentEnvironmentId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate) values (2577, 2573, -22222, 1, '2010-11-04 00:00:00', 1, '2010-11-04 00:00:00');
insert into ParentDependableEnvironment (environmentId, parentEnvironmentId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate) values (2578, 2573, -22222, 1, '2010-11-04 00:00:00', 1, '2010-11-04 00:00:00');
insert into ParentDependableEnvironment (environmentId, parentEnvironmentId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate) values (2579, 2573, -22222, 1, '2010-11-04 00:00:00', 1, '2010-11-04 00:00:00');
insert into ParentDependableEnvironment (environmentId, parentEnvironmentId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate) values (2580, 2573, -22222, 1, '2010-11-04 00:00:00', 1, '2010-11-04 00:00:00');
insert into ParentDependableEnvironment (environmentId, parentEnvironmentId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate) values (2581, 2573, -22222, 1, '2010-11-04 00:00:00', 1, '2010-11-04 00:00:00');
insert into ParentDependableEnvironment (environmentId, parentEnvironmentId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate) values (2589, 2573, -22222, 1, '2010-11-04 00:00:00', 1, '2010-11-04 00:00:00');
insert into ParentDependableEnvironment (environmentId, parentEnvironmentId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate) values (2590, 2573, -22222, 1, '2010-11-04 00:00:00', 1, '2010-11-04 00:00:00');
insert into ParentDependableEnvironment (environmentId, parentEnvironmentId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate) values (2591, 2573, -22222, 1, '2010-11-04 00:00:00', 1, '2010-11-04 00:00:00');
insert into ParentDependableEnvironment (environmentId, parentEnvironmentId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate) values (2586, 2574, -22222, 1, '2010-11-04 00:00:00', 1, '2010-11-04 00:00:00');
insert into ParentDependableEnvironment (environmentId, parentEnvironmentId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate) values (2587, 2574, -22222, 1, '2010-11-04 00:00:00', 1, '2010-11-04 00:00:00');
insert into ParentDependableEnvironment (environmentId, parentEnvironmentId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate) values (2588, 2574, -22222, 1, '2010-11-04 00:00:00', 1, '2010-11-04 00:00:00');
insert into ParentDependableEnvironment (environmentId, parentEnvironmentId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate) values (2582, 2575, -22222, 1, '2010-11-04 00:00:00', 1, '2010-11-04 00:00:00');
insert into ParentDependableEnvironment (environmentId, parentEnvironmentId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate) values (2583, 2575, -22222, 1, '2010-11-04 00:00:00', 1, '2010-11-04 00:00:00');
insert into ParentDependableEnvironment (environmentId, parentEnvironmentId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate) values (2584, 2575, -22222, 1, '2010-11-04 00:00:00', 1, '2010-11-04 00:00:00');
insert into ParentDependableEnvironment (environmentId, parentEnvironmentId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate) values (2585, 2575, -22222, 1, '2010-11-04 00:00:00', 1, '2010-11-04 00:00:00');
insert into ParentDependableEnvironment (environmentId, parentEnvironmentId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate) values (2592, 2576, -22222, 1, '2010-11-04 00:00:00', 1, '2010-11-04 00:00:00');
insert into ParentDependableEnvironment (environmentId, parentEnvironmentId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate) values (3590, 2574, -22222, 1, '2011-09-27 00:00:00', 1, '2011-09-27 00:00:00');
insert into ParentDependableEnvironment (environmentId, parentEnvironmentId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate) values (3591, 2574, -22222, 1, '2011-09-27 00:00:00', 1, '2011-09-27 00:00:00');
insert into ParentDependableEnvironment (environmentId, parentEnvironmentId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate) values (3592, 2574, -22222, 1, '2011-09-27 00:00:00', 1, '2011-09-27 00:00:00');
insert into ParentDependableEnvironment (environmentId, parentEnvironmentId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate) values (3593, 2574, -22222, 1, '2011-09-27 00:00:00', 1, '2011-09-27 00:00:00');
insert into ParentDependableEnvironment (environmentId, parentEnvironmentId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate) values (3589, 2575, -22222, 1, '2011-09-27 00:00:00', 1, '2011-09-27 00:00:00');
insert into ParentDependableEnvironment (environmentId, parentEnvironmentId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate) values (3130, 2573, -22222, 1, '2011-09-29 00:00:00', 1, '2011-09-29 00:00:00');
insert into ParentDependableEnvironment (environmentId, parentEnvironmentId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate) values (3131, 2573, -22222, 1, '2011-09-29 00:00:00', 1, '2011-09-29 00:00:00');
insert into ParentDependableEnvironment (environmentId, parentEnvironmentId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate) values (3135, 2573, -22222, 1, '2011-09-29 00:00:00', 1, '2011-09-29 00:00:00');
insert into ParentDependableEnvironment (environmentId, parentEnvironmentId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate) values (3136, 2573, -22222, 1, '2011-09-29 00:00:00', 1, '2011-09-29 00:00:00');
insert into ParentDependableEnvironment (environmentId, parentEnvironmentId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate) values (3130, 2574, -22222, 1, '2011-09-29 00:00:00', 1, '2011-09-29 00:00:00');
insert into ParentDependableEnvironment (environmentId, parentEnvironmentId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate) values (3131, 2574, -22222, 1, '2011-09-29 00:00:00', 1, '2011-09-29 00:00:00');
insert into ParentDependableEnvironment (environmentId, parentEnvironmentId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate) values (3135, 2574, -22222, 1, '2011-09-29 00:00:00', 1, '2011-09-29 00:00:00');
insert into ParentDependableEnvironment (environmentId, parentEnvironmentId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate) values (3136, 2574, -22222, 1, '2011-09-29 00:00:00', 1, '2011-09-29 00:00:00');
insert into ParentDependableEnvironment (environmentId, parentEnvironmentId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate) values (3130, 2575, -22222, 1, '2011-09-29 00:00:00', 1, '2011-09-29 00:00:00');
insert into ParentDependableEnvironment (environmentId, parentEnvironmentId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate) values (3131, 2575, -22222, 1, '2011-09-29 00:00:00', 1, '2011-09-29 00:00:00');
insert into ParentDependableEnvironment (environmentId, parentEnvironmentId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate) values (3135, 2575, -22222, 1, '2011-09-29 00:00:00', 1, '2011-09-29 00:00:00');
insert into ParentDependableEnvironment (environmentId, parentEnvironmentId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate) values (3136, 2575, -22222, 1, '2011-09-29 00:00:00', 1, '2011-09-29 00:00:00');
insert into ParentDependableEnvironment (environmentId, parentEnvironmentId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate) values (3132, 2573, -22222, 1, '2011-09-29 00:00:00', 1, '2011-09-29 00:00:00');
insert into ParentDependableEnvironment (environmentId, parentEnvironmentId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate) values (3133, 2573, -22222, 1, '2011-09-29 00:00:00', 1, '2011-09-29 00:00:00');
insert into ParentDependableEnvironment (environmentId, parentEnvironmentId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate) values (3134, 2573, -22222, 1, '2011-09-29 00:00:00', 1, '2011-09-29 00:00:00');
insert into ParentDependableEnvironment (environmentId, parentEnvironmentId, companyId, createdBy, createDate, lastChangedBy, lastChangeDate) values (3137, 2573, -22222, 1, '2011-09-29 00:00:00', 1, '2011-09-29 00:00:00');
