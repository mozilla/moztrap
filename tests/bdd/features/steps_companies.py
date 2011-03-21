'''
Created on Jan 31, 2011

@author: camerondawson
'''

from features.models import CompanyModel
from features.tcm_data_helper import get_stored_or_store_name, ns
from features.tcm_request_helper import do_post, do_delete, eq_
from lettuce import step, world


'''
######################################################################

                     COMPANY STEPS

######################################################################
'''

@step(u'fetch the company with name "(.*)" by its id')
def fetch_company_by_id(step, name):

    data = CompanyModel().get_by_name(name)
    eq_(data[ns("name")], name, "Fetch company by id")


@step(u'company with (that name|name "(.*)") (does not exist|exists)')
def check_company_foo_existence(step, stored, name, existence):
    name = get_stored_or_store_name("company", stored, name)
    CompanyModel().verify_existence_on_root(name,
                                            existence = existence)


@step(u'create a new company with name "(.*)"')
def create_a_new_company_with_name(step, company_name):
    post_payload = {"name": company_name,
                    "phone": "617-417-0593",
                    "address": "31 lakeside drive",
                    "city": "Boston",
                    "zip": "01721",
                    "url": "http//www.utest.com",
                    "countryId": 123
                    }

    companyModel = CompanyModel()
    companyModel.create(post_payload)

@step(u'create the following new companies')
def create_companies(step):
    companyModel = CompanyModel()
    for item in step.hashes:
        company = item.copy()
        # persist the last one we make.  Sometimes we will only make one.
        world.names["company"] = company["name"]

        # get the product id from the passed product name
        #country_id = get_country_resid(company["country name"])
        country_id = 123
        company["countryId"] = country_id
        del company["country name"]

        companyModel.create(company)

@step(u'search for all companies returns at least these results:')
def at_least_these_companys_exist(step):
    company_list = CompanyModel().get_all_list()

    # walk through all the expected roles and make sure it has them all
    # note, it doesn't check that ONLY these roles exist.  That should be a different
    # method.
    for company in step.hashes:
        found_company = [x for x in company_list if x[ns("name")] == company["name"]]

        assert len(found_company) == 1, "Expected to find company named %s in:\n%s" % (company["name"],
                                                                                   str(company_list))

@step(u'delete the company with (that name|name "(.*)")')
def delete_company_with_name(step, stored, name):
    companyModel = CompanyModel()
    name = companyModel.get_stored_or_store_name(stored, name)
    companyModel.delete(name)


@step(u'search all Companies')
def search_all_companies(step):
    assert False, 'This step must be implemented'

