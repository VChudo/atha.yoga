# Generated by Django 4.1.5 on 2023-01-15 08:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("articles", "0002_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="article",
            old_name="is_draft",
            new_name="published",
        ),
    ]