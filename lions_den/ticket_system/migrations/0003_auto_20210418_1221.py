# Generated by Django 3.1.4 on 2021-04-18 11:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticket_system', '0002_auto_20210417_2300'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticket',
            name='is_open',
        ),
        migrations.AddField(
            model_name='ticket',
            name='app',
            field=models.CharField(choices=[('ZV', 'Zooverse'), ('LD', "Lion's Den")], default='LD', max_length=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ticket',
            name='status',
            field=models.CharField(choices=[('O', 'Open'), ('C', 'Closed')], default='O', max_length=2),
            preserve_default=False,
        ),
    ]
