# Generated by Django 3.2.4 on 2021-08-02 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smm', '0003_alter_post_post_body'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, default='default.jpg', upload_to=''),
        ),
    ]