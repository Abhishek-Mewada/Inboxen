# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-07 20:03
from __future__ import unicode_literals

import inboxen.cms.fields
from django.db import migrations, models
import inboxen.validators


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0015_auto_20180315_1434'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apppage',
            name='app',
            field=models.CharField(choices=[('tickets.urls', 'Tickets')], max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='helpbasepage',
            name='url_cache',
            field=models.CharField(default='', max_length=255, validators=[inboxen.validators.ProhibitNullCharactersValidator()]),
        ),
        migrations.AlterField(
            model_name='helppage',
            name='body',
            field=inboxen.cms.fields.RichTextField(allow_tags=['p', 'a', 'i', 'b', 'em', 'strong', 'ol', 'ul', 'li', 'pre', 'code', 'h1', 'h2', 'h3', 'h4', 'h5'], extensions=['markdown.extensions.toc'], help_text='Markdown text, supports the TOC extension.', safe_attrs=['href', 'id'], validators=[inboxen.validators.ProhibitNullCharactersValidator()]),
        ),
        migrations.AlterField(
            model_name='image',
            name='file',
            field=models.ImageField(height_field='height', upload_to='', width_field='width'),
        ),
    ]
