# Generated by Django 4.1 on 2023-03-13 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0011_completedvisit_visit_date"),
    ]

    operations = [
        migrations.AddField(
            model_name="completedvisit",
            name="ignore",
            field=models.BooleanField(
                default=False, help_text="don't create instruments for this visit"
            ),
        ),
    ]
