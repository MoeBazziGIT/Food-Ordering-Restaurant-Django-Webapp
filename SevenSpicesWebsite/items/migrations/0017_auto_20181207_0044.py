# Generated by Django 2.1.2 on 2018-12-07 00:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0016_auto_20181207_0042'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuitem',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=4),
        ),
        migrations.AlterField(
            model_name='topping',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=4),
        ),
    ]
