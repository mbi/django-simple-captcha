# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'CaptchaStore'
        db.create_table('captcha_captchastore', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('challenge', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('response', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('hashkey', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
            ('expiration', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('captcha', ['CaptchaStore'])


    def backwards(self, orm):
        
        # Deleting model 'CaptchaStore'
        db.delete_table('captcha_captchastore')


    models = {
        'captcha.captchastore': {
            'Meta': {'object_name': 'CaptchaStore'},
            'challenge': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'expiration': ('django.db.models.fields.DateTimeField', [], {}),
            'hashkey': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'response': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        }
    }

    complete_apps = ['captcha']
