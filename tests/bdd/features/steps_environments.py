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

@step(u'(environment|environmenttype|environmentgroup) with (that name|name "(.*)") (exists|does not exist)')
def check_environement_foo_existence(step, objtype, stored, name, existence):
    name = get_stored_or_store_name(objtype, stored, name) 
    search_and_verify_existence(step, world.path_environments, 
                    {"name": name}, 
                    objtype, existence)

@step(u'create a new environment with (that name|name "(.*)") of type (.*)')
def create_environment_with_name(step, stored, name, type_name):
    '''
        This creates an environmenttype that applies to an environment object
    '''
    name = get_stored_or_store_name("environment", stored, name)
    
    type_resid = get_environmenttype_resid(type_name)
    
    headers = {'Authorization': get_auth_header(),
               'content-type': "application/x-www-form-urlencoded"
               }
               
    post_payload = {
                    "name": name,
                    "companyId": 9,
                    "environmentTypeId": type_resid
                    }
    
    world.conn.request("POST", add_params(world.path_environments), 
                       urllib.urlencode(post_payload, doseq=True), 
                       headers)

    response = world.conn.getresponse()
    verify_status(200, response, "Create new environemnttype")


#@step(u'product with (that name|name "(.*)" (has|does not have) the environmentgroup with (that name|name "(.*)"')
def product_has_environementgroup(step, stored_prod, prod_name, haveness, stored_envgrp, envgrp_name):
    prod_name = get_stored_or_store_name("product", stored_prod, prod_name) 
    envgrp_name  = get_stored_or_store_name("environment", stored_envgrp, envgrp_name)
     
    # this url needs to search for environment groups for that product
    # should be products/{id}/environmentgroups
    
    resid, version = get_product_resid(prod_name)

    
    url = world.path_products + "/" + resid + "/environmentgroups"
    search_and_verify(step, url, 
                      {"name": envgrp_name}, 
                      "environmentgroup", 
                      (haveness == "has"))


'''
######################################################################

                     ENVIRONMENT TYPE STEPS

######################################################################
'''

@step(u'create a new environmenttype( group) with name "(.*)"')
def create_environmenttype_with_name(step, group, name):
    '''
        This creates an environmenttype that applies to an environmentGroup object
    '''
    groupType = (group.strip() == "group")
    name = get_stored_or_store_name("environmenttype", "store", name)
    
    headers = {'Authorization': get_auth_header(),
               'content-type': "application/x-www-form-urlencoded"
               }
               
    post_payload = {
                    "name": name,
                    "groupType": groupType,
                    "companyId": 9
                    }
    
    world.conn.request("POST", add_params(world.path_environmenttypes),  
                       urllib.urlencode(post_payload, doseq=True), 
                       headers)

    response = world.conn.getresponse()
    verify_status(200, response, "Create new environmenttype")


'''
######################################################################

                     ENVIRONMENT GROUP STEPS

######################################################################
'''
@step(u'create a new environmentgroup with (that name|name "(.*)")')
def create_environmentgroup_with_name_foo(step, stored, name):
    name = get_stored_or_store_name("environmentgroup", stored, name)
    
    headers = {'Authorization': get_auth_header(),
               'content-type': "application/x-www-form-urlencoded"
               }
               
    post_payload = {
                    "name": name,
                    "description": "oh, this old thing...",
                    "companyId": 9,
                    "environmentTypeId": 3
                    }
    
    world.conn.request("POST", add_params(world.path_environmentgroups), 
                       urllib.urlencode(post_payload, doseq=True), 
                       headers)

    response = world.conn.getresponse()
    verify_status(200, response, "Create new environemntgroup")


