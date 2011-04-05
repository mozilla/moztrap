'''
Created on Mar 17, 2011

@author: camerondawson
'''

from features.tcm_data_helper import jstr, ns, json_to_obj, json_pretty, \
    get_user_password, as_arrayof, eq_, verify_single_item_in_list, \
    get_stored_or_store_name, get_stored_or_store_field, compare_dicts_by_keys, \
    ns_keys, plural
from features.tcm_request_helper import get_resource_identity, get_json_headers, \
    do_get, get_auth_header, do_put_for_cookie, do_post, do_delete, do_put, \
    encode_multipart_formdata, get_form_headers
from lettuce.terrain import world

class BaseModel(object):

    def __init__(self,
                 singular,
                 plural = None,
                 root_path = None,
                 creation_key = None):
        self.singular = singular

        if plural == None:
            self.plural = singular + "s"
        else:
            self.plural = plural

        # creation key is the field name key when a new one of these is created.  it's different for
        # some objects, such as for testcase, it's testcaseversion
        if creation_key == None:
            self.creation_key = self.singular
        else:
            self.creation_key = creation_key

        if root_path == None:
            self.root_path = "%s%s" % \
                (world.api_prefix, self.plural)
        else:
            self.root_path = "%s%s" % \
                (world.api_prefix, root_path)


    def search_for_resid(self, params = {}):
        '''
            Return the id and version as a tuple

        '''

        item = self.get_single_item_from_search(self.root_path, params = params)
        assert item != None, "%s not found in search with these params:\n%s" % \
            (self.singular, jstr(params))

        return get_resource_identity(item)

    def create(self, params, headers = get_form_headers()):
        data = do_post(self.root_path, params, headers = headers)
        try:
            created_obj = json_to_obj(data)[ns(self.creation_key)][0]
        except KeyError:
            assert False, "looking for %s in:\n%s" % (self.creation_key, json_pretty(data))

        self.store_latest(created_obj)
        return created_obj


    def delete(self, name):
        resid, version = self.get_resid(name)
        do_delete("%s/%s" % (self.root_path, str(resid)),
                  {"originalVersionId": version})

    def get_resid(self, name):
        resid = self.__get_resid__({"name" : name})
        assert resid is not None, "resid came back as None"
        return resid

    def __get_resid__(self, params):
        return self.search_for_resid(params)

    def get_list_from_search(self,
                             uri,
                             tcm_type = None,
                             plural_tcm_type = None,
                             params = {},
                             headers = get_json_headers()):
        '''
            This will always return an array.  May have many, one or no items in it
            it goes into the "searchResult" tcm_type of response
        '''
        if tcm_type == None:
            tcm_type = self.singular
            plural_tcm_type = self.plural

        if plural_tcm_type == None:
            plural_tcm_type = plural(tcm_type)

        response_txt = do_get(uri, params, headers)

        sr_field = ns("searchResult")
        tcm_type = ns(tcm_type)
        pl_type = ns(plural_tcm_type)

        try:
            sr = json_to_obj(response_txt)[sr_field][0]
            if (sr[ns("totalResults")] > 0):
                items = sr[pl_type][tcm_type]
                if (not isinstance(items, list)):
                    items = [items]
            else:
                items = []

            return items
        except (KeyError, TypeError) as err:
            assert False, \
                "%s\nDidn't find [%s][0][%s][%s] in\n%s" % \
                (str(err),
                 sr_field,
                 pl_type,
                 ns(tcm_type),
                 json_pretty(response_txt))

    def get_single_item_from_search(self,
                                    uri,
                                    tcm_type = None,
                                    params = {},
                                    headers = get_json_headers()):
        '''
            This will always return a single item or None type.  May have many responses, so throw an
            error if there is more than one.
            It goes into the "searchResult" tcm_type of response

            Yeah, it's inefficient to create a list, then potentially return the first item as NOT a list.
            But this makes the coding easier and more uniform, so I chose to do that.
        '''

        list = self.get_list_from_search(uri, tcm_type, params = params, headers = headers)

        # if the last attempt to get something returned None, we want to persist that in the last_id,
        # otherwise we may think we're referencing the LAST one, but we'd be getting the one from before
        if len(list) == 0:
            self.store_latest(None)
            return None
        assert len(list) < 2,\
            '''More than one object returned from search.  Don't know which one to return.
                uri: %s
                params: %s
            %s
            '''\
            % (uri, params, jstr(list))

        item = list[0]
        self.store_latest(item)
        return item


    def get_stored_or_store_name(self, stored, name):
        return get_stored_or_store_name(self.singular, stored, name)


    def get_stored_or_store_obj(self,
                                stored,
                                name):
        '''
            If stored is not None and has the word "that" in it, then we try to use the last stored object
            of that type.  This can be tricky, because that last stored one might not have the latest verison id.
            Some step code may need to refetch the latest version.  Or perhaps we should re-fetch the latest
            version here?

            If stored IS None, then we do a search for the object of that type with that name.  For type of "users"
            we have to split the name to first and last.  Sucky special case.
        '''
        if stored == None:
            # search for the object with that name
            if self.singular == "user":
                names = name.split()
                params = {"firstName": names[0], "lastName": names[1]}
            else:
                params = {"name": name}
            tcm_obj = self.get_single_item_from_search(self.root_path, params)
            self.store_latest(tcm_obj)
        else:
            # returned the stored object
            # DO WE RE-FETCH IT TO GET THE LATEST VERSION?
            tcm_obj = self.get_latest_stored()
            tcm_obj = self.get_single_item_from_endpoint("%s/%s" % \
                                                         (self.root_path,
                                                         str(get_resource_identity(tcm_obj)[0])))
            return tcm_obj

    # simple accessors that can be changed if I change where I store these things.
    def store_latest(self, tcm_obj):
        world.latest_of_type[self.singular] = tcm_obj

    def get_latest_stored(self):
        return world.latest_of_type[self.singular]

    def get_list_from_endpoint(self,
                               uri,
                               tcm_type = None,
                               headers = get_json_headers()):
        '''
            This hits an endpoint.  It goes into the ArrayOfXXX tcm_type of response
        '''
        if tcm_type == None:
            tcm_type = self.singular

        response_txt = do_get(uri, headers = headers)

        try:
            array_of_type = json_to_obj(response_txt)[ns(as_arrayof(tcm_type))][0]
            if (len(array_of_type) > 1):
                items = array_of_type[ns(tcm_type)]
                if (not isinstance(items, list)):
                    items = [items]
            else:
                items = []

            return items
        except (KeyError, TypeError) as err:
            assert False, \
                "%s\nDidn't find [%s][0][%s] in\n%s" % \
                (str(err),
                 ns(as_arrayof(tcm_type)),
                 ns(tcm_type),
                 json_pretty(response_txt))

    def get_by_name(self, name):
        '''
            Return just a single item.  If more than one found with that name, throw assertion.
        '''
        resid = self.get_resid(name)[0]
        return self.get_by_id(resid)


    def get_by_id(self, resid):
        return self.get_single_item_from_endpoint("%s/%s" % (self.root_path, resid))


    def get_all_list(self,
                     sort_direction = None,
                     sort_field = None):
        params = {}
        if (sort_direction is not None) and (sort_field is not None):
            params = {"sortDirection": sort_direction,
                      "sortField": sort_field}

        return self.get_list_from_search(self.root_path,
                                         tcm_type = self.singular,
                                         params = params)


    '''

        #######################################
        Refactoring:  need to make these intelligently use their root_path rather than having a rui
        pased in.
        #######################################

    '''


    def get_single_item_from_endpoint(self,
                                      uri = None,
                                      tcm_type = None,
                                      headers = get_json_headers()):
        '''
            This hits an endpoint.  No searchResult or ArrayOfXXXX part here
        '''

        if uri == None:
            uri = self.root_path

        if tcm_type == None:
            tcm_type = self.singular

        response_txt = do_get(uri, headers = headers)
        tcm_obj = json_to_obj(response_txt)
        try:
            item = tcm_obj[ns(tcm_type)][0]
            self.store_latest(item)
            return item

        except KeyError:
            assert False, "%s\nDidn't find %s in %s" % (str(KeyError), ns(tcm_type), jstr(tcm_obj))


    def search_and_verify_existence(self, uri, search_args, existence):
        expect_to_find = (existence.strip() == "exists")
        self.search_and_verify(uri, search_args, expect_to_find)


    def search_and_verify(self, uri, search_args, expect_to_find, tcm_type = None):
        '''
            This does a search based on the search_args passed in.  So "expect_to_find"
            is really filtered based on those parameters.

            expect_to_find: If True, then we verify based on expecting to find something.
                            If False, this will fail if we get a resultset greater than 0.
        '''
        if tcm_type == None:
            tcm_type = self.singular

        resp_list = self.get_list_from_search(uri, params = search_args)

        if not expect_to_find:
            eq_(len(resp_list), 0, "expect result size zero:\n" + jstr(resp_list))
        else:
            # we want to verify just ONE of the items returned.  Indeed, we likely
            # expect only one.  So we pick the first item returned

            verify_single_item_in_list(resp_list,
                                       params = search_args)


    def verify_existence_on_root(self,
                                 name = None,
                                 existence = "exists",
                                 params = {}):
        '''
            the existence parameter is a string that has either "exists"
            or "does not exist" and a boolean is formed based on that in the
            delegated method call to search_and_verify_existence
        '''
        if params == {}:
            params = {"name": name}
        self.search_and_verify_existence(self.root_path,
                                         params,
                                         existence)

    def verify_found_on_root(self,
                             name = None,
                             exp_to_find = True,
                             params = {}):
        '''
            Find the object with this name in the root_path, with the
            specified search parameters.

            More generic than the verify_existence method.  It takes
            a boolean for exp_to_find
        '''
        if params == {}:
            params = {"name": name}
        self.search_and_verify(self.root_path,
                               params,
                               exp_to_find)

    def verify_has(self, uri, search_args, expect_to_find, tcm_type):
        self.search_and_verify(uri, search_args, expect_to_find, tcm_type)

