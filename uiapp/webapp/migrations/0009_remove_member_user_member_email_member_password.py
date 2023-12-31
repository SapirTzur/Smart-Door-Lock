# Generated by Django 4.1 on 2023-04-27 22:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("webapp", "0008_fullname_delete_manager_remove_member_firstname_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="member",
            name="user",
        ),
        migrations.AddField(
            model_name="member",
            name="email",
            field=models.EmailField(default=1, max_length=254, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="member",
            name="password",
            field=models.CharField(default=4, max_length=255),
            preserve_default=False,
        ),
    ]
