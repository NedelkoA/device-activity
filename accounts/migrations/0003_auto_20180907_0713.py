# Generated by Django 2.1.1 on 2018-09-07 07:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20180906_1229'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='company',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='company', to='company_manager.Company'),
        ),
    ]
