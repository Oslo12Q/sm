# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Useradmin',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_code', models.CharField(max_length=200)),
                ('user_key', models.CharField(max_length=200)),
                ('seq', models.IntegerField()),
                ('create_time', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
