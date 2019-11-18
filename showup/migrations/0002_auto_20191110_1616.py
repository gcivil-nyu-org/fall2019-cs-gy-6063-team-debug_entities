# Generated by Django 2.2.6 on 2019-11-10 21:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("showup", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="genres",
            field=models.ManyToManyField(
                blank=True, related_name="genres", to="showup.Genre"
            ),
        )
    ]
