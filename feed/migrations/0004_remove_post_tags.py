# Generated by Django 4.1.1 on 2022-10-31 09:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0003_alter_post_options_post_shared_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='tags',
        ),
    ]
