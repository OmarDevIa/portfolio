from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0014_populate_service_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteprofile',
            name='google_analytics_dashboard_url',
            field=models.URLField(blank=True, default='', help_text='Lien direct vers votre propri\u00e9t\u00e9 Google Analytics.', verbose_name='URL tableau de bord Google Analytics'),
        ),
        migrations.AddField(
            model_name='siteprofile',
            name='google_analytics_id',
            field=models.CharField(blank=True, default='', help_text='Exemple : G-XXXXXXXXXX', max_length=40, verbose_name='ID Google Analytics'),
        ),
        migrations.AddField(
            model_name='siteprofile',
            name='google_site_verification',
            field=models.CharField(blank=True, default='', help_text='Code utilis\u00e9 pour la balise meta google-site-verification.', max_length=255, verbose_name='code de v\u00e9rification Google'),
        ),
    ]
