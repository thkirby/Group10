# Generated by Django 4.1.1 on 2022-11-28 04:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0013_threadmodel_messagemodel'),
    ]

    operations = [
        migrations.RenameField(
            model_name='messagemodel',
            old_name='body',
            new_name='textbody',
        ),
    ]
