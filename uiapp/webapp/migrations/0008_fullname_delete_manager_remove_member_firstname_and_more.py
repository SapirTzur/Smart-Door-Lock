# Generated by Django 4.1 on 2023-04-27 11:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("webapp", "0007_rename_mail_manager_email"),
    ]

    operations = [
        migrations.CreateModel(
            name="FullName",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("full_name", models.CharField(max_length=255)),
            ],
        ),
        migrations.DeleteModel(
            name="Manager",
        ),
        migrations.RemoveField(
            model_name="member",
            name="firstname",
        ),
        migrations.RemoveField(
            model_name="member",
            name="lastname",
        ),
        migrations.AddField(
            model_name="member",
            name="user",
            field=models.OneToOneField(
                default=2,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="fullname",
            name="member",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="webapp.member"
            ),
        ),
    ]