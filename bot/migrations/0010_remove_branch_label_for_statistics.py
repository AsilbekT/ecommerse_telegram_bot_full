# Generated by Django 4.0.5 on 2022-09-02 16:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0009_branch_label_for_statistics'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='branch',
            name='label_for_statistics',
        ),
    ]