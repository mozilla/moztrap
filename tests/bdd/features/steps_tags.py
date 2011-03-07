'''
Created on Feb 9, 2011

@author: camerondawson
'''
from features.step_helper import get_seed_company_id, do_post, \
    get_stored_or_store_field, search_and_verify_existence, get_tag_resid, do_delete
from lettuce import step, world


'''
######################################################################

                     TAG STEPS

######################################################################
'''

@step(u'create a new tag with (that tag|tag "(.*)")')
def create_tag_with_name(step, stored, tag):
    tag = get_stored_or_store_field("tag", "tag", stored, tag)

    post_payload = {"companyId": get_seed_company_id(),
                    "tag": tag
                   }

    do_post(world.path_tags,
            post_payload)



@step(u'tag with (that tag|tag "(.*)") (exists|does not exist)')
def check_tag_foo_existence(step, stored, tag, existence):
    tag = get_stored_or_store_field("tag", "tag", stored, tag)
    search_and_verify_existence(world.path_tags,
                    {"tag": tag},
                     "tag", existence)


@step(u'delete the tag with (that tag|tag "(.*)")')
def delete_tag_with_tag_foo(step, stored, tag):
    tag = get_stored_or_store_field("tag", "tag", stored, tag)

    tag_id, version = get_tag_resid(tag)

    do_delete(world.path_tags + str(tag_id),
              {"originalVersionId": version})

