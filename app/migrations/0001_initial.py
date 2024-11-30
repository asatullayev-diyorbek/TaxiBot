# Generated by Django 5.1.3 on 2024-11-21 14:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BotUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat_id', models.BigIntegerField(unique=True)),
                ('full_name', models.CharField(max_length=255)),
                ('phone_number', models.CharField(max_length=13)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat_id', models.BigIntegerField(unique=True)),
                ('full_name', models.CharField(max_length=255)),
                ('phone_number', models.CharField(max_length=13)),
                ('car_info', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='OrderTaxi',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_location', models.TextField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('person_count', models.PositiveIntegerField(blank=True, null=True)),
                ('direction', models.CharField(blank=True, max_length=100, null=True)),
                ('leave_time', models.CharField(blank=True, max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('driver', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.driver')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.botuser')),
            ],
        ),
    ]