class UserModel(BaseModel):
    def __init__(self):
        BaseModel.__init__(self, "user")

    def get_resid(self, name):
        names = name.split()
        return super(UserModel, self).__get_resid__({"firstName": names[0],
                                                     "lastName": names[1]})

    def get_auth_header(self, user_name):
        names = user_name.split()
        user_list = self.get_list_from_search(self.root_path,
                                              params = {"firstName": names[0], "lastName": names[1]})
        try:
            useremail = user_list[0][ns("email")]
            userpw = get_user_password(user_name)
        except KeyError:
            assert False, "%s\nDidn't find field in %s" % (str(KeyError), user_list)

        return get_auth_header(useremail, userpw)

    def log_user_in(self, name):
        headers = get_json_headers(self.get_auth_header(name))
        # log the user in

        return do_put_for_cookie("%s/login" % self.root_path,
                                 "",
                                 headers)

    def get_logged_in_user(self):
        headers = {'cookie': world.auth_cookie,
                   'Content-Type':'application/json' }

        return self.get_single_item_from_endpoint( "%s/current" % self.root_path,
                                                  headers = headers)


    def check_values(self, act_obj, exp_hash):
        '''
            Takes the actual object, one expected hash, as from the lettuce step.hashes
            and which keys to compare.
            Note:  the keys may be different from expected because of things like
            "company name" in expected, but we will get the id for that company name and
            compare the ids with the act_obj
        '''
        try:
            exp_hash["companyId"] = CompanyModel().get_resid(exp_hash["company name"])[0]
            del exp_hash["company name"]
        except KeyError:
            # we may not be checking company name, and that's ok, so just pass
            pass

        # check that the data matches
        compare_dicts_by_keys(ns_keys(exp_hash),
                              act_obj,
                              exp_hash.keys())

    def get_assignment_list(self, user_id):
        return self.get_list_from_endpoint("%s/%s/assignments" % (self.root_path, user_id),
                                           tcm_type = "assignments")

    def add_role(self, user_name, role_name):
        user_id, user_version = self.get_resid(user_name)
        role_id = RoleModel().get_resid(role_name)[0]
        do_post("%s/%s/roles/%s/" % (self.root_path, user_id, role_id),
            {"originalVersionId": user_version})

    def add_roles(self, user_name, role_hashes):

        for role in role_hashes:
            self.add_role( user_name, role["name"])


    def set_roles(self, user_name, role_ids):
        '''
            replace the users roles with these roles
        '''
        user_id, user_version = self.get_resid(user_name)
        do_put("%s/%s/roles/" % (self.root_path, user_id),
            {"originalVersionId": user_version,
             "roleIds": role_ids})

    def has_role(self, user_name, role_name):
        '''
            This doesn't use the search_and_verify.  Not sure if this is the better approach
            or not.  May need to decide on one.
        '''
        role_list = self.get_role_list(user_name)

        found_role = [x for x in role_list if x[ns("name")] == role_name]

        assert len(found_role) == 1, "Expected to find role with name %s in:\n%s" % (role_name,
                                                                                   str(role_list))

    def remove_role(self, user_name, role_name):
        # fetch the user's and the role's resource identity
        user_id, user_version = UserModel().get_resid(user_name)
        role_id_to_remove = RoleModel().get_resid(role_name)[0]

        do_delete("%s/%s/roles/%s" % (self.root_path, user_id, role_id_to_remove),
                  {"originalVersionId": user_version})


    def get_role_list(self, user_name):
        user_id = self.get_resid(user_name)[0]

        return self.get_list_from_endpoint("%s/%s/roles" % (self.root_path, user_id),
                                           "role")

    def get_permission_list(self, user_name):
        user_id = self.get_resid(user_name)[0]
        return self.get_list_from_endpoint("%s/%s/permissions"% (self.root_path, user_id),
                                           "permission")

    def activate(self, user_name):
        user_id, version = self.get_resid(user_name)
        do_put("%s/%s/activate" % (self.root_path, user_id), {"originalVersionId": version})

    def deactivate(self, user_name):
        user_id, version = self.get_resid(user_name)
        do_put("%s/%s/deactivate" % (self.root_path, user_id), {"originalVersionId": version})

