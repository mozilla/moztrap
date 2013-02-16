"""Importer for suites and cases from a dictionary."""

import json

from django.db import transaction

from ..core.auth import User
from ..tags.models import Tag
from .models import Case, CaseVersion, CaseStep, Suite, SuiteCase



class Importer(object):
    """
    Importer for Suites and Cases.

    The "suites" or "cases" sections are optional.
    The object should be structured like this::

        {
            "suites": [
                {
                    "name": "suite1 name",
                    "description": "suite description"
                },
            ],
            "cases": [
                {
                    "name": "case title",
                    "description": "case description",
                    "tags": ["tag1", "tag2", "tag3"],
                    "suites": ["suite1 name", "suite2 name", "suite3 name"],
                    "created_by": "cdawson@mozilla.com"
                    "steps": [
                        {
                            "instruction": "instruction text",
                            "expected": "expected text"
                        },
                    ]
                }
            ]
        }

    Instantiate an ``Importer`` and call its ``import_data`` method::

        importer = Importer()
        import_result = importer.import_data(productversion, case_data)

    Returned value will be an ``ImportResult`` object with the following
    attributes:

    * cases: the number of cases imported
    * suites: the number of suites imported
    * warnings: list of warnings about the imported items, if any.

    """

    @transaction.commit_on_success
    def import_data(self, productversion, case_data, force_dupes=False):
        """
        Import the top-level dictionary of cases and suites.

        Return an object that has the number of imported and skipped items.

        Keyword arguments:

        * productversion -- The ProductVersion model object for which case_data
          will be imported
        * case_data -- a dictionary of cases and/or suites to be imported
        * force_dupes -- if True, will import cases with duplicate names.  If
          False, they will be skipped.

        """

        # the result object used to keep track of import status
        result = ImportResult()

        # importer for suites.
        suite_importer = None
        if "suites" in case_data:
            suite_importer = SuiteImporter(productversion.product)
            suite_importer.add_dicts(case_data["suites"])


        # no reason why the data couldn't include ONLY suites.  So function
        # gracefully if no cases.
        if "cases" in case_data:
            case_importer = CaseImporter(productversion, suite_importer)
            result.append(case_importer.import_cases(
                case_data["cases"],
                force_dupes=force_dupes))

        # now create the suites and add cases to them
        if suite_importer:
            result.append(suite_importer.import_suites())

        return result



