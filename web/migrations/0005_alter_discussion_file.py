# Generated by Django 3.2.2 on 2022-05-07 17:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0004_auto_20220507_1725'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discussion',
            name='file',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='web.file'),
        ),
    ]
