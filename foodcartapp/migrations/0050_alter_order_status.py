# Generated by Django 3.2.15 on 2024-05-15 08:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0049_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('received', 'Начат'), ('accepted', 'Принят'), ('in_progress', 'Собирается'), ('being_delivered', 'В доставке'), ('delivered', 'Выполнен')], db_index=True, default='received', max_length=20),
        ),
    ]
