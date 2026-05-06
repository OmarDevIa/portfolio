from django.db import migrations, models
import django.db.models.deletion
from django.utils.text import slugify


def populate_project_categories(apps, schema_editor):
    Project = apps.get_model('portfolio', 'Project')
    ProjectCategory = apps.get_model('portfolio', 'ProjectCategory')
    db_alias = schema_editor.connection.alias

    category_map = {
        'ia': 'IA & chatbot',
        'web': 'Web & e-commerce',
        'mobile': 'Application Mobile',
        'automation': 'Automatisation',
        'erp': 'ERP / CRM',
    }

    mapping = {}
    existing_values = (
        Project.objects.using(db_alias)
        .values_list('category', flat=True)
        .distinct()
    )

    for value in existing_values:
        if value is None:
            continue
        name = category_map.get(value, value)
        slug = slugify(value) or slugify(name) or f'cat-{value}'
        category, _created = ProjectCategory.objects.using(db_alias).get_or_create(
            slug=slug,
            defaults={'name': name, 'order': 0},
        )
        if category.name != name:
            category.name = name
            category.save(update_fields=['name'])
        mapping[value] = category.id

    for project in Project.objects.using(db_alias).all():
        value = project.category
        category_id = mapping.get(value)
        if category_id is None:
            name = value or 'Autres'
            slug = slugify(name) or 'autres'
            category, _created = ProjectCategory.objects.using(db_alias).get_or_create(
                slug=slug,
                defaults={'name': name, 'order': 0},
            )
            mapping[value] = category.id
            category_id = category.id
        project.category_ref_id = category_id
        project.save(update_fields=['category_ref'])


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0016_siteprofile_dynamic_mail_settings'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, unique=True, verbose_name='nom')),
                ('slug', models.SlugField(max_length=140, unique=True, verbose_name='slug')),
                ('order', models.PositiveSmallIntegerField(default=0, verbose_name='ordre')),
            ],
            options={
                'ordering': ['order', 'name'],
                'verbose_name': 'categorie de projet',
                'verbose_name_plural': 'categories de projet',
            },
        ),
        migrations.AddField(
            model_name='project',
            name='category_ref',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='projects',
                to='portfolio.projectcategory',
                verbose_name='categorie',
            ),
        ),
        migrations.RunPython(populate_project_categories, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='project',
            name='category',
        ),
        migrations.RenameField(
            model_name='project',
            old_name='category_ref',
            new_name='category',
        ),
        migrations.AlterField(
            model_name='project',
            name='category',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='projects',
                to='portfolio.projectcategory',
                verbose_name='categorie',
            ),
        ),
    ]
