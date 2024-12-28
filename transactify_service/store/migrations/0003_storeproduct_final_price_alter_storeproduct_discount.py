# Generated by Django 5.1.3 on 2024-12-28 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_customer_balance_customer_last_changed_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='storeproduct',
            name='final_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='storeproduct',
            name='discount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=3),
        ),
    ]
