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

@step(u'create a new tag with (that tag|tag "(.*)")')
def create_tag_with_name(step, stored, tag):
    tag = get_stored_or_store_field("tag", "tag", stored, tag)
    
    post_payload = {"companyId": 9,
                    "tag": tag
                   }
    
    do_post(world.path_tags,
            post_payload)



@step(u'tag with (that tag|tag "(.*)") (exists|does not exist)')
def check_tag_foo_existence(step, stored, tag, existence):
    tag = get_stored_or_store_field("tag", "tag", stored, tag)
    search_and_verify_existence(step, world.path_tags, 
                    {"tag": tag}, 
                     "tag", existence)


@step(u'delete the tag with (that tag|tag "(.*)")')
def delete_tag_with_tag_foo(step, stored, tag):
    tag = get_stored_or_store_field("tag", "tag", stored, tag)
    
    tag_id, version = get_resource_identity("tag", 
                                             add_params(world.path_tags, {"tag": tag}))
               
    do_delete(world.path_tags + tag_id, 
              {"originalVersionId": version})

