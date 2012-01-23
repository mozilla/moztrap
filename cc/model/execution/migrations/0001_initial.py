# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Run'
        db.create_table('execution_run', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 1, 12, 3, 59, 14, 141073))),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User'])),
            ('modified_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 1, 12, 3, 59, 14, 141289))),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User'])),
            ('deleted_on', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('deleted_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User'])),
            ('has_team', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('productversion', self.gf('django.db.models.fields.related.ForeignKey')(related_name='runs', to=orm['core.ProductVersion'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='draft', max_length=30, db_index=True)),
            ('start', self.gf('django.db.models.fields.DateField')(default=datetime.date.today)),
            ('end', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal('execution', ['Run'])

        # Adding M2M table for field own_team on 'Run'
        db.create_table('execution_run_own_team', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('run', models.ForeignKey(orm['execution.run'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('execution_run_own_team', ['run_id', 'user_id'])

        # Adding M2M table for field environments on 'Run'
        db.create_table('execution_run_environments', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('run', models.ForeignKey(orm['execution.run'], null=False)),
            ('environment', models.ForeignKey(orm['environments.environment'], null=False))
        ))
        db.create_unique('execution_run_environments', ['run_id', 'environment_id'])

        # Adding model 'RunCaseVersion'
        db.create_table('execution_runcaseversion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 1, 12, 3, 59, 14, 143138))),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User'])),
            ('modified_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 1, 12, 3, 59, 14, 143330))),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User'])),
            ('deleted_on', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('deleted_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User'])),
            ('run', self.gf('django.db.models.fields.related.ForeignKey')(related_name='runcaseversions', to=orm['execution.Run'])),
            ('caseversion', self.gf('django.db.models.fields.related.ForeignKey')(related_name='runcaseversions', to=orm['library.CaseVersion'])),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
        ))
        db.send_create_signal('execution', ['RunCaseVersion'])

        # Adding M2M table for field environments on 'RunCaseVersion'
        db.create_table('execution_runcaseversion_environments', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('runcaseversion', models.ForeignKey(orm['execution.runcaseversion'], null=False)),
            ('environment', models.ForeignKey(orm['environments.environment'], null=False))
        ))
        db.create_unique('execution_runcaseversion_environments', ['runcaseversion_id', 'environment_id'])

        # Adding model 'RunSuite'
        db.create_table('execution_runsuite', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 1, 12, 3, 59, 14, 147198))),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User'])),
            ('modified_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 1, 12, 3, 59, 14, 147385))),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User'])),
            ('deleted_on', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('deleted_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User'])),
            ('run', self.gf('django.db.models.fields.related.ForeignKey')(related_name='runsuites', to=orm['execution.Run'])),
            ('suite', self.gf('django.db.models.fields.related.ForeignKey')(related_name='runsuites', to=orm['library.Suite'])),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
        ))
        db.send_create_signal('execution', ['RunSuite'])

        # Adding model 'Result'
        db.create_table('execution_result', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 1, 12, 3, 59, 14, 152497))),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User'])),
            ('modified_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 1, 12, 3, 59, 14, 152716))),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User'])),
            ('deleted_on', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('deleted_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User'])),
            ('tester', self.gf('django.db.models.fields.related.ForeignKey')(related_name='results', to=orm['auth.User'])),
            ('runcaseversion', self.gf('django.db.models.fields.related.ForeignKey')(related_name='results', to=orm['execution.RunCaseVersion'])),
            ('environment', self.gf('django.db.models.fields.related.ForeignKey')(related_name='results', to=orm['environments.Environment'])),
            ('status', self.gf('django.db.models.fields.CharField')(default='assigned', max_length=50, db_index=True)),
            ('started', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 1, 12, 3, 59, 14, 153516))),
            ('completed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('comment', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('review', self.gf('django.db.models.fields.CharField')(default='pending', max_length=50, db_index=True)),
            ('reviewed_on', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('reviewed_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='reviews', null=True, to=orm['auth.User'])),
        ))
        db.send_create_signal('execution', ['Result'])

        # Adding model 'StepResult'
        db.create_table('execution_stepresult', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 1, 12, 3, 59, 14, 148564))),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User'])),
            ('modified_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 1, 12, 3, 59, 14, 148756))),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User'])),
            ('deleted_on', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('deleted_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User'])),
            ('result', self.gf('django.db.models.fields.related.ForeignKey')(related_name='stepresults', to=orm['execution.Result'])),
            ('step', self.gf('django.db.models.fields.related.ForeignKey')(related_name='stepresults', to=orm['library.CaseStep'])),
            ('status', self.gf('django.db.models.fields.CharField')(default='passed', max_length=50, db_index=True)),
            ('bug_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
        ))
        db.send_create_signal('execution', ['StepResult'])


    def backwards(self, orm):
        
        # Deleting model 'Run'
        db.delete_table('execution_run')

        # Removing M2M table for field own_team on 'Run'
        db.delete_table('execution_run_own_team')

        # Removing M2M table for field environments on 'Run'
        db.delete_table('execution_run_environments')

        # Deleting model 'RunCaseVersion'
        db.delete_table('execution_runcaseversion')

        # Removing M2M table for field environments on 'RunCaseVersion'
        db.delete_table('execution_runcaseversion_environments')

        # Deleting model 'RunSuite'
        db.delete_table('execution_runsuite')

        # Deleting model 'Result'
        db.delete_table('execution_result')

        # Deleting model 'StepResult'
        db.delete_table('execution_stepresult')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.product': {
            'Meta': {'object_name': 'Product'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 1, 12, 3, 59, 14, 176926)'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'deleted_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 1, 12, 3, 59, 14, 177145)'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'team': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'core.productversion': {
            'Meta': {'ordering': "['order']", 'unique_together': "[('product', 'version')]", 'object_name': 'ProductVersion'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 1, 12, 3, 59, 14, 187545)'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'deleted_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'environments': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'productversion'", 'symmetrical': 'False', 'to': "orm['environments.Environment']"}),
            'has_team': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 1, 12, 3, 59, 14, 187756)'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'own_team': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False', 'blank': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'versions'", 'to': "orm['core.Product']"}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'environments.category': {
            'Meta': {'object_name': 'Category'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 1, 12, 3, 59, 14, 181818)'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'deleted_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 1, 12, 3, 59, 14, 182028)'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'environments.element': {
            'Meta': {'object_name': 'Element'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'elements'", 'to': "orm['environments.Category']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 1, 12, 3, 59, 14, 189106)'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'deleted_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 1, 12, 3, 59, 14, 189320)'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'environments.environment': {
            'Meta': {'object_name': 'Environment'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 1, 12, 3, 59, 14, 186510)'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'deleted_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'elements': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['environments.Element']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 1, 12, 3, 59, 14, 186722)'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'environments'", 'null': 'True', 'to': "orm['environments.Profile']"})
        },
        'environments.profile': {
            'Meta': {'object_name': 'Profile'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 1, 12, 3, 59, 14, 185623)'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'deleted_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 1, 12, 3, 59, 14, 185834)'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'execution.result': {
            'Meta': {'object_name': 'Result'},
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'completed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 1, 12, 3, 59, 14, 182697)'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'deleted_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'environment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'results'", 'to': "orm['environments.Environment']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 1, 12, 3, 59, 14, 182905)'}),
            'review': ('django.db.models.fields.CharField', [], {'default': "'pending'", 'max_length': '50', 'db_index': 'True'}),
            'reviewed_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'reviews'", 'null': 'True', 'to': "orm['auth.User']"}),
            'reviewed_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'runcaseversion': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'results'", 'to': "orm['execution.RunCaseVersion']"}),
            'started': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 1, 12, 3, 59, 14, 183713)'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'assigned'", 'max_length': '50', 'db_index': 'True'}),
            'tester': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'results'", 'to': "orm['auth.User']"})
        },
        'execution.run': {
            'Meta': {'object_name': 'Run'},
            'caseversions': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'runs'", 'symmetrical': 'False', 'through': "orm['execution.RunCaseVersion']", 'to': "orm['library.CaseVersion']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 1, 12, 3, 59, 14, 171517)'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'deleted_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'end': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'environments': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'run'", 'symmetrical': 'False', 'to': "orm['environments.Environment']"}),
            'has_team': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 1, 12, 3, 59, 14, 171748)'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'own_team': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False', 'blank': 'True'}),
            'productversion': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'runs'", 'to': "orm['core.ProductVersion']"}),
            'start': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'draft'", 'max_length': '30', 'db_index': 'True'}),
            'suites': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'runs'", 'symmetrical': 'False', 'through': "orm['execution.RunSuite']", 'to': "orm['library.Suite']"})
        },
        'execution.runcaseversion': {
            'Meta': {'ordering': "['order']", 'object_name': 'RunCaseVersion'},
            'caseversion': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'runcaseversions'", 'to': "orm['library.CaseVersion']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 1, 12, 3, 59, 14, 173465)'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'deleted_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'environments': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'runcaseversions'", 'symmetrical': 'False', 'to': "orm['environments.Environment']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 1, 12, 3, 59, 14, 173681)'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'run': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'runcaseversions'", 'to': "orm['execution.Run']"})
        },
        'execution.runsuite': {
            'Meta': {'ordering': "['order']", 'object_name': 'RunSuite'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 1, 12, 3, 59, 14, 178056)'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'deleted_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 1, 12, 3, 59, 14, 178275)'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'run': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'runsuites'", 'to': "orm['execution.Run']"}),
            'suite': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'runsuites'", 'to': "orm['library.Suite']"})
        },
        'execution.stepresult': {
            'Meta': {'object_name': 'StepResult'},
            'bug_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 1, 12, 3, 59, 14, 179573)'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'deleted_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 1, 12, 3, 59, 14, 179795)'}),
            'result': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stepresults'", 'to': "orm['execution.Result']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'passed'", 'max_length': '50', 'db_index': 'True'}),
            'step': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stepresults'", 'to': "orm['library.CaseStep']"})
        },
        'library.case': {
            'Meta': {'object_name': 'Case'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 1, 12, 3, 59, 14, 191296)'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'deleted_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 1, 12, 3, 59, 14, 191508)'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cases'", 'to': "orm['core.Product']"})
        },
        'library.casestep': {
            'Meta': {'ordering': "['caseversion', 'number']", 'unique_together': "[('caseversion', 'number')]", 'object_name': 'CaseStep'},
            'caseversion': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'steps'", 'to': "orm['library.CaseVersion']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 1, 12, 3, 59, 14, 190098)'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'deleted_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'expected': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instruction': ('django.db.models.fields.TextField', [], {}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 1, 12, 3, 59, 14, 190307)'}),
            'number': ('django.db.models.fields.IntegerField', [], {})
        },
        'library.caseversion': {
            'Meta': {'ordering': "['number']", 'object_name': 'CaseVersion'},
            'case': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'versions'", 'to': "orm['library.Case']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 1, 12, 3, 59, 14, 174702)'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'deleted_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'environments': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'caseversion'", 'symmetrical': 'False', 'to': "orm['environments.Environment']"}),
            'envs_narrowed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latest': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 1, 12, 3, 59, 14, 174914)'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'number': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'productversion': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'caseversions'", 'to': "orm['core.ProductVersion']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'draft'", 'max_length': '30', 'db_index': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['tags.Tag']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'library.suite': {
            'Meta': {'object_name': 'Suite'},
            'cases': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'suites'", 'symmetrical': 'False', 'through': "orm['library.SuiteCase']", 'to': "orm['library.Case']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 1, 12, 3, 59, 14, 193505)'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'deleted_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 1, 12, 3, 59, 14, 193721)'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'suites'", 'to': "orm['core.Product']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'draft'", 'max_length': '30', 'db_index': 'True'})
        },
        'library.suitecase': {
            'Meta': {'ordering': "['order']", 'object_name': 'SuiteCase'},
            'case': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'suitecases'", 'to': "orm['library.Case']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 1, 12, 3, 59, 14, 184514)'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'deleted_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 1, 12, 3, 59, 14, 184725)'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'suite': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'suitecases'", 'to': "orm['library.Suite']"})
        },
        'tags.tag': {
            'Meta': {'object_name': 'Tag'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 1, 12, 3, 59, 14, 180824)'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'deleted_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 1, 12, 3, 59, 14, 181039)'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Product']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['execution']
