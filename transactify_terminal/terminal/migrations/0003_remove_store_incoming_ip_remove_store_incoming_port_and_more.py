# Generated by Django 5.1.4 on 2025-01-15 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('terminal', '0002_storeconnection'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='store',
            name='incoming_ip',
        ),
        migrations.RemoveField(
            model_name='store',
            name='incoming_port',
        ),
        migrations.RemoveField(
            model_name='store',
            name='uid',
        ),
        migrations.AlterField(
            model_name='store',
            name='service_name',
            field=models.CharField(default=1, max_length=255, unique=True),
            preserve_default=False,
        ),
    ]
