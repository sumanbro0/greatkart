# Generated by Django 5.0.1 on 2024-01-25 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0004_order_payment_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='coupon_code',
            field=models.CharField(blank=True, default='', max_length=10, null=True),
        ),
    ]