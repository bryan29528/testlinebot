# Generated by Django 2.2.17 on 2021-06-13 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('botapp', '0002_users_asktime'),
    ]

    operations = [
        migrations.AddField(
            model_name='users',
            name='resSF',
            field=models.CharField(max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='users',
            name='restext',
            field=models.CharField(max_length=10, null=True),
        ),
    ]
