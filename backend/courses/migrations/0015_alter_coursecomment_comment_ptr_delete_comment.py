# Generated by Django 4.1.5 on 2023-01-13 09:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0012_comment"),
        ("courses", "0014_alter_course_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="coursecomment",
            name="comment_ptr",
            field=models.OneToOneField(
                auto_created=True,
                on_delete=django.db.models.deletion.CASCADE,
                parent_link=True,
                primary_key=True,
                serialize=False,
                to="core.comment",
            ),
        ),
        migrations.DeleteModel(
            name="Comment",
        ),
    ]
