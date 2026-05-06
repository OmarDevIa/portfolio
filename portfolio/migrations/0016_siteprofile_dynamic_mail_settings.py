from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0015_siteprofile_google_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteprofile',
            name='contact_recipient_email',
            field=models.EmailField(blank=True, default='', help_text='Adresse qui reçoit les messages du formulaire de contact.', max_length=254, verbose_name='email de réception contact'),
        ),
        migrations.AddField(
            model_name='siteprofile',
            name='mail_from_email',
            field=models.EmailField(blank=True, default='', help_text='Adresse affichée comme expéditeur des emails envoyés par le site.', max_length=254, verbose_name='email expéditeur'),
        ),
        migrations.AddField(
            model_name='siteprofile',
            name='smtp_app_password',
            field=models.CharField(blank=True, default='', help_text="Mot de passe d'application Google ou secret SMTP utilisé pour l'envoi.", max_length=255, verbose_name='clé application Google'),
        ),
        migrations.AddField(
            model_name='siteprofile',
            name='smtp_username',
            field=models.EmailField(blank=True, default='', help_text="Compte Gmail ou SMTP utilisé pour l'envoi des emails.", max_length=254, verbose_name='email SMTP / Google'),
        ),
    ]
