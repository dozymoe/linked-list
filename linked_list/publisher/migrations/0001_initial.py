# Generated by Django 3.0.6 on 2020-05-22 01:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Publisher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=70)),
                ('url', models.URLField(null=True)),
                ('image', models.ImageField(null=True, upload_to='')),
                ('image_height', models.SmallIntegerField(null=True)),
                ('image_width', models.SmallIntegerField(null=True)),
                ('updated_at', models.DateTimeField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='PublisherSocial',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(db_index=True)),
                ('entity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='publisher.Publisher')),
            ],
            options={
                'ordering': ['url'],
            },
        ),
    ]