class CaseImporter(object):
    """Imports cases and links to or creates associated tags, suites."""

    def __init__(self, productversion, suite_importer=None):
        """
        Construct a CaseImporter

        Keyword arguments:

        * productversion -- ProductVersion.  This is the productversion
          to which these cases apply.
        * suite_importer -- A SuiteImporter class to handle any suites listed
          for each case.  If None, or default, this class will create
          an empty one.

        Also create a TagImporter for importing tags and a UserCache to
        speed the lookup of User objects to match emails for case ownership.

        """

        self.productversion = productversion
        self.suite_importer = (
            suite_importer or SuiteImporter(productversion.product)
            )

        # the object responsible for importing tags
        self.tag_importer = TagImporter(self.productversion.product)

        # cache of user emails
        self.user_cache = UserCache()

    def import_cases(self, case_dict_list, force_dupes=False):
        """
        Import the test cases in the data.

        This may include suites and tags that each case belongs to.  If a case
        has no name, it will be skipped.  If a case has no steps, it will
        be imported, but a warning will be given.  All fields are optional
        with the exception of a name.

        Case data should be in this format::

            [
                {
                    "name": "case title",
                    "description": "case description",
                    "tags": ["tag1", "tag2", "tag3"],
                    "suites": ["suite1 name", "suite2 name", "suite3 name"],
                    "created_by": "cdawson@mozilla.com"
                    "steps": [
                        {
                            "instruction": "insruction text",
                            "expected": "expected text"
                        },
                    ]
                }
            ]


        """

        result = ImportResult()

        for new_case in case_dict_list:

            if not "name" in new_case:
                result.warn(
                    ImportResult.SKIP_CASE_NO_NAME,
                    new_case,
                    )
                continue

            # Don't re-import if we have the same case name and Product Version
            if not force_dupes and CaseVersion.objects.filter(
                name=new_case["name"],
                productversion=self.productversion,
                ).exists():

                result.warn(
                    ImportResult.SKIP_CASE_NAME_CONFLICT,
                    new_case,
                    )

                continue

            user = None
            if "created_by" in new_case:
                try:
                    email = new_case["created_by"]
                    user = self.user_cache.get_user(email)

                except User.DoesNotExist:
                    result.warn(
                        ImportResult.WARN_USER_NOT_FOUND,
                        email,
                        )

            # the case looks good so far, but there may be a problem with
            # one of the steps.  So, create a savepoint in case something
            # is inherently wrong with this case, we can roll back to skip
            # it, and still import the rest of the cases.
            sid = transaction.savepoint()

            # create the top-level case object which holds the versions
            case = Case.objects.create(
                product=self.productversion.product,
                idprefix=new_case.get("idprefix", ""),
                )

            # create the case version which holds the details
            caseversion = CaseVersion.objects.create(
                productversion=self.productversion,
                case=case,
                name=new_case["name"],
                description=new_case.get("description", ""),
                user=user,
                )

            # add the steps to this case version
            if "steps" in new_case:
                try:
                    self.import_steps(caseversion, new_case["steps"])
                except ValueError as e:
                    result.warn(
                        e.args[0],
                        new_case,
                        )

                    transaction.savepoint_rollback(sid)
                    continue
            else:
                result.warn(
                    ImportResult.WARN_NO_STEPS,
                    caseversion,
                    )

            if "tags" in new_case:
                self.tag_importer.add_names(caseversion, new_case["tags"])

            if "suites" in new_case:
                self.suite_importer.add_names(case, new_case["suites"])

            # case has been created, increment our count for reporting
            result.num_cases += 1

            # this case went ok.  We'll save it as complete in the overall
            # transaction.
            transaction.savepoint_commit(sid)

            # now create the tags and add case versions to them
            self.tag_importer.import_tags()

            # now create the suites and add cases to them
            result.append(self.suite_importer.import_suites())

        return result


    def import_steps(self, caseversion, step_data):
        """
        Add the steps to this case version.

        Keyword arguments:

        * caseversion -- the CaseVersion object that step_data applies to
        * step_data -- a dictionary containing the steps for the case

        Instruction is a required field for a step, but expected is optional.

        """

        for step_num, new_step in enumerate(step_data):
            try:
                casestep = CaseStep.objects.create(
                    caseversion=caseversion,
                    number=step_num + 1,
                    instruction=new_step["instruction"],
                    expected=new_step.get("expected", ""),
                    )
            except KeyError:
                raise ValueError(ImportResult.SKIP_STEP_NO_INSTRUCTION)



class UserCache(object):
    """
    Cache of emails to User objects.

    If an email was searched for, but no matching User object was found,
    then cache None so we don't keep looking for it.

    """

    def __init__(self):
        """Create a UserCache with an internal dictionary cache."""

        self.cache = {}


    def get_user(self, email):
        """
        Return the user object that matches the email in the case, if any.

        Keyword arguments:

        * email -- a string containing an email address
        * result -- an ImportResult object to post results to

        If the email is already in the cache, then return that user.
        If this method had already searched for the user and not found it,
        then it will thrown an exception once.  In that case, it will save
        the user of None in the cache and subsequent calls for that user
        will return None.

        """

        if email in self.cache:
            return self.cache[email]

        else:
            try:
                user = User.objects.get(email=email)
                self.cache[email] = user

            except User.DoesNotExist as e:
                self.cache[email] = None
                raise e

        return self.cache[email]



class TagImporter(object):
    """
    Imports suites based on lists and dicts of suites used to build it.

    """

    def __init__(self, product):
        """Store the Product, and create the internal map."""

        self.product = product
        self.map = {}


    def add_names(self, caseversion, tag_names):
        """
        Add a simple list of tag names.

        Keyword arguments:

        * caseversion -- the CaseVersion object that tag_names applies to
        * tag_names -- a list of strings containing the names of the tags
          to be applied to the caseversion (and created if necessary)

        """

        for tag_name in tag_names:
            caseversions = self.map.setdefault(tag_name, [])
            caseversions.append(caseversion)


    def import_tags(self):
        """
        Import all added tags.

        Check for existing tags to prevent creating a global tag with the same
        name as a product tag, and vice versa.

        Use or create tags in this order of priority:

            * use existing product tag
            * use existing global tag
            * create new product tag

        """

        for tag_name, caseversions in self.map.items():
            existing_tags = Tag.objects.filter(
                name=tag_name,
                product__in=[None, self.product],
                ).order_by("-product")

            # If there is a product tag, it will be sorted to first.
            # If not, then the only item will be the global one, so
            # use that.
            if list(existing_tags):
                tag = existing_tags[0]

            else:
                tag = Tag.objects.create(
                    name=tag_name,
                    product=self.product,
                    )

            tag.caseversions.add(*caseversions)

        # we have imported these items.  clear them out now.
        self.map.clear()



