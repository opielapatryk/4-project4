# Generated by Django 4.2.3 on 2023-08-14 08:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0003_rename_user_id_post_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='likes',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='post',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, default="2000-12-12 12:12"),
            preserve_default=False,
        ),
    ]
