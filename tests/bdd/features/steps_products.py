'''

Created on Jan 28, 2011
@author: camerondawson
'''
from features.step_helper import get_stored_or_store_name, get_seed_company_id, \
    do_post, get_company_resid, search_and_verify_existence, get_product_resid, \
    do_delete, get_environment_resid, search_and_verify
from lettuce import step, world


'''
######################################################################

                     PRODUCT STEPS

######################################################################
'''

@step(u'create a new product with (that name|name "(.*)")')
def create_product_with_name_foo(step, stored, name):
    name = get_stored_or_store_name("product", stored, name)
    
    post_payload = {"companyId": get_seed_company_id(),
                    "name": name,
                    "description": "Lettuce Product Description"
                   }
    
    do_post(world.path_products, 
            post_payload)


@step(u'create the following new products')
def create_products(step):

    for item in step.hashes:
        # must copy the item, because we change it, and that freaks lettuce out
        # when it displays results
        product = item.copy()
        # persist the last one we make.  Sometimes we will only make one.
        world.names["product"] = product["name"]
        
        # get the company id from the passed company name
        company_id = get_company_resid(product["company name"])[0] 
        product["companyId"] = company_id 
        del product["company name"]
        
    
        do_post(world.path_products, 
                product)

@step(u'product with (that name|name "(.*)") (exists|does not exist)')
def check_product_existence(step, stored, name, existence):
    name = get_stored_or_store_name("product", stored, name)
    search_and_verify_existence(world.path_products, 
                    {"name": name}, 
                    "product", existence)

@step(u'delete the product with (that name|name "(.*)")')
def delete_product_with_name(step, stored, name):
    name = get_stored_or_store_name("product", stored, name)
    

    resid, version = get_product_resid(name)
    do_delete(world.path_products + str(resid), 
              {"originalVersionId": version})


@step(u'add environment "(.*)" to product "(.*)"')
def add_environment_foo_to_product_bar(step, environment, product):
    # this takes 2 requests.  
    #    1: get the id of this product
    #    2: add the environment to the product
    
    # fetch the product's resource identity
    product_id, version = get_product_resid(product)
    
    post_payload = {"name": "Walter's Lab"}
    
    do_post(world.path_products + str(product_id) + "/environments",
            post_payload,
            params ={"originalVersionId": version})

@step(u'remove environment "(.*)" from product "(.*)"')
def remove_environment_from_product(step, environment, product):
    # fetch the product's resource identity
    product_id, version = get_product_resid(product)
    environment_id = get_environment_resid(environment)
    
    do_delete(world.path_products + str(product_id) + "/environments/" + environment_id, 
              {"originalVersionId": version})

    
@step(u'product "(.*)" (has|does not have) environment "(.*)"')
def product_foo_has_environment_bar(step, product, haveness, env_name):
    # fetch the product's resource identity
    product_id = get_product_resid(product)[0]
    
    expect_to_find = (haveness == "has")
    search_and_verify("environment", 
                    world.path_products + str(product_id) + "/environments",
                    "",
                    "name", 
                    env_name,
                    expect_to_find)