class RoleModel(BaseModel):
    def __init__(self):
        super(RoleModel, self).__init__("role", root_path = "users/roles")

    def get_permissions_list(self, role_name):
        role_id = self.get_resid(role_name)[0]

        return self.get_list_from_endpoint("%s/%s/permissions" %
                                                (self.root_path,
                                                 role_id),
                                            tcm_type = "permission")

    def add_permission(self, role_id, role_version, permission_id):
        perm_uri = "%s/%s/permissions/%s/" % (self.root_path, role_id, permission_id)
        perm_payload = {"originalVersionId": role_version}
        do_post(perm_uri, perm_payload)


class PermissionModel(BaseModel):
    def __init__(self):
        super(PermissionModel, self).__init__("permission", root_path = "users/permissions")

class CompanyModel(BaseModel):
    def __init__(self):
        BaseModel.__init__(self, "company", "companies")

#        super(CompanyModel, self).__init__("company", "companies")

    def get_seed_resid(self):
        return self.get_resid(world.seed_company["name"])

class ProductModel(BaseModel):
    def __init__(self):
        super(ProductModel, self).__init__("product")

    def get_seed_resid(self):
        return self.get_resid(world.seed_product["name"])

    def verify_has_environmentgroup(self, product_name, envgrp_name, expect_to_find):
        prod_resid = self.get_resid(product_name)[0]
        uri = "%s/%s/environmentgroups" % (self.root_path,
                                           prod_resid)
        self.search_and_verify(uri,
                               {"name": envgrp_name},
                               "environmentgroup",
                               expect_to_find)

    def add_component(self, product_id, product_version, component_dict):
        params = component_dict.copy()
        params["originalVersionId"] = product_version
        do_post("%s/%s/components" % (self.root_path, product_id),
                params)

    def add_environmentgroups(self, tcm_name, envgrp_ids):
        tcm_id, version = self.get_resid(tcm_name)

        do_put("%s/%s/environmentgroups" % (self.root_path, tcm_id),
               {"environmentGroupIds": envgrp_ids,
                "originalVersionId": version})


    def get_environmentgroup_list(self, tcm_id):
        return self.get_list_from_endpoint("%s/%s/environmentgroups" % (self.root_path,
                                                                        tcm_id),
                                           "environmentgroup")

