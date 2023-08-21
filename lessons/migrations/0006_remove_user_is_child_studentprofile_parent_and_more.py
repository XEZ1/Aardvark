# Generated by Django 4.1.3 on 2022-11-21 15:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0005_lessonrequest_recipient'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_child',
        ),
        migrations.AddField(
            model_name='studentprofile',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='lessons.studentprofile'),
        ),
        migrations.AlterField(
            model_name='lessonrequest',
            name='recipient',
            field=models.TextField(),
        ),
        migrations.DeleteModel(
            name='ChildProfile',
        ),
    ]
