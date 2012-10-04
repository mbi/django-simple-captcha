-*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding index on 'CaptchaStore', fields ['expiration']
        db.create_index('captcha_captchastore', ['expiration'])


    def backwards(self, orm):
        # Removing index on 'CaptchaStore', fields ['expiration']
        db.delete_index('captcha_captchastore', ['expiration'])


    models = {
        'captcha.captchastore': {
            'Meta': {'object_name': 'CaptchaStore'},
            'challenge': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'expiration': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'hashkey': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'response': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        }
    }

    complete_apps = ['captcha']
