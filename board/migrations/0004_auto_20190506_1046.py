# Generated by Django 2.2.1 on 2019-05-06 05:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0003_topic_views'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topic',
            name='last_updated',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
