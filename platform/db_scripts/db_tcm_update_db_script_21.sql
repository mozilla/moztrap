

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