class SuiteImporter(object):
    """
    Imports suites based on lists and dicts of suites used to build it.

    The internal dict looks like this::

        {
            "suitename": {
                "description": "foo",
                "cases": [case1, case2]
            }
        }

    """

    def __init__(self, product):
        """
        Construct a SuiteImporter

        Store the Product, and create the internal map.  Also create a
        result object to keep track of any issues with adding and importing
        as we go.

        """

        self.product = product
        self.map = {}
        self.result = ImportResult()


    def add_names(self, case, suite_names):
        """
        Add a simple list of Suite names.

        Keyword arguments:

        * case -- the Case object that suite_names applies to
        * suite_names -- a list of strings.  These are the names of the
          suites to be applied to this case.  Suites will be created if
          they do not yet exist.

        """

        for suite_name in suite_names:
            suite = self.map.setdefault(suite_name, {})
            cases = suite.setdefault("cases", [])
            cases.append(case)


    def add_dicts(self, suite_dicts):
        """
        Add a list of suite dictionaries.

        Keyword arguments:

        * suite_dicts -- a list of dictionaries that represent suites
          to be imported

        The list should look like this::

            [
                {
                    "name": "suite1 name"
                    "description": "suite description",
                },
                {
                    "name": "suite2 name"
                    "description": "suite description",
                },
            ]

        Suites without names will be skipped.

        """

        for suite_dict in suite_dicts:
            try:
                suite = self.map.setdefault(suite_dict["name"], {})
                suite.setdefault(
                    "description",
                    suite_dict.get("description", ""),
                    )

            except KeyError:
                self.result.warn(
                    ImportResult.SKIP_SUITE_NO_NAME,
                    suite_dict,
                    )


    def import_suites(self):
        """Import all mapped suites."""

        for suite_name, suite_data in self.map.items():

            suite, created = Suite.objects.get_or_create(
                name=suite_name,
                product=self.product,
                defaults={"description": suite_data.get("description", "")},
                )

            if created:
                self.result.num_suites += 1

            # now add any cases the suite may have specified
            if "cases" in suite_data:
                for case in suite_data["cases"]:
                    SuiteCase.objects.create(case=case, suite=suite)

        # we have imported (or warned on) these items, so reset map.
        self.map.clear()

        return self.result



class ImportResult(object):
    """
    Results of the import process.

    This may be for a small part of the process, or the process as a whole.
    ImportResults can be merged with the append() method.

    """

    SKIP_SUITE_NO_NAME = "Skipped: Name field required for Suite"
    SKIP_CASE_NO_NAME = "Skipped: Name field required for Case"
    SKIP_STEP_NO_INSTRUCTION = "Skipped: Instruction field required for Step"
    SKIP_CASE_NAME_CONFLICT = ("Skipped: Case with this name already exists "
        "for this product")
    WARN_NO_STEPS = "Warning: Case has no steps"
    WARN_USER_NOT_FOUND = "Warning: user with this email does not exist."

    def __init__(self):
        """
        Construct an ImportResult to keep track of import status.

        num_cases -- number of cases imported
        num_suites -- number of suites imported
        warnings -- general warnings, and skipped items

        """

        # the total number of test cases that were imported
        self.num_cases = 0
        self.num_suites = 0
        self.warnings = []


    def warn(self, reason, item):
        """
        Add a warning to the result.

        Keyword arguments:

        * reason -- The string constant that describes the warning
        * item -- The object (dict or model object) that the warning is about.

        """

        self.warnings.append({"reason": reason, "item": item})


    def append(self, result):
        """Append the results object into this results object."""

        self.num_cases += result.num_cases
        self.num_suites += result.num_suites
        self.warnings.extend(result.warnings)


    def get_as_list(self):
        """
        Return a list of the statuses from the import.

        List items will look like::

            Warning: Case has no steps: case title3
            Skipped: Instruction field required for Step: {u'suites': ...
            Skipped: Name field required for Case: {u'suites': ...
            Imported 3 cases
            Imported 4 suites

        """

        result_list = [
            "{0}: {1}".format(x["reason"], json.dumps(x["item"], indent=4))
            for x in self.warnings
            ]

        result_list.append("Imported {0} cases".format(self.num_cases))
        result_list.append("Imported {0} suites".format(self.num_suites))
        return result_list
