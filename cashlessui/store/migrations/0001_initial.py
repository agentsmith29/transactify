# Generated by Django 5.1.3 on 2024-11-28 19:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cashlessui', '0002_remove_customer_balance'),
    ]

    operations = [
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='StoreProduct',
            fields=[
                ('ean', models.CharField(primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(default='Generic Product', max_length=100)),
                ('stock_quantity', models.PositiveIntegerField(default=0)),
                ('resell_price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='CustomerBalance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.DecimalField(decimal_places=2, max_digits=10)),
                ('last_changed', models.DateTimeField(auto_now_add=True)),
                ('customer', models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.CASCADE, to='cashlessui.customer')),
            ],
        ),
        migrations.CreateModel(
            name='CustomerDeposit',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('customer_balance', models.DecimalField(decimal_places=2, max_digits=10)),
                ('deposit_date', models.DateTimeField(auto_now_add=True)),
                ('customer', models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.CASCADE, related_name='deposits', to='cashlessui.customer')),
            ],
        ),
        migrations.CreateModel(
            name='ProductRestock',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('quantity', models.PositiveIntegerField()),
                ('purchase_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('restock_date', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stock_purchases', to='store.storeproduct')),
            ],
        ),
        migrations.CreateModel(
            name='CustomerPurchase',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('quantity', models.PositiveIntegerField()),
                ('purchase_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('customer_balance', models.DecimalField(decimal_places=2, max_digits=10)),
                ('purchase_date', models.DateTimeField(auto_now_add=True)),
                ('customer', models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.CASCADE, to='cashlessui.customer')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.storeproduct')),
            ],
        ),
    ]
