# Generated by Django 4.1.1 on 2022-11-02 08:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0009_alter_post_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-shared_date', '-date_posted']},
        ),
    ]