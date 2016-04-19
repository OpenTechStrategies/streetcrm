# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('streetcrm', '0028_auto_20150429_1248'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('institution', models.ForeignKey(related_name='organization', to='streetcrm.Institution')),
                ('participant', models.ForeignKey(related_name='leaders', to='streetcrm.Participant')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='institution',
            name='contact',
            field=models.ManyToManyField(through='streetcrm.Contact', to='streetcrm.Participant', related_name='main_contact'),
            preserve_default=True,
        ),
    ]
