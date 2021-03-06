# Generated by Django 3.0.6 on 2020-05-22 01:18

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('author', '0001_initial'),
        ('publisher', '0001_initial'),
        ('link', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LinkKeyword',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=32)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AlterModelOptions(
            name='link',
            options={'ordering': ['created_at']},
        ),
        migrations.RenameField(
            model_name='link',
            old_name='headline',
            new_name='title',
        ),
        migrations.RenameField(
            model_name='link',
            old_name='href',
            new_name='url',
        ),
        migrations.RemoveField(
            model_name='link',
            name='pub_date',
        ),
        migrations.AddField(
            model_name='link',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='author.Author'),
        ),
        migrations.AddField(
            model_name='link',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='link',
            name='html',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='link',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='link',
            name='image_alt',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='link',
            name='image_height',
            field=models.SmallIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='link',
            name='image_width',
            field=models.SmallIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='link',
            name='modified_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='link',
            name='published_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='link',
            name='publisher',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='publisher.Publisher'),
        ),
        migrations.AddField(
            model_name='link',
            name='text',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='link',
            name='description',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='link',
            name='keywords',
            field=models.ManyToManyField(to='link.LinkKeyword'),
        ),
    ]
