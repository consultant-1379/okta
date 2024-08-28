# Generated by Django 3.1.7 on 2021-04-28 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cloudoverview', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PotentialCloud',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cloud_name', models.CharField(blank=True, max_length=32, null=True, unique=True)),
                ('version', models.CharField(blank=True, max_length=32, null=True)),
                ('number_of_hosts', models.CharField(blank=True, max_length=32, null=True)),
                ('cpu_contention', models.CharField(blank=True, max_length=32, null=True)),
                ('total_cpu', models.CharField(blank=True, max_length=32, null=True)),
                ('ram_contention', models.CharField(blank=True, max_length=32, null=True)),
                ('total_ram', models.CharField(blank=True, max_length=32, null=True)),
                ('storage', models.CharField(blank=True, max_length=32, null=True)),
                ('provisioning', models.CharField(blank=True, max_length=32, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='post',
            name='author',
        ),
        migrations.RemoveField(
            model_name='post',
            name='tags',
        ),
        migrations.DeleteModel(
            name='Comment',
        ),
        migrations.DeleteModel(
            name='Post',
        ),
    ]
