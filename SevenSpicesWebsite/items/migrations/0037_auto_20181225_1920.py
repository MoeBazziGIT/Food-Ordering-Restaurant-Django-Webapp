# Generated by Django 2.1.2 on 2018-12-25 19:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0036_auto_20181225_1919'),
    ]

    operations = [
        migrations.AlterField(
            model_name='toppingscategory',
            name='amount_allowed',
            field=models.PositiveIntegerField(blank=True, default=True),
        ),
    ]