class CountryModel(BaseModel):
    def __init__(self):
        super(CountryModel, self).__init__("country", "countries")


class EnvironmentModel(BaseModel):
    def __init__(self):
        super(EnvironmentModel, self).__init__("environment")


class EnvironmenttypeModel(BaseModel):
    def __init__(self):
        super(EnvironmenttypeModel, self).__init__("environmenttype")


class EnvironmentgroupModel(BaseModel):
    def __init__(self):
        super(EnvironmentgroupModel, self).__init__("environmentgroup")

    def add_environments(self, envgrp_id, version, env_ids):
        do_put("%s/%s/environments" % (self.root_path, envgrp_id),
               {"environmentIds": env_ids,
                "originalVersionId": version})

class TagModel(BaseModel):
    def __init__(self):
        super(TagModel, self).__init__("tag")

    def get_resid(self, name):
        return super(TagModel, self).__get_resid__({"tag": name})

    def get_stored_or_store_tag(self, stored, tag):
        return get_stored_or_store_field("tag", self.singular, stored, tag)

    def delete(self, name):
        resid, version = self.get_resid(name)
        do_delete("%s/%s" % (self.root_path, str(resid)),
                  {"originalVersionId": version})










'''
    ############################################################################

            TEST OBJECT CLASSES

    ############################################################################
'''


