# Generated by Django 5.0.4 on 2024-07-28 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0007_taskapplication_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='final_delivery_comments',
            field=models.TextField(blank=True, null=True),
        ),
    ]