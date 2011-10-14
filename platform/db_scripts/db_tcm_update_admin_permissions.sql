

insert into RolePermission (permissionId, accessRoleId, createdBy, createDate, lastChangedBy, lastChangeDate) 
select permissionId, 1, 1, current_timestamp, 1, current_timestamp
from Permission p
where not exists 
(
select 1 from RolePermission where accessRoleId = 1 and permissionId = p.permissionId
)
and permissionId > 0;