class TestcaseModel(BaseModel):
    def __init__(self):
        super(TestcaseModel, self).__init__("testcase",
                                            creation_key = "testcaseversion")

    def get_latestversion(self, testcase_id):
        # now get the latest version for that testcase id

        latestversion_uri = "%s/%s/latestversion/" % (self.root_path, testcase_id)

        return self.get_single_item_from_endpoint(latestversion_uri,
                                                  tcm_type = "testcaseversion",)
    def get_latestversion_resid(self, testcase_id):
        return get_resource_identity(self.get_latestversion(testcase_id))

    def add_steps(self, testcaseversion_id, stepshash):
        uri = "%s/versions/%s/steps" % (self.root_path, testcaseversion_id)
        for case_step in stepshash:
            do_post(uri, case_step)


    def get_steps_list(self, testcaseversion_id):
        uri = "%s/versions/%s/steps" % (self.root_path, testcaseversion_id)
        return self.get_list_from_endpoint(uri, "testcasestep")

    def get_latest_steps_list(self, name):
        testcase_id = self.get_resid(name)[0]
        latestversion_id = self.get_latestversion_resid(testcase_id)[0]
        return self.get_steps_list(latestversion_id)

    def get_environment_list(self, testcase_id):
        return self.get_list_from_search("%s/%s/environments" % (self.root_path,
                                                          testcase_id),
                                  tcm_type = "environment")

    def get_attachment_list(self, testcase_id):
        return self.get_list_from_search("%s/%s/attachments" % (self.root_path,
                                                                testcase_id),
                                         tcm_type = "attachment")

    def upload_attachment(self, filename, testcase_obj):
        testcase_id, version = get_resource_identity(testcase_obj)

        content_type, body = encode_multipart_formdata([], [{'key': filename,
                                                             'filename': filename,
                                                             'value': open(world.testfile_dir + filename, 'rb')}])

        headers = {"Accept": "application/xml",
                   "Content-Type":content_type,
                   "Content-Length": "%d" % len(body) }

        do_post("%s/%s/attachments/upload" % (self.root_path, testcase_id),
                body,
                params = {"originalVersionId": version},
                headers = headers)

    def approve_by_user(self, testcase_name, user_name):
                # first we need the testcase id so we can get the latest version to approve
        testcase_id, version = self.get_resid(testcase_name)
        testcaseversion_id = self.get_latestversion_resid(testcase_id)[0]


        # do the approval of the testcase
        uri = "%s/versions/%s/approve/" % (self.root_path, testcaseversion_id)
        headers = get_form_headers(UserModel().get_auth_header(user_name))

        do_put(uri,
               {"originalVersionId": version},
                headers = headers)

    def activate(self, testcase_name):
        testcase_id = self.get_resid(testcase_name)[0]
        testcaseversion_id, version = self.get_latestversion_resid(testcase_id)

        do_put("%s/versions/%s/activate" % (self.root_path, testcaseversion_id),
                  {"originalVersionId": version})



