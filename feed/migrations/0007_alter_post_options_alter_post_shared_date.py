# Generated by Django 4.1.1 on 2022-11-02 07:48

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0006_alter_post_description'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-date_posted', '-shared_date']},
        ),
        migrations.AlterField(
            model_name='post',
            name='shared_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
