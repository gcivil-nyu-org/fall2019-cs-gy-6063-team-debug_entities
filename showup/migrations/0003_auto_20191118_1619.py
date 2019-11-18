# Generated by Django 2.2.5 on 2019-11-18 21:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("showup", "0002_auto_20191110_1616"),
    ]

    operations = [
        migrations.CreateModel(
            name="Squad",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID'
                    )
                ),
            ],
        ),
        migrations.CreateModel(
            name="SquadSwipe",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("direction", models.BooleanField()),
                ("swipee", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="squadswipee", to="showup.Squad")),
                ("swiper", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="squadswiper", to="showup.Squad")),
            ],
        ),
        migrations.AddField(
            model_name="customuser",
            name="squad",
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name="squad", to="showup.Squad"),
        ),
        migrations.AddConstraint(
            model_name="squadswipe",
            constraint=models.UniqueConstraint(fields=("swiper", "swipee"), name="Squad member can only swipe on another Squad once"),
        ),
    ]
