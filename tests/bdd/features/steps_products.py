'''

Created on Jan 28, 2011
@author: camerondawson
'''
from features.models import CompanyModel, ProductModel, EnvironmentModel
from features.tcm_data_helper import get_stored_or_store_name
from features.tcm_request_helper import do_post, do_delete, \
    get_resource_identity, tcmpath
from lettuce import step, world


'''
######################################################################

                     PRODUCT STEPS

######################################################################
'''

@step(u'create a new product with (that name|name "(.*)")')
def create_product_with_name_foo(step, stored, name):
    name = get_stored_or_store_name("product", stored, name)

    post_payload = {"companyId": CompanyModel().get_seed_resid()[0],
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
        company_id = CompanyModel().get_resid(product["company name"])[0]
        product["companyId"] = company_id
        del product["company name"]


        do_post(world.path_products,
                product)

@step(u'product with (that name|name "(.*)") (exists|does not exist)')
def check_product_existence(step, stored, name, existence):
    productModel = ProductModel()
    name = productModel.get_stored_or_store_name(stored, name)
    productModel.verify_existence(name, existence)

@step(u'delete the product with (that name|name "(.*)")')
def delete_product_with_name(step, stored, name):
    productModel = ProductModel()
    name = productModel.get_stored_or_store_name(stored, name)

    productModel.delete(name)

@step(u'add the following components to (that product|the product with name "(.*)")')
def add_components_to_product(step, stored_product, product_name):
    productModel = ProductModel()
    product = productModel.get_stored_or_store_obj(stored_product, product_name)

    product_resid, version = productModel.get_resid(product)

    for component in step.hashes:
        productModel.add_component(product_resid, version,
                                   {"name": component["name"],
                                    "description": component["description"]})

@step(u'add environment "(.*)" to product "(.*)"')
def add_environment_foo_to_product_bar(step, environment, product):
    # this takes 2 requests.
    #    1: get the id of this product
    #    2: add the environment to the product

    # fetch the product's resource identity
    product_id, version = ProductModel().get_resid(product)

    post_payload = {"name": "Walter's Lab"}

    do_post(world.path_products + str(product_id) + "/environments",
            post_payload,
            params ={"originalVersionId": version})

@step(u'remove environment "(.*)" from product "(.*)"')
def remove_environment_from_product(step, environment, product):
    # fetch the product's resource identity
    product_id, version = ProductModel().get_resid(product)
    environment_id = EnvironmentModel().get_resid(environment)

    do_delete(world.path_products + str(product_id) + "/environments/" + environment_id,
              {"originalVersionId": version})


@step(u'product "(.*)" (has|does not have) environment "(.*)"')
def product_foo_has_environment_bar(step, product_name, haveness, env_name):
    # fetch the product's resource identity
    productModel = ProductModel()
    expect_to_find = (haveness == "has")

    productModel.verify_has_environment(product_name, env_name, expect_to_find)


