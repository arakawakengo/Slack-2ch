from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Posts',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('text', models.CharField(max_length=100)),
                ('category', models.CharField(max_length=10)),
                ('comment_cnt', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='users_posts', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Questions',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('text', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts_questions', to='posts.posts')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='users_questions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Replies',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('text', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions_replies', to='posts.questions')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='users_replies', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Categories',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('category_name', models.CharField(max_length=10)),
                ('workspace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='authentication.workspace')),
            ],
        ),
        migrations.AddConstraint(
            model_name='categories',
            constraint=models.UniqueConstraint(fields=('category_name', 'workspace'), name='category_unique'),
        ),
    ]
