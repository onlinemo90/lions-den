# Generated by Django 3.1.4 on 2021-05-15 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticket_system', '0011_auto_20210515_0136'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticketaction',
            name='type',
            field=models.CharField(choices=[('CREATE', 'created'), ('EDIT', 'edited')], max_length=6),
        ),
    ]
