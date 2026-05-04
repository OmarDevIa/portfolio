from django.db import migrations
from django.utils.text import slugify


def forwards(apps, schema_editor):
    Service = apps.get_model('portfolio', 'Service')
    existing = set(
        Service.objects.exclude(slug__isnull=True).exclude(slug='').values_list('slug', flat=True)
    )

    for service in Service.objects.all().order_by('id'):
        if service.slug:
            continue
        base = slugify(service.title) or 'service'
        candidate = base
        counter = 2
        while candidate in existing:
            candidate = f"{base}-{counter}"
            counter += 1
        service.slug = candidate
        service.save(update_fields=['slug'])
        existing.add(candidate)


def backwards(apps, schema_editor):
    Service = apps.get_model('portfolio', 'Service')
    Service.objects.update(slug=None)


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0013_service_cover_image_service_demo_video_file_and_more'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
