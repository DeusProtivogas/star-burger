# Generated by Django 3.2.15 on 2024-05-14 10:04

from django.db import migrations

def fill_element_prices(apps, schema_editor):
    Product = apps.get_model('foodcartapp', 'Product')
    OrderElement = apps.get_model('foodcartapp', 'OrderElement')
    for elem in OrderElement.objects.all():
        product = elem.product
        elem.price = product.price
        elem.save()

class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0044_rename_element_orderelement_product'),
    ]

    operations = [
        migrations.RunPython(fill_element_prices),
    ]
