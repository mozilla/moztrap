# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from datetime import datetime
from optparse import make_option

from django.core.management.base import BaseCommand

from moztrap.model.core import models as core_models
from moztrap.model.environments import models as env_models


class Command(BaseCommand):
    help = 'Deletes old test data'
    option_list = BaseCommand.option_list + (
        make_option('--permanent',
                    action='store_true',
                    dest='permanent',
                    default=True,
                    help='Permanently delete records?'),)

    def handle(self, *args, **options):
        for model in (core_models.Product,
                      env_models.Category,
                      env_models.Element,
                      env_models.Profile):
            obj_type = model._meta.object_name
            objects_to_delete = model.everything.filter(name__startswith='Test %s ' % obj_type)
            obj_count = objects_to_delete.count()
            objects_to_delete.delete(permanent=options['permanent'])
            self.stdout.write('%s: %s test %s object(s) deleted\n' %
                              (datetime.now().isoformat(), obj_count, obj_type))
