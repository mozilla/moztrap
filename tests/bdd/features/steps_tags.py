'''
Created on Feb 9, 2011

@author: camerondawson
'''
from lettuce import *
from step_helper import *


'''
######################################################################

                     TAG STEPS

######################################################################
'''

@step(u'create a new tag with (that name|name "(.*)")')
def create_tag_with_name(step, stored, name):
    name = get_stored_or_store_name("tag", stored, name)
    
    headers = {'Authorization': get_auth_header(),
               'content-type': "application/x-www-form-urlencoded"
               }

    post_payload = {"productId": 1,
                    "name": name,
                    "description": "Sweet Relief",
                    "useLatestVersions": "true"
                   }
    
    world.conn.request("POST", add_params(world.path_tags), 
                       urllib.urlencode(post_payload, doseq=True), 
                       headers)

    response = world.conn.getresponse()
    verify_status(200, response, "Create new user")



@step(u'tag with (that name|name "(.*)") (exists|does not exist)')
def check_tag_foo_existence(step, stored, name, existence):
    name = get_stored_or_store_name("tag", stored, name)
    search_and_verify_existence(step, world.path_tags, 
                    {"name": name}, 
                     "tag", existence)


@step(u'delete the tag with (that name|name "(.*)")')
def delete_tag_with_name_foo(step, stored, name):
    name = get_stored_or_store_name("tag", stored, name)
    
    headers = {'Authorization': get_auth_header(),
               'content-type': "application/x-www-form-urlencoded"
               }

    tag_id, version = get_resource_identity("tag", 
                                                  add_params(world.path_tags, {"name": name}))
               
    world.conn.request("DELETE", 
                       add_params(world.path_tags + tag_id, 
                                  {"originalVersionId": version}), "", headers)

    response = world.conn.getresponse()
    verify_status(200, response, "delete tag")

