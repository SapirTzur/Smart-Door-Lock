# Generated by Django 4.1 on 2023-04-25 13:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("webapp", "0006_manager_delete_customuser"),
    ]

    operations = [
        migrations.RenameField(
            model_name="manager",
            old_name="mail",
            new_name="email",
        ),
    ]