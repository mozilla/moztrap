# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Cycle'
        db.create_table('execution_cycle', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 12, 19, 21, 7, 18, 140406))),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User'])),
            ('modified_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 12, 19, 21, 7, 18, 140588))),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User'])),
            ('deleted_on', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('deleted_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User'])),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(related_name='cycles', to=orm['core.Product'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='draft', max_length=30, db_index=True)),
            ('start', self.gf('django.db.models.fields.DateField')(default=datetime.date.today)),
            ('end', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal('execution', ['Cycle'])

        # Adding model 'Run'
        db.create_table('execution_run', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 12, 19, 21, 7, 18, 143906))),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User'])),
            ('modified_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 12, 19, 21, 7, 18, 144116))),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User'])),
            ('deleted_on', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('deleted_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User'])),
            ('cycle', self.gf('django.db.models.fields.related.ForeignKey')(related_name='runs', to=orm['execution.Cycle'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='draft', max_length=30, db_index=True)),
            ('start', self.gf('django.db.models.fields.DateField')(default=datetime.date.today)),
            ('end', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal('execution', ['Run'])

        # Adding model 'RunCaseVersion'
        db.create_table('execution_runcaseversion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 12, 19, 21, 7, 18, 129033))),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User'])),
            ('modified_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 12, 19, 21, 7, 18, 129239))),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User'])),
            ('deleted_on', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('deleted_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User'])),
            ('run', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['execution.Run'])),
            ('caseversion', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['library.CaseVersion'])),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
        ))
        db.send_create_signal('execution', ['RunCaseVersion'])

        # Adding model 'RunSuite'
        db.create_table('execution_runsuite', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 12, 19, 21, 7, 18, 133310))),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User'])),
            ('modified_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 12, 19, 21, 7, 18, 133499))),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User'])),
            ('deleted_on', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('deleted_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User'])),
            ('run', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['execution.Run'])),
            ('suite', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['library.Suite'])),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
        ))
        db.send_create_signal('execution', ['RunSuite'])

        # Adding model 'Result'
        db.create_table('execution_result', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 12, 19, 21, 7, 18, 130011))),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User'])),
            ('modified_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 12, 19, 21, 7, 18, 130197))),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User'])),
            ('deleted_on', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('deleted_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User'])),
            ('tester', self.gf('django.db.models.fields.related.ForeignKey')(related_name='results', to=orm['auth.User'])),
            ('runcaseversion', self.gf('django.db.models.fields.related.ForeignKey')(related_name='results', to=orm['execution.RunCaseVersion'])),
            ('environment', self.gf('django.db.models.fields.related.ForeignKey')(related_name='results', to=orm['environments.Environment'])),
            ('status', self.gf('django.db.models.fields.CharField')(default='started', max_length=50, db_index=True)),
            ('started', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 12, 19, 21, 7, 18, 130895))),
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
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 12, 19, 21, 7, 18, 139467))),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User'])),
            ('modified_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 12, 19, 21, 7, 18, 139649))),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User'])),
            ('deleted_on', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('deleted_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User'])),
            ('result', self.gf('django.db.models.fields.related.ForeignKey')(related_name='stepresults', to=orm['execution.Result'])),
            ('step', self.gf('django.db.models.fields.related.ForeignKey')(related_name='stepresults', to=orm['library.CaseStep'])),
            ('status', self.gf('django.db.models.fields.CharField')(default='passed', max_length=50, db_index=True)),
        ))
        db.send_create_signal('execution', ['StepResult'])


    def backwards(self, orm):
        
        # Deleting model 'Cycle'
        db.delete_table('execution_cycle')

        # Deleting model 'Run'
        db.delete_table('execution_run')

        # Deleting model 'RunCaseVersion'
        db.delete_table('execution_runcaseversion')

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
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 19, 21, 7, 18, 164690)'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'deleted_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 19, 21, 7, 18, 165003)'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'environments.category': {
            'Meta': {'object_name': 'Category'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 19, 21, 7, 18, 167559)'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'deleted_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 19, 21, 7, 18, 167758)'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'environments.element': {
            'Meta': {'object_name': 'Element'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'elements'", 'to': "orm['environments.Category']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 19, 21, 7, 18, 174598)'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'deleted_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 19, 21, 7, 18, 174796)'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'environments.environment': {
            'Meta': {'object_name': 'Environment'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 19, 21, 7, 18, 165740)'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'deleted_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'elements': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['environments.Element']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 19, 21, 7, 18, 165940)'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'environments'", 'to': "orm['environments.Profile']"})
        },
        'environments.profile': {
            'Meta': {'object_name': 'Profile'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 19, 21, 7, 18, 166721)'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'deleted_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 19, 21, 7, 18, 166923)'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'execution.cycle': {
            'Meta': {'object_name': 'Cycle'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 19, 21, 7, 18, 169479)'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'deleted_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'end': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 19, 21, 7, 18, 169682)'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cycles'", 'to': "orm['core.Product']"}),
            'start': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'draft'", 'max_length': '30', 'db_index': 'True'})
        },
        'execution.result': {
            'Meta': {'object_name': 'Result'},
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'completed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 19, 21, 7, 18, 157830)'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'deleted_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'environment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'results'", 'to': "orm['environments.Environment']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 19, 21, 7, 18, 158032)'}),
            'review': ('django.db.models.fields.CharField', [], {'default': "'pending'", 'max_length': '50', 'db_index': 'True'}),
            'reviewed_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'reviews'", 'null': 'True', 'to': "orm['auth.User']"}),
            'reviewed_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'runcaseversion': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'results'", 'to': "orm['execution.RunCaseVersion']"}),
            'started': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 19, 21, 7, 18, 158811)'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'started'", 'max_length': '50', 'db_index': 'True'}),
            'tester': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'results'", 'to': "orm['auth.User']"})
        },
        'execution.run': {
            'Meta': {'object_name': 'Run'},
            'caseversions': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'runs'", 'symmetrical': 'False', 'through': "orm['execution.RunCaseVersion']", 'to': "orm['library.CaseVersion']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 19, 21, 7, 18, 173088)'}),
            'cycle': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'runs'", 'to': "orm['execution.Cycle']"}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'deleted_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'end': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 19, 21, 7, 18, 173289)'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'start': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'draft'", 'max_length': '30', 'db_index': 'True'}),
            'suites': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'runs'", 'symmetrical': 'False', 'through': "orm['execution.RunSuite']", 'to': "orm['library.Suite']"})
        },
        'execution.runcaseversion': {
            'Meta': {'object_name': 'RunCaseVersion'},
            'caseversion': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['library.CaseVersion']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 19, 21, 7, 18, 156743)'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'deleted_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 19, 21, 7, 18, 156959)'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'run': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['execution.Run']"})
        },
        'execution.runsuite': {
            'Meta': {'object_name': 'RunSuite'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 19, 21, 7, 18, 161414)'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'deleted_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 19, 21, 7, 18, 161614)'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'run': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['execution.Run']"}),
            'suite': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['library.Suite']"})
        },
        'execution.stepresult': {
            'Meta': {'object_name': 'StepResult'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 19, 21, 7, 18, 168386)'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'deleted_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 19, 21, 7, 18, 168591)'}),
            'result': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stepresults'", 'to': "orm['execution.Result']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'passed'", 'max_length': '50', 'db_index': 'True'}),
            'step': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stepresults'", 'to': "orm['library.CaseStep']"})
        },
        'library.case': {
            'Meta': {'object_name': 'Case'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 19, 21, 7, 18, 162481)'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'deleted_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 19, 21, 7, 18, 162682)'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cases'", 'to': "orm['core.Product']"})
        },
        'library.casestep': {
            'Meta': {'ordering': "['number']", 'object_name': 'CaseStep'},
            'caseversion': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'steps'", 'to': "orm['library.CaseVersion']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 19, 21, 7, 18, 160295)'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'deleted_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'expected': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instruction': ('django.db.models.fields.TextField', [], {}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 19, 21, 7, 18, 160507)'}),
            'number': ('django.db.models.fields.IntegerField', [], {'unique': 'True'})
        },
        'library.caseversion': {
            'Meta': {'ordering': "['number']", 'object_name': 'CaseVersion'},
            'case': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'versions'", 'to': "orm['library.Case']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 19, 21, 7, 18, 175540)'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'deleted_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latest': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 19, 21, 7, 18, 175746)'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'number': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'draft'", 'max_length': '30', 'db_index': 'True'})
        },
        'library.suite': {
            'Meta': {'object_name': 'Suite'},
            'cases': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'suites'", 'symmetrical': 'False', 'through': "orm['library.SuiteCase']", 'to': "orm['library.Case']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 19, 21, 7, 18, 163337)'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'deleted_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 19, 21, 7, 18, 163537)'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'suites'", 'to': "orm['core.Product']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'draft'", 'max_length': '30', 'db_index': 'True'})
        },
        'library.suitecase': {
            'Meta': {'ordering': "['order']", 'object_name': 'SuiteCase'},
            'case': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['library.Case']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 19, 21, 7, 18, 170782)'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'deleted_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 19, 21, 7, 18, 170984)'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'suite': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['library.Suite']"})
        }
    }

    complete_apps = ['execution']
