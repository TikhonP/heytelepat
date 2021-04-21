# Generated by Django 3.1.5 on 2021-04-21 04:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('medsenger_agent', '0006_auto_20210218_0440'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message_id', models.IntegerField()),
                ('text', models.TextField()),
                ('date', models.DateTimeField()),
                ('is_red', models.BooleanField(default=False)),
                ('is_notified', models.BooleanField(default=False)),
                ('contract', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='medsenger_agent.contract')),
            ],
        ),
    ]
