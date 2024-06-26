# Generated by Django 5.0.3 on 2024-03-21 20:26

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="JavaFile",
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
                ("file_name", models.CharField(max_length=255)),
                ("javadoc_comment_count", models.IntegerField()),
                ("other_comment_count", models.IntegerField()),
                ("code_line_count", models.IntegerField()),
                ("loc", models.IntegerField()),
                ("function_count", models.IntegerField()),
                ("comment_deviation_percentage", models.FloatField()),
            ],
        ),
    ]
