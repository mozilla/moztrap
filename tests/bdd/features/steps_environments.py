'''
Created on Jan 28, 2011

@author: camerondawson
'''
from lettuce import *
from step_helper import *

'''
######################################################################

                     ENVIRONMENT STEPS

######################################################################
'''

@step(u'an (environment|environmenttype|environmentgroup) with (that name|name "(.*)") (exists|does not exist)')
def check_environement_foo_existence(step, objtype, stored, name, existence):
    name = get_stored_or_store_name(objtype, stored, name)
    
    
    search_and_verify_existence(world.env_path_map[objtype], 
                    {"name": name}, 
                    objtype, existence)

@step(u'a group environmenttype with (that name|name "(.*)") (exists|does not exist)')
def check_group_environement_foo_existence(step, stored, name, existence):
    objtype = "environmenttype"
    name = get_stored_or_store_name(objtype, stored, name)
    
    
    search_and_verify_existence(world.env_path_map[objtype], 
                    {"name": name,
                     "groupType": True}, 
                     objtype, existence)

@step(u'create a new environment with (that name|name "(.*)") of type (.*)')
def create_environment_with_name(step, stored, name, type_name):
    '''
        This creates an environmenttype that applies to an environment object
    '''
    name = get_stored_or_store_name("environment", stored, name)
    
    type_resid = get_environmenttype_resid(type_name)[0]
    
    post_payload = {
                    "name": name,
                    "companyId": get_seed_company_id(),
                    "environmentTypeId": type_resid
                    }
    
    do_post(world.path_environments,
            post_payload)


@step(u'delete the environment with (that name|name "(.*)")')
def delete_environment_with_name(step, stored, name):
    name = get_stored_or_store_name("environment", stored, name)
    
    resid, version = get_environment_resid(name)

    do_delete(world.path_environments + resid, 
              {"originalVersionId": version})
               

#@todo: do we need this function?
#@step(u'product with (that name|name "(.*)" (has|does not have) the environmentgroup with (that name|name "(.*)"')
def product_has_environementgroup(step, stored_prod, prod_name, haveness, stored_envgrp, envgrp_name):
    prod_name = get_stored_or_store_name("product", stored_prod, prod_name) 
    envgrp_name  = get_stored_or_store_name("environment", stored_envgrp, envgrp_name)
     
    # this url needs to search for environment groups for that product
    # should be products/{id}/environmentgroups
    
    resid = get_product_resid(prod_name)[0]

    
    uri = world.path_products + "/" + resid + "/environmentgroups"
    search_and_verify(uri, 
                      {"name": envgrp_name}, 
                      "environmentgroup", 
                      (haveness == "has"))


'''
######################################################################

                     ENVIRONMENT TYPE STEPS

######################################################################
'''

@step(u'create a new (group environmenttype|environmenttype) with (that name|name "(.*)")')
def create_environmenttype_with_name(step, group, stored, name):
    '''
        This creates an environmenttype that applies to an environmentGroup object
    '''
    groupType = (group.strip() == "group environmenttype")
    name = get_stored_or_store_name("environmenttype", stored, name)
    
    post_payload = {
                    "name": name,
                    "groupType": groupType,
                    "companyId": get_seed_company_id()
                    }
    
    do_post(world.path_environmenttypes,
            post_payload)

@step(u'delete the environmenttype with (that name|name "(.*)")')
def delete_environmenttype_with_name(step, stored, name):
    name = get_stored_or_store_name("environmenttype", stored, name)
    
    resid, version = get_environmenttype_resid(name)
    do_delete(world.path_environmenttypes + resid, 
              {"originalVersionId": version})
               

@step(u'environmenttype with (that name|name "(.*)") is (a group|not a group) environmenttype')
def check_group_environmenttype_with_name(step, stored, name, is_group):

    name = get_stored_or_store_name("environmenttype", stored, name)
    groupType = (is_group.strip() == "a group")
   
    data = do_get(world.path_environmenttypes, {"name": name})

    env_type = get_single_item(data, "environmenttype")
    eq_(env_type[ns("groupType")], groupType, "GroupType match check")

'''
######################################################################

                     ENVIRONMENT GROUP STEPS

######################################################################
'''
@step(u'create a new environmentgroup with (that name|name "(.*)") of type "(.*)"')
def create_environmentgroup_with_name(step, stored, name, type_name):
    name = get_stored_or_store_name("environmentgroup", stored, name)
    
    type_resid = get_environmenttype_resid(type_name)[0]
    post_payload = {
                    "name": name,
                    "description": "oh, this old thing...",
                    "companyId": get_seed_company_id(),
                    "environmentTypeId": type_resid
                    }
    
    do_post(world.path_environmentgroups,
            post_payload)


@step(u'delete the environmentgroup with (that name|name "(.*)")')
def delete_environmentgroup_with_name(step, stored, name):
    name = get_stored_or_store_name("environmentgroup", stored, name)
    
    resid, version = get_environmentgroup_resid(name)
               
    do_delete(world.path_environmentgroups + resid, 
                                            {"originalVersionId": version})
   

