from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='ContactMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('subject', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('budget', models.CharField(blank=True, max_length=50)),
                ('received_at', models.DateTimeField(auto_now_add=True)),
                ('is_read', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['-received_at'],
            },
        ),
        migrations.CreateModel(
            name='KPI',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(help_text='ex: +32%', max_length=30)),
                ('label', models.CharField(max_length=150)),
                ('order', models.PositiveSmallIntegerField(default=0)),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150)),
                ('slug', models.SlugField(unique=True)),
                ('category', models.CharField(choices=[('ia', 'IA & Chatbot'), ('web', 'Web & E-commerce'), ('mobile', 'Application Mobile'), ('automation', 'Automatisation'), ('erp', 'ERP / CRM')], default='web', max_length=20)),
                ('short_description', models.CharField(max_length=200)),
                ('full_description', models.TextField()),
                ('challenge', models.TextField(blank=True, help_text='Problème client résolu')),
                ('solution', models.TextField(blank=True, help_text='Solution apportée')),
                ('result', models.TextField(blank=True, help_text='Résultat mesurable ex: +32% conversion')),
                ('thumbnail', models.ImageField(upload_to='projects/thumbnails/')),
                ('demo_video_url', models.URLField(blank=True, help_text='URL YouTube/Vimeo embed ex: https://www.youtube.com/embed/XXXX')),
                ('demo_video_file', models.FileField(blank=True, help_text='Vidéo démo uploadée directement (mp4)', upload_to='projects/videos/')),
                ('live_url', models.URLField(blank=True, help_text='Lien vers le projet en ligne')),
                ('github_url', models.URLField(blank=True, help_text='Lien GitHub du projet')),
                ('tags', models.CharField(help_text='Tags séparés par virgule ex: Python,Django,IA', max_length=300)),
                ('is_featured', models.BooleanField(default=False, help_text='Afficher en avant dans le portfolio')),
                ('order', models.PositiveSmallIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['order', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('icon', models.CharField(help_text='Classe Font Awesome ex: fas fa-brain', max_length=60)),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('order', models.PositiveSmallIntegerField(default=0)),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(choices=[('ia', 'IA & Data Science'), ('web', 'Web & E-commerce'), ('mobile', 'Mobile'), ('automation', 'Automatisation')], max_length=20)),
                ('icon', models.CharField(max_length=60)),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('level', models.PositiveSmallIntegerField(default=80, help_text='Pourcentage 0-100')),
                ('order', models.PositiveSmallIntegerField(default=0)),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Tool',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('icon', models.CharField(max_length=60)),
                ('icon_class', models.CharField(help_text='Classe CSS couleur ex: icon-python', max_length=40)),
                ('title', models.CharField(max_length=80)),
                ('description', models.TextField()),
                ('order', models.PositiveSmallIntegerField(default=0)),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Testimonial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author_name', models.CharField(max_length=100)),
                ('author_role', models.CharField(help_text='ex: COO, RetailTech Paris', max_length=150)),
                ('author_email', models.EmailField(blank=True, max_length=254)),
                ('company_name', models.CharField(blank=True, max_length=150)),
                ('author_photo', models.ImageField(blank=True, upload_to='avatars/')),
                ('content', models.TextField()),
                ('rating', models.PositiveSmallIntegerField(default=5)),
                ('is_visible', models.BooleanField(default=True)),
                ('order', models.PositiveSmallIntegerField(default=0)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='portfolio.project')),
            ],
            options={
                'ordering': ['order', '-submitted_at'],
            },
        ),
    ]