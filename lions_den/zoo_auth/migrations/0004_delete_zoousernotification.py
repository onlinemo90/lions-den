# Generated by Django 3.1.4 on 2021-05-15 22:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('zoo_auth', '0003_zoousernotification'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ZooUserNotification',
        ),
    ]