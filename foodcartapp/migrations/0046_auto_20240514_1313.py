# Generated by Django 3.2.15 on 2024-05-14 10:13

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0044_rename_element_orderelement_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderelement',
            name='price',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=8, validators=[django.core.validators.MinValueValidator(0)], verbose_name='стоимость'),
        ),
        migrations.AlterField(
            model_name='orderelement',
            name='quantity',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='количество'),
        ),
    ]
