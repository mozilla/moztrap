'''
Created on Oct 7, 2010

@author: camerondawson
'''
from features.models import CompanyModel, ProductModel
from features.tcm_request_helper import verify_status, add_params
from lettuce import step, world
from lettuce.terrain import before, after
import cgi
import httplib
import mock_scenario_data


def save_db_state():
    '''
        This will dump the database to a file.  That file will then be used at the beginning
        of each scenario to reset to a known state of the database
    '''
    conn = httplib.HTTPConnection(world.hostname, world.port, timeout=120)
    conn.request("GET", world.path_savedb)
    conn.getresponse()

def restore_db_state():
    '''
        This will re-create the database from the dump created in save_db_state().  This will
        be run at the beginning end of each scenario to reset the database to the known state.
    '''
    conn = httplib.HTTPConnection(world.hostname, world.port, timeout=120)
    conn.request("GET", world.path_restoredb)
    response = conn.getresponse()
    verify_status(200, response, "Restored the database")

def setup_connection():
    world.conn = httplib.HTTPConnection(world.hostname, world.port)


@before.all
def setup_before_all():
    if (world.save_db):
        save_db_state()

    # usually, the test will replace the countryId based on looking it up
    world.seed_company = {"name": "Massive Dynamic",
                          "phone": "555-867-5309",
                          "address": "650 Castro St.",
                          "city": "Mountain View",
                          "zip": "94043",
                          "url": "http//www.fringepedia.net",
                          "country name": "United States"
                          }

    # usually the test setup will replace the companyId with the one looked up based on creating
    # the seed company above.
    world.seed_product = {"company name": "Massive Dynamic",
                          "name": "Cortexiphan",
                          "description": "I can see your universe from here"
                          }

    # keep track of the api(uri) calls made
    world.apis_called = {}

@before.each_scenario
def setup_before_scenario(scenario):
    # make sure the auth cookie is cleared
    world.auth_cookie = None

    # @todo: DON'T NEED?????
    # dict of names of objects used in scenarios to remember from one step to the next keyed by type such as "user"
    world.names = {}

    # the id of the last referenced item of this tcm_type
    world.latest_of_type = {}

    if (world.restore_db):
        restore_db_state()

    if (world.use_mock):
        scenarioData = mock_scenario_data.get_scenario_data(scenario.name).strip()

        headers = {'content-Type':'text/plain',
                   "Content-Length": "%d" % len(scenarioData) }

        setup_connection()
        world.conn.request("POST",
                           add_params(world.path_mockdata,
                                      {"scenario" : scenario.name}),
                            "", headers)

        world.conn.send(scenarioData)
        world.conn.getresponse()

@before.each_step
def setup_step_connection(step):
    setup_connection()

    world.current_sentence = step.sentence

@after.all
def teardown_after_all(total):
    if (world.restore_db_after_all):
        restore_db_state()

    write_apis_called_file()


def write_apis_called_file():

    f = open(world.apis_called_file, 'w')

    world.apis_called

    tablerows = ""
    # we can't sort a dict, so we need to sort the keys, then fetch the value for it
    keys = world.apis_called.keys()
    keys.sort()
    for key in keys:
        # each value is a set of the methods called (to keep them unique) so we join them by spaces
        tablerow = "<tr><td>%s</td><td>%s</td></tr>" % (key, ' '.join(world.apis_called[key]))
        tablerows += tablerow

    output = '''
            <html xmlns="http://www.w3.org/1999/xhtml">
                <head>
                    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />

                    <title>%(appUnderTest)s Results</title>
                </head>
                <body>
                    <h1>%(appUnderTest)s APIs Called</h1>
                    <table border=1>
                    <tr><th>API</th><th>Methods</th></tr>
                    %(tablerows)s
                    </table>
                </body>
            </html>
        ''' % {'tablerows': tablerows,
               'appUnderTest': cgi.escape(world.applicationUnderTest)
               }


    f.write(output)


@step(u'create the seed company and product with these names')
def create_seed_company_and_product(step):
    names = step.hashes[0]

    # create the seed company
    company = world.seed_company.copy()
    # use the value passed in, in case it's different than the default
    company["name"] = names["company name"]
    world.names["company"] = company["name"]

    #TODO: not able to search for the country name yet
    company["countryId"] = 123
    if company.has_key("country name"):
        del company["country name"]

    companyModel = CompanyModel()
    companyModel.create(company)

    # create the seed product
    # persist the last one we make.  Sometimes we will only make one.
    product = world.seed_product.copy()
    product["name"] = names["product name"]
    world.names["product"] = product["name"]

    # get the company id from the passed company name
    company_id = CompanyModel().get_resid(product["company name"])[0]
    product["companyId"] = company_id
    if product.has_key("company name"):
        del product["company name"]

    productModel = ProductModel()
    productModel.create(product)












