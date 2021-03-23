# Generated by Django 3.1.2 on 2021-02-11 07:07

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_auto_20210201_1146'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='file',
            name='owner',
            field=models.ForeignKey(default=13, on_delete=django.db.models.deletion.CASCADE, related_name='file_owner', to='api.customuser'),
            preserve_default=False,
        ),
    ]