# Generated by Django 3.0.7 on 2020-07-05 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Shop', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.FloatField(),
        ),
    ]
