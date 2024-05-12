# Generated by Django 5.0 on 2024-01-15 15:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=20, unique=True)),
                ('password', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='JobSeeker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=255)),
                ('skill', models.CharField(max_length=255)),
                ('format', models.CharField(max_length=255)),
                ('experience_j', models.CharField(max_length=255)),
                ('salary', models.CharField(max_length=255)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.user')),
            ],
        ),
        migrations.CreateModel(
            name='Employer',
            fields=[
                ('job_title', models.CharField(max_length=255)),
                ('vacancy_id', models.AutoField(default=0, primary_key=True, serialize=False)),
                ('company_name', models.CharField(max_length=255)),
                ('industry', models.CharField(max_length=255)),
                ('skills', models.TextField()),
                ('short_description', models.TextField()),
                ('job_description', models.TextField()),
                ('format_e', models.CharField(max_length=255)),
                ('experience_e', models.CharField(max_length=255)),
                ('salary', models.CharField(max_length=255)),
                ('spec', models.CharField(max_length=255)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.user')),
            ],
        ),
        migrations.CreateModel(
            name='Anketa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('age', models.IntegerField()),
                ('city', models.CharField(max_length=255)),
                ('gender', models.CharField(max_length=20)),
                ('file_url', models.CharField(max_length=255)),
                ('phone_number', models.CharField(blank=True, max_length=230)),
                ('job', models.CharField(max_length=20)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.user')),
            ],
        ),
    ]
