# Generated by Django 5.0.4 on 2024-05-25 06:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0029_recycleform_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recycleform',
            name='status',
            field=models.CharField(max_length=10, null=True),
        ),
    ]