class TestsuiteModel(BaseModel):
    def __init__(self):
        super(TestsuiteModel, self).__init__("testsuite")

    def activate(self, testsuite_name):
        testsuite_id, version = self.get_resid(testsuite_name)

        do_put("%s/%s/activate" % (self.root_path, testsuite_id),
                  {"originalVersionId": version})

    def add_testcase(self,
                     testsuite_name,
                     testcase_name,
                     priorityId = 1,
                     runOrder = 1,
                     blocking = "false"):
        testsuite_id, version = self.get_resid(testsuite_name)
        tcModel = TestcaseModel()

        tc_id = tcModel.get_resid(testcase_name)[0]
        tc_ver_id = tcModel.get_latestversion_resid(tc_id)[0]

        do_post("%s/%s/includedtestcases" % (self.root_path, testsuite_id),
                {"testCaseVersionId": tc_ver_id,
                 "priorityId": priorityId,
                 "runOrder": runOrder,
                 "blocking": blocking,
                 "originalVersionId": version})












'''
    ############################################################################

    These classes are runnable and contain tests.  They have
    a number of apis in common, so they have a common base-class

    ############################################################################
'''


class RunnableTestContainerBaseModel(BaseModel):
    '''
        Base class for Models that contain tests, such as Testcycles and Testruns.
        Testsuites may also use this.
    '''

    def __init__(self,
                 singular,
                 plural = None,
                 root_path = None,
                 creation_key = None):
        super(RunnableTestContainerBaseModel, self).__init__(singular, plural, root_path, creation_key)

    def activate(self, tcm_name):
        tcm_id, version = self.get_resid(tcm_name)

        do_put("%s/%s/activate" % (self.root_path, tcm_id),
                  {"originalVersionId": version})

    def get_summary_list(self, tcm_id):
        return self.get_list_from_endpoint("%s/%s/reports/coverage/resultstatus" %
                                           (self.root_path, tcm_id),
                                           tcm_type = "CategoryValueInfo")

    def approve_all_results(self, testcycle):
        tcm_id, version = get_resource_identity(testcycle)
        return do_put("%s/%s/approveallresults" % (self.root_path,
                                                 tcm_id),
                      body = {"originalVersionId": version}
                      )

    def add_environmentgroups(self, tcm_name, envgrp_ids):
        tcm_id, version = self.get_resid(tcm_name)

        do_put("%s/%s/environmentgroups" % (self.root_path, tcm_id),
               {"environmentGroupIds": envgrp_ids,
                "originalVersionId": version})

    def get_environmentgroup_list(self, tcm_id):
        return self.get_list_from_endpoint("%s/%s/environmentgroups" % (self.root_path,
                                                                        tcm_id),
                                           "environmentgroup")

    def add_team_members(self, tcm_name, user_ids):
        tcm_id, version = self.get_resid(tcm_name)

        do_put("%s/%s/team/members" % (self.root_path, tcm_id),
           {"userIds": user_ids,
            "originalVersionId": version})

    def get_team_members_list(self, tcm_id):
        return self.get_list_from_endpoint("%s/%s/team/members" % (self.root_path,
                                                                        tcm_id),
                                           "user")


