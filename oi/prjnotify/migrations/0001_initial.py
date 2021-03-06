# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'NoticeType'
        db.create_table('prjnotify_noticetype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('display', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('prjnotify', ['NoticeType'])

        # Adding model 'Observer'
        db.create_table('prjnotify_observer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('use_default', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('last_notice', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('send_every', self.gf('django.db.models.fields.IntegerField')(default=3600)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.Project'], null=True, blank=True)),
        ))
        db.send_create_signal('prjnotify', ['Observer'])

        # Adding unique constraint on 'Observer', fields ['user', 'project']
        db.create_unique('prjnotify_observer', ['user_id', 'project_id'])

        # Adding model 'NoticeSetting'
        db.create_table('prjnotify_noticesetting', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('observer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['prjnotify.Observer'])),
            ('notice_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['prjnotify.NoticeType'])),
            ('medium', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('send', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('prjnotify', ['NoticeSetting'])

        # Adding unique constraint on 'NoticeSetting', fields ['observer', 'notice_type']
        db.create_unique('prjnotify_noticesetting', ['observer_id', 'notice_type_id'])

        # Adding model 'Notice'
        db.create_table('prjnotify_notice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('recipient', self.gf('django.db.models.fields.related.ForeignKey')(related_name='recieved_notices', to=orm['auth.User'])),
            ('sender', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sent_notices', null=True, to=orm['auth.User'])),
            ('notice_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['prjnotify.NoticeType'])),
            ('param', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('unseen', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('archived', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('sent', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('on_site', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.Project'])),
            ('observer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['prjnotify.Observer'])),
        ))
        db.send_create_signal('prjnotify', ['Notice'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'NoticeSetting', fields ['observer', 'notice_type']
        db.delete_unique('prjnotify_noticesetting', ['observer_id', 'notice_type_id'])

        # Removing unique constraint on 'Observer', fields ['user', 'project']
        db.delete_unique('prjnotify_observer', ['user_id', 'project_id'])

        # Deleting model 'NoticeType'
        db.delete_table('prjnotify_noticetype')

        # Deleting model 'Observer'
        db.delete_table('prjnotify_observer')

        # Deleting model 'NoticeSetting'
        db.delete_table('prjnotify_noticesetting')

        # Deleting model 'Notice'
        db.delete_table('prjnotify_notice')


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
        'prjnotify.notice': {
            'Meta': {'ordering': "['-added']", 'object_name': 'Notice'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notice_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['prjnotify.NoticeType']"}),
            'observer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['prjnotify.Observer']"}),
            'on_site': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'param': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['projects.Project']"}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'recieved_notices'", 'to': "orm['auth.User']"}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sent_notices'", 'null': 'True', 'to': "orm['auth.User']"}),
            'sent': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'unseen': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'prjnotify.noticesetting': {
            'Meta': {'unique_together': "(('observer', 'notice_type'),)", 'object_name': 'NoticeSetting'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'medium': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'notice_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['prjnotify.NoticeType']"}),
            'observer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['prjnotify.Observer']"}),
            'send': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'prjnotify.noticetype': {
            'Meta': {'object_name': 'NoticeType'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'display': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'prjnotify.observer': {
            'Meta': {'unique_together': "(('user', 'project'),)", 'object_name': 'Observer'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_notice': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['projects.Project']", 'null': 'True', 'blank': 'True'}),
            'send_every': ('django.db.models.fields.IntegerField', [], {'default': '3600'}),
            'use_default': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'projects.project': {
            'Meta': {'object_name': 'Project'},
            'ancestors': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'descendants'", 'blank': 'True', 'to': "orm['projects.Project']"}),
            'assignee': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assigned_projects'", 'null': 'True', 'to': "orm['auth.User']"}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ownprojects'", 'null': 'True', 'to': "orm['auth.User']"}),
            'commission': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '12', 'decimal_places': '2'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'delay': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'delegate_to': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'delegated_projects'", 'null': 'True', 'to': "orm['auth.User']"}),
            'due_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'subprojects'", 'null': 'True', 'to': "orm['projects.Project']"}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'offer': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '12', 'decimal_places': '2'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'tasks'", 'null': 'True', 'to': "orm['projects.Project']"}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'progress': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'validation': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['prjnotify']
