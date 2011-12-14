# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Case'
        db.create_table('library_case', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, to=orm['auth.User'])),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, to=orm['auth.User'])),
            ('deleted_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, to=orm['auth.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 12, 14, 7, 22, 14, 548232))),
            ('modified_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 12, 14, 7, 22, 14, 548319))),
            ('deleted_on', self.gf('django.db.models.fields.DateTimeField')(null=True, db_index=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(related_name='cases', to=orm['core.Product'])),
        ))
        db.send_create_signal('library', ['Case'])

        # Adding model 'CaseVersion'
        db.create_table('library_caseversion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, to=orm['auth.User'])),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, to=orm['auth.User'])),
            ('deleted_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, to=orm['auth.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 12, 14, 7, 22, 14, 544358))),
            ('modified_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 12, 14, 7, 22, 14, 544464))),
            ('deleted_on', self.gf('django.db.models.fields.DateTimeField')(null=True, db_index=True)),
            ('case', self.gf('django.db.models.fields.related.ForeignKey')(related_name='versions', to=orm['library.Case'])),
            ('number', self.gf('django.db.models.fields.PositiveIntegerField')(unique=True)),
            ('latest', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('library', ['CaseVersion'])

        # Adding model 'CaseStep'
        db.create_table('library_casestep', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, to=orm['auth.User'])),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, to=orm['auth.User'])),
            ('deleted_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, to=orm['auth.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 12, 14, 7, 22, 14, 542708))),
            ('modified_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 12, 14, 7, 22, 14, 542899))),
            ('deleted_on', self.gf('django.db.models.fields.DateTimeField')(null=True, db_index=True)),
            ('caseversion', self.gf('django.db.models.fields.related.ForeignKey')(related_name='steps', to=orm['library.CaseVersion'])),
            ('number', self.gf('django.db.models.fields.IntegerField')(unique=True)),
            ('instruction', self.gf('django.db.models.fields.TextField')()),
            ('expected', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('library', ['CaseStep'])

        # Adding model 'Suite'
        db.create_table('library_suite', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, to=orm['auth.User'])),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, to=orm['auth.User'])),
            ('deleted_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, to=orm['auth.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 12, 14, 7, 22, 14, 549001))),
            ('modified_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 12, 14, 7, 22, 14, 549087))),
            ('deleted_on', self.gf('django.db.models.fields.DateTimeField')(null=True, db_index=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(related_name='suites', to=orm['core.Product'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('library', ['Suite'])

        # Adding model 'SuiteCase'
        db.create_table('library_suitecase', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, to=orm['auth.User'])),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, to=orm['auth.User'])),
            ('deleted_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, to=orm['auth.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 12, 14, 7, 22, 14, 546488))),
            ('modified_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 12, 14, 7, 22, 14, 546586))),
            ('deleted_on', self.gf('django.db.models.fields.DateTimeField')(null=True, db_index=True)),
            ('suite', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['library.Suite'])),
            ('case', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['library.Case'])),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('library', ['SuiteCase'])


    def backwards(self, orm):
        
        # Deleting model 'Case'
        db.delete_table('library_case')

        # Deleting model 'CaseVersion'
        db.delete_table('library_caseversion')

        # Deleting model 'CaseStep'
        db.delete_table('library_casestep')

        # Deleting model 'Suite'
        db.delete_table('library_suite')

        # Deleting model 'SuiteCase'
        db.delete_table('library_suitecase')


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
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 14, 7, 22, 14, 560827)'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'deleted_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_index': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 14, 7, 22, 14, 560914)'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'library.case': {
            'Meta': {'object_name': 'Case'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 14, 7, 22, 14, 559056)'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'deleted_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 14, 7, 22, 14, 559144)'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cases'", 'to': "orm['core.Product']"})
        },
        'library.casestep': {
            'Meta': {'ordering': "['number']", 'object_name': 'CaseStep'},
            'caseversion': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'steps'", 'to': "orm['library.CaseVersion']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 14, 7, 22, 14, 555237)'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'deleted_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_index': 'True'}),
            'expected': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instruction': ('django.db.models.fields.TextField', [], {}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 14, 7, 22, 14, 555333)'}),
            'number': ('django.db.models.fields.IntegerField', [], {'unique': 'True'})
        },
        'library.caseversion': {
            'Meta': {'ordering': "['number']", 'object_name': 'CaseVersion'},
            'case': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'versions'", 'to': "orm['library.Case']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 14, 7, 22, 14, 556287)'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'deleted_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_index': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latest': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 14, 7, 22, 14, 556374)'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'number': ('django.db.models.fields.PositiveIntegerField', [], {'unique': 'True'})
        },
        'library.suite': {
            'Meta': {'object_name': 'Suite'},
            'cases': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'suites'", 'symmetrical': 'False', 'through': "orm['library.SuiteCase']", 'to': "orm['library.Case']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 14, 7, 22, 14, 559821)'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'deleted_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_index': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 14, 7, 22, 14, 559906)'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'suites'", 'to': "orm['core.Product']"})
        },
        'library.suitecase': {
            'Meta': {'ordering': "['order']", 'object_name': 'SuiteCase'},
            'case': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['library.Case']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 14, 7, 22, 14, 557760)'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'deleted_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 14, 7, 22, 14, 557847)'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'suite': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['library.Suite']"})
        }
    }

    complete_apps = ['library']
