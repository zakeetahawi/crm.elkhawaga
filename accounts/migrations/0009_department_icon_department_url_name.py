# Generated by Django 4.2.20 on 2025-04-15 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_usersession_delete_formfield_alter_branch_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='department',
            name='icon',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='department',
            name='url_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