class TestcycleModel(RunnableTestContainerBaseModel):
    def __init__(self):
        super(TestcycleModel, self).__init__("testcycle")

    def get_testrun_list(self, testcycle_id):
        uri = "%s/%s/testruns" % (self.root_path, testcycle_id)
        return self.get_list_from_endpoint(uri,
                                           tcm_type = "testrun")


class TestrunModel(RunnableTestContainerBaseModel):
    def __init__(self):
        super(TestrunModel, self).__init__("testrun")


    def add_testcase(self,
                     testrun_name,
                     testcase_name,
                     priorityId = 1,
                     runOrder = 1,
                     blocking = "false"):
        testrun_id, version = self.get_resid(testrun_name)
        tcModel = TestcaseModel()

        tc_id = tcModel.get_resid(testcase_name)[0]
        tc_ver_id = tcModel.get_latestversion_resid(tc_id)[0]

        do_post("%s/%s/includedtestcases" % (self.root_path, testrun_id),
                {"testCaseVersionId": tc_ver_id,
                 "priorityId": priorityId,
                 "runOrder": runOrder,
                 "blocking": blocking,
                 "originalVersionId": version})


    def get_testsuite_list(self, testrun_id):
        return self.get_list_from_endpoint("%s/%s/testsuites" % (self.root_path,
                                                         testrun_id),
                                            tcm_type = "testsuite")

    def add_testsuite(self, testrun_name, testsuite_name):
        testrun_id, version = self.get_resid(testrun_name)

        testsuite_id = TestsuiteModel().get_resid(testsuite_name)[0]

        do_post("%s/%s/includedtestcases/testsuite/%s" % (self.root_path, testrun_id, testsuite_id),
                {"originalVersionId": version})


    def get_component_list(self, testrun_id):
        return self.get_list_from_endpoint("%s/%s/components" % (self.root_path,
                                                          testrun_id))

    def get_included_testcases(self, testrun_id):
        return self.get_list_from_endpoint("%s/%s/includedtestcases" % \
                                                (self.root_path, testrun_id),
                                           tcm_type = "includedtestcase")

    def get_testcase_assignments(self, includedtestcase_id):
        return self.get_list_from_endpoint("%s/includedtestcases/%s/assignments" % \
                                                (self.root_path, includedtestcase_id),
                                           tcm_type = "testcaseassignment")

    def get_result_list(self,
                   testcase_id,
                   testrun_id = None,
                   includedtestcase_list = None,
                   tcassignment_list = None):
        '''
            I *think* this is the best way to overload the method for several possible parameters.
            trying this technique
        '''
        if tcassignment_list is None:
            # we need to get it first
            if includedtestcase_list is None:
                # we need to get it first
                if testrun_id is None:
                    assert False, "we need at least a testrun_id to fetch a result"
                includedtestcase_list = self.get_included_testcases(testrun_id)

            incl_testcase = verify_single_item_in_list(includedtestcase_list, "testCaseId", testcase_id)
            includedtestcase_id = get_resource_identity(incl_testcase)[0]
            tcassignment_list = self.get_testcase_assignments(includedtestcase_id)


        found_assignment = verify_single_item_in_list(tcassignment_list, "testCaseId", testcase_id)
        assignment_id = get_resource_identity(found_assignment)[0]
        return self.get_list_from_endpoint("%s/assignments/%s/results" % \
                                                (self.root_path, assignment_id),
                                           tcm_type = "testresult")


    def get_result(self,
                   testcase_id,
                   testrun_id = None,
                   includedtestcase_list = None,
                   tcassignment_list = None,
                   result_list = None):
        if result_list == None:
            result_list = self.get_result_list(testcase_id,
                                                 testrun_id = testrun_id,
                                                 includedtestcase_list = includedtestcase_list,
                                                 tcassignment_list = tcassignment_list)

        result = verify_single_item_in_list(result_list, "testCaseId", testcase_id)
        return result

    def search_for_results_by_result_status(self,
                                            testrun_id,
                                            status_id):

        #../testruns/results/?pageSize=20&testRunId=123&testRunResultStatusId=1

        result_list = self.get_list_from_search("%s/results" % self.root_path,
                                                tcm_type = "testresult",
                                                params = {"testRunId": testrun_id,
                                                          "testRunResultStatusId": status_id})
        return result_list


    def get_result_by_id(self, testresult_id):

        result = self.get_single_item_from_endpoint("%s/results/%s" % (self.root_path, testresult_id),
                                                    tcm_type = "testresult")
        return result

    def get_result_environments_list(self, testresult_id):
        #results/{resultId}/environments
        return self.get_list_from_endpoint("%s/results/%s/environments" % \
                                                (self.root_path, testresult_id),
                                           tcm_type = "environment")

    def approve_result(self, testrun_id, testcase_id):

        #/testruns/results/{resultId}/approve/
        result_obj = self.get_result(testcase_id, testrun_id)
        result_id, version = get_resource_identity(result_obj)
        return do_put("%s/results/%s/approve" % (self.root_path,
                                                 result_id),
                      body = {"originalVersionId": version}
                      )


    def assign_testcase(self, testrun_name, user_id, testcase_name):
        testrun_id, testrun_version = self.get_resid(testrun_name)
        testcase_id = TestcaseModel().get_resid(testcase_name)[0]

        # get the list of testcases for this testrun
        includedtestcase_list = self.get_included_testcases(testrun_id)
        # find that in the list of testcases
        includedtestcase = verify_single_item_in_list(includedtestcase_list, "testCaseId", testcase_id)

        includedtestcase_id = get_resource_identity(includedtestcase)[0]

        post_uri = "%s/includedtestcases/%s/assignments/" % (self.root_path, includedtestcase_id)
        body = {"testerId": user_id,
                "originalVersionId": testrun_version}

        do_post(post_uri, body)

    def start_testcase(self, result_obj, user_name):
        result_id, result_version = get_resource_identity(result_obj)

        # start the test
        headers = get_form_headers(UserModel().get_auth_header(user_name))
        testresult = do_put("%s/results/%s/start" % (self.root_path, result_id),
                            {"originalVersionId": result_version}, headers)
        started_result = json_to_obj(testresult)[ns("testresult")][0]
        return started_result

    # do I need a special header here?
    def set_testcase_status(self, result_id, started_result_version, user_name, status):
        status_map = {"Passed": "finishsucceed",
                      "Failed": "finishfail",
                      "Skipped": "finishskip",
                      "Invalidated": "finishinvalidate"}

        headers = get_form_headers(UserModel().get_auth_header(user_name))

        do_put("%s/results/%s/%s" % (self.root_path, result_id, status_map[status]),
               {"originalVersionId": started_result_version},
               headers = headers)

    def retest(self, testrun, only_failed = False):
        testrun_id, version = get_resource_identity(testrun)

        do_post("%s/%s/retest" % (self.root_path, testrun_id),
                body = {"originalVersionId": version,
                        "failedResultsOnly": only_failed})

    def retest_single(self, result_id, tester_id = None):
        body = None

        if tester_id is not None:
            body = {"testerId": tester_id}

        do_post("%s/results/%s/retest" % (self.root_path, result_id),
                body = body)













