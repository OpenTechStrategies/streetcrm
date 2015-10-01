# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('swoptact', '0052_add_staff_permissions'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='issue_area',
        ),
        migrations.AddField(
            model_name='event',
            name='narrative',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='event',
            name='secondary_organizer',
            field=models.ForeignKey(blank=True, related_name='Organizer2', null=True, to='swoptact.Participant'),
        ),
        migrations.AlterField(
            model_name='event',
            name='major_action',
            field=models.ForeignKey(blank=True, null=True, verbose_name='Connected Action', to='swoptact.Event'),
        ),
        migrations.AlterField(
            model_name='event',
            name='tags',
            field=models.ManyToManyField(verbose_name='Tags', to='swoptact.Tag', blank=True, help_text='Note that new tags added here are not created.'),
        ),
        migrations.AlterField(
            model_name='institution',
            name='contacts',
            field=models.ManyToManyField(to='swoptact.Participant', related_name='main_contact'),
        ),
        migrations.AlterField(
            model_name='institution',
            name='tags',
            field=models.ManyToManyField(verbose_name='Institution Tags', to='swoptact.Tag', blank=True, help_text='Note that new tags added here are not created.'),
        ),
        migrations.AlterField(
            model_name='participant',
            name='participant_city_address',
            field=models.CharField(null=True, verbose_name='City', blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(verbose_name='Tag', unique=True, max_length=25),
        ),
    ]
