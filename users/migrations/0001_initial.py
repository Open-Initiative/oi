# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'UserProfile'
        db.create_table('users_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True)),
            ('birthdate', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('postcode', self.gf('django.db.models.fields.CharField')(max_length=9, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('mobile', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('display_name', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('picture', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('language', self.gf('django.db.models.fields.CharField')(default='fr', max_length=10)),
            ('balance', self.gf('django.db.models.fields.DecimalField')(default='0.0', max_digits=10, decimal_places=2)),
            ('blog', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['messages.Message'], unique=True)),
            ('rss_feed', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('last_feed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('users', ['UserProfile'])

        # Adding M2M table for field contacts on 'UserProfile'
        db.create_table('users_userprofile_contacts', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_userprofile', models.ForeignKey(orm['users.userprofile'], null=False)),
            ('to_userprofile', models.ForeignKey(orm['users.userprofile'], null=False))
        ))
        db.create_unique('users_userprofile_contacts', ['from_userprofile_id', 'to_userprofile_id'])

        # Adding M2M table for field observed_projects on 'UserProfile'
        db.create_table('users_userprofile_observed_projects', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm['users.userprofile'], null=False)),
            ('project', models.ForeignKey(orm['projects.project'], null=False))
        ))
        db.create_unique('users_userprofile_observed_projects', ['userprofile_id', 'project_id'])

        # Adding model 'Skill'
        db.create_table('users_skill', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('main', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('comment', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('users', ['Skill'])

        # Adding model 'Experience'
        db.create_table('users_experience', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('begining', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('end', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('company', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('job', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('users', ['Experience'])

        # Adding model 'Training'
        db.create_table('users_training', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('begining', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('end', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('degree', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('university', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('comment', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('users', ['Training'])

        # Adding model 'Payment'
        db.create_table('users_payment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('reason', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('transaction_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.Project'], null=True, blank=True)),
        ))
        db.send_create_signal('users', ['Payment'])

        # Adding model 'Prospect'
        db.create_table('users_prospect', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('contacted', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('kompassId', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal('users', ['Prospect'])

        # Adding model 'PersonalMessage'
        db.create_table('users_personalmessage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('from_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sent', to=orm['auth.User'])),
            ('to_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='received', to=orm['auth.User'])),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('sent_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('users', ['PersonalMessage'])


    def backwards(self, orm):
        
        # Deleting model 'UserProfile'
        db.delete_table('users_userprofile')

        # Removing M2M table for field contacts on 'UserProfile'
        db.delete_table('users_userprofile_contacts')

        # Removing M2M table for field observed_projects on 'UserProfile'
        db.delete_table('users_userprofile_observed_projects')

        # Deleting model 'Skill'
        db.delete_table('users_skill')

        # Deleting model 'Experience'
        db.delete_table('users_experience')

        # Deleting model 'Training'
        db.delete_table('users_training')

        # Deleting model 'Payment'
        db.delete_table('users_payment')

        # Deleting model 'Prospect'
        db.delete_table('users_prospect')

        # Deleting model 'PersonalMessage'
        db.delete_table('users_personalmessage')


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
        'messages.message': {
            'Meta': {'object_name': 'Message'},
            'ancestors': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'descendants'", 'blank': 'True', 'to': "orm['messages.Message']"}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ownmessages'", 'null': 'True', 'to': "orm['auth.User']"}),
            'category': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'icon': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['messages.Message']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['projects.Project']", 'null': 'True', 'blank': 'True'}),
            'related': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'related_to'", 'blank': 'True', 'to': "orm['messages.Message']"}),
            'relevance': ('django.db.models.fields.FloatField', [], {}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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
        },
        'users.experience': {
            'Meta': {'object_name': 'Experience'},
            'begining': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'company': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'end': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'users.payment': {
            'Meta': {'object_name': 'Payment'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['projects.Project']", 'null': 'True', 'blank': 'True'}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'transaction_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'users.personalmessage': {
            'Meta': {'object_name': 'PersonalMessage'},
            'from_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sent'", 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sent_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'to_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'received'", 'to': "orm['auth.User']"})
        },
        'users.prospect': {
            'Meta': {'object_name': 'Prospect'},
            'contacted': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kompassId': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'users.skill': {
            'Meta': {'object_name': 'Skill'},
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'main': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'users.training': {
            'Meta': {'object_name': 'Training'},
            'begining': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'degree': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'university': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'users.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'balance': ('django.db.models.fields.DecimalField', [], {'default': "'0.0'", 'max_digits': '10', 'decimal_places': '2'}),
            'birthdate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'blog': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['messages.Message']", 'unique': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'contacts': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'contacts_rel_+'", 'blank': 'True', 'to': "orm['users.UserProfile']"}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'display_name': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'fr'", 'max_length': '10'}),
            'last_feed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'mobile': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'observed_projects': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'followers'", 'blank': 'True', 'to': "orm['projects.Project']"}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'picture': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'postcode': ('django.db.models.fields.CharField', [], {'max_length': '9', 'blank': 'True'}),
            'rss_feed': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['users']
