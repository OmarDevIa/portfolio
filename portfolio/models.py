from urllib.parse import urlparse

from PIL import Image, ImageOps, UnidentifiedImageError

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.utils.deconstruct import deconstructible
from django_ckeditor_5.fields import CKEditor5Field


TECH_VISUALS = {
    'python': ('fab fa-python', 'tech-badge--python'),
    'django': ('fas fa-leaf', 'tech-badge--django'),
    'react': ('fab fa-react', 'tech-badge--react'),
    'flutter': ('fas fa-mobile-screen-button', 'tech-badge--flutter'),
    'aws': ('fab fa-aws', 'tech-badge--aws'),
    'docker': ('fab fa-docker', 'tech-badge--docker'),
    'postgresql': ('fas fa-database', 'tech-badge--db'),
    'mysql': ('fas fa-database', 'tech-badge--db'),
    'sqlite': ('fas fa-database', 'tech-badge--db'),
    'tensorflow': ('fas fa-brain', 'tech-badge--ai'),
    'pytorch': ('fas fa-brain', 'tech-badge--ai'),
    'langchain': ('fas fa-link', 'tech-badge--ai'),
    'rag': ('fas fa-robot', 'tech-badge--ai'),
    'llm': ('fas fa-robot', 'tech-badge--ai'),
    'gradio': ('fas fa-wand-magic-sparkles', 'tech-badge--web'),
    'next.js': ('fas fa-bolt', 'tech-badge--web'),
    'nextjs': ('fas fa-bolt', 'tech-badge--web'),
    'typescript': ('fas fa-code', 'tech-badge--web'),
    'javascript': ('fas fa-code', 'tech-badge--web'),
    'php': ('fas fa-server', 'tech-badge--backend'),
    'laravel': ('fab fa-laravel', 'tech-badge--backend'),
    'node.js': ('fab fa-node-js', 'tech-badge--backend'),
    'nodejs': ('fab fa-node-js', 'tech-badge--backend'),
    'express': ('fas fa-server', 'tech-badge--backend'),
    'firebase': ('fas fa-fire', 'tech-badge--mobile'),
    'shopify': ('fab fa-shopify', 'tech-badge--shop'),
    'stripe api': ('fas fa-credit-card', 'tech-badge--shop'),
}


@deconstructible
class FileSizeValidator:
    def __init__(self, max_mb):
        self.max_mb = max_mb
        self.max_bytes = max_mb * 1024 * 1024

    def __call__(self, file_obj):
        if file_obj.size > self.max_bytes:
            raise ValidationError(f'File exceeds {self.max_mb} MB limit.')


def _validate_image_content(file_obj):
    try:
        file_obj.seek(0)
        Image.open(file_obj).verify()
    except (UnidentifiedImageError, OSError):
        raise ValidationError('Invalid or corrupted image file.')
    finally:
        file_obj.seek(0)

SIGNAL_VISUALS = {
    'ia': 'fas fa-brain',
    'mobile': 'fas fa-mobile-screen-button',
    'aws': 'fas fa-cloud',
    'agents': 'fas fa-robot',
    'data': 'fas fa-database',
    'automation': 'fas fa-bolt',
    'cloud': 'fas fa-cloud-arrow-up',
    'rag': 'fas fa-link',
}


class SiteProfile(models.Model):
    full_name = models.CharField(_('nom complet'), max_length=120, default='Omar Atta')
    brand_name = models.CharField(_('nom de marque'), max_length=120, default='Omar.tech')
    hero_badge_text = models.CharField(_('badge hero'), max_length=120, default='Disponible pour missions')
    hero_role = models.CharField(_('rôle hero'), max_length=120, default='Ingénieur Freelance')
    hero_highlight = models.CharField(_('mise en avant hero'), max_length=180, default='IA, Logiciel, Mobile & Cloud AWS')
    hero_description = CKEditor5Field(
        _('description hero'),
        default='Je conçois et mets en production des produits IA, applications métier, stacks cloud AWS et assistants virtuels pour startups, PME et équipes qui veulent livrer plus vite, mieux servir leurs clients et structurer leur croissance en Afrique et à l’international.',
    )
    years_experience = models.PositiveSmallIntegerField(_('années d’expérience'), default=4)
    experience_label = models.CharField(_('libellé expérience'), max_length=120, default="Ans d'expérience")
    impact_value = models.CharField(_('valeur impact'), max_length=40, default='B2B')
    impact_label = models.CharField(_('libellé impact'), max_length=120, default='Approche orientée impact')
    profile_photo = models.ImageField(
        _('photo de profil'),
        upload_to='profile/',
        blank=True,
        validators=[
            FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp']),
            FileSizeValidator(5),
            _validate_image_content,
        ],
        help_text='Image recommandee: 1200x1500 px minimum, ratio portrait 4:5, visage bien centre avec espace au-dessus de la tete.',
    )
    about_photo = models.ImageField(
        _('photo à propos'),
        upload_to='profile/',
        blank=True,
        validators=[
            FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp']),
            FileSizeValidator(5),
            _validate_image_content,
        ],
    )
    about_title = models.CharField(_('titre à propos'), max_length=180, default='Ingénieur orienté business, livraison rapide et impact mesurable.')
    about_intro = CKEditor5Field(
        _('introduction à propos'),
        default='Développeur full-stack spécialisé en IA, logiciels métier, applications mobiles, cloud AWS et automatisation, je transforme des besoins complexes en produits fiables, scalables et orientés retour sur investissement. Certifié IBM, j’interviens comme partenaire technique pour des entreprises en Afrique francophone, Europe et remote international.',
    )
    about_body = CKEditor5Field(
        _('texte à propos'),
        default='Mon approche est simple : comprendre le problème métier, sécuriser l’architecture, livrer vite et mesurer l’impact. J’accompagne aussi bien des lancements MVP que des plateformes critiques, assistants virtuels et systèmes intelligents connectés au cloud.',
    )
    cv_file = models.FileField(
        _('CV'),
        upload_to='profile/',
        blank=True,
        validators=[
            FileExtensionValidator(['pdf']),
            FileSizeValidator(10),
        ],
    )
    footer_tagline = models.CharField(_('sous-titre footer'), max_length=160, default='Ingénieur Freelance IA & Logiciel')
    availability_text = models.CharField(_('texte de disponibilité'), max_length=180, default='Disponible pour nouvelles missions — Afrique & Remote')
    email = models.EmailField(_('email'), default='')
    contact_recipient_email = models.EmailField(
        _('email de réception contact'),
        blank=True,
        default='',
        help_text=_("Adresse qui reçoit les messages du formulaire de contact."),
    )
    mail_from_email = models.EmailField(
        _('email expéditeur'),
        blank=True,
        default='',
        help_text=_("Adresse affichée comme expéditeur des emails envoyés par le site."),
    )
    smtp_username = models.EmailField(
        _('email SMTP / Google'),
        blank=True,
        default='',
        help_text=_("Compte Gmail ou SMTP utilisé pour l'envoi des emails."),
    )
    smtp_app_password = models.CharField(
        _('clé application Google'),
        max_length=255,
        blank=True,
        default='',
        help_text=_("Mot de passe d'application Google ou secret SMTP utilisé pour l'envoi."),
    )
    whatsapp_url = models.URLField(_('URL WhatsApp'), blank=True, default='')
    linkedin_url = models.URLField(_('URL LinkedIn'), blank=True, default='')
    github_url = models.URLField(_('URL GitHub'), blank=True)
    hero_signals = models.CharField(_('signaux hero'), max_length=255, default='IA,Mobile,AWS,Agents,Data,Automation', help_text=_('Valeurs séparées par virgule.'))
    tech_stack_marquee = models.CharField(_('bande technologies'), max_length=500, default='Python,Django,React,Flutter,LangChain,RAG,Docker,AWS,Node.js,PostgreSQL,TensorFlow,n8n', help_text=_('Technologies séparées par virgule.'))
    primary_badge_text = models.CharField(_('badge principal'), max_length=120, default='IBM Certified')
    secondary_badge_text = models.CharField(_('badge secondaire'), max_length=120, default='Livraison orientée impact')
    secondary_badge_icon = models.CharField(_('icône badge secondaire'), max_length=60, default='fas fa-layer-group')
    primary_certificate_label = models.CharField(_('libellé certification 1'), max_length=120, default='IBM AI Engineering')
    primary_certificate_url = models.URLField(_('URL certification 1'), blank=True, default='https://www.credly.com/badges/84bc6f03-87d3-4fc6-b3dd-c67a48f70d2a/public_url')
    secondary_certificate_label = models.CharField(_('libellé certification 2'), max_length=120, default='IBM Applied AI')
    secondary_certificate_url = models.URLField(_('URL certification 2'), blank=True, default='https://www.credly.com/badges/b5b05f89-e8e7-48a4-b96d-f73b05b33f1f/public_url')
    cert_section_title = models.CharField(
        _('titre certifications'),
        max_length=180,
        default='Ma Certification Spécialisée en Developpement Logiciel && IA',
        blank=True,
    )
    cert_section_desc = CKEditor5Field(
        _('description certifications'),
        default='Mon expertise est prouvée et certifiée par IBM / Coursera.',
        blank=True,
    )
    cert_section_note = models.CharField(
        _('note certifications'),
        max_length=180,
        default='Cliquez sur le badge pour vérifier la certification sur Credly.',
        blank=True,
    )
    primary_certificate_badge = models.FileField(
        _('badge certification 1'),
        upload_to='profile/',
        blank=True,
        validators=[
            FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp', 'pdf']),
            FileSizeValidator(5),
        ],
        help_text=_('Image ou PDF du badge (jpg, png, pdf).'),
    )
    secondary_certificate_badge = models.FileField(
        _('badge certification 2'),
        upload_to='profile/',
        blank=True,
        validators=[
            FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp', 'pdf']),
            FileSizeValidator(5),
        ],
        help_text=_('Image ou PDF du badge (jpg, png, pdf).'),
    )
    services_section_subtitle = models.CharField(_('sous-titre services'), max_length=120, default='Services', blank=True)
    services_section_title = models.CharField(_('titre services'), max_length=120, default='Ce que je fais', blank=True)
    skills_section_subtitle = models.CharField(_('sous-titre competences'), max_length=120, default='Stack technique', blank=True)
    skills_section_title = models.CharField(_('titre competences'), max_length=120, default='Compétences', blank=True)
    tools_section_subtitle = models.CharField(_('sous-titre outils'), max_length=120, default='Outils & plateformes', blank=True)
    tools_section_title = models.CharField(_('titre outils'), max_length=120, default='Stack operationnelle', blank=True)
    tools_section_desc = CKEditor5Field(_('description outils'), default='Des outils robustes pour livrer vite, securiser l\'execution et scaler proprement.', blank=True)
    tools_section_intro = CKEditor5Field(_('intro outils'), default='Une vision plus visuelle de mon ecosysteme : chaque bloc combine un logo avec les plateformes que j\'utilise au quotidien.', blank=True)
    portfolio_section_title = models.CharField(_('titre portfolio'), max_length=160, default='Projets & Réalisations', blank=True)
    portfolio_section_desc = CKEditor5Field(_('description portfolio'), default='Des projets concrets, orientés résultats et livrables mesurables.', blank=True)
    testimonials_section_subtitle = models.CharField(_('sous-titre temoignages'), max_length=120, default='Témoignages', blank=True)
    testimonials_section_title = models.CharField(_('titre temoignages'), max_length=160, default='Ce que disent mes clients', blank=True)
    contact_section_subtitle = models.CharField(_('sous-titre contact'), max_length=120, default='Contact', blank=True)
    contact_section_title = models.CharField(_('titre contact'), max_length=160, default='Obtenir un devis gratuit', blank=True)
    google_analytics_id = models.CharField(
        _('ID Google Analytics'),
        max_length=40,
        blank=True,
        default='',
        help_text=_('Exemple : G-XXXXXXXXXX'),
    )
    google_analytics_dashboard_url = models.URLField(
        _('URL tableau de bord Google Analytics'),
        blank=True,
        default='',
        help_text=_('Lien direct vers votre propri\u00e9t\u00e9 Google Analytics.'),
    )
    google_site_verification = models.CharField(
        _('code de v\u00e9rification Google'),
        max_length=255,
        blank=True,
        default='',
        help_text=_('Code utilis\u00e9 pour la balise meta google-site-verification.'),
    )

    class Meta:
        verbose_name = _('profil du site')
        verbose_name_plural = _('profil du site')

    def __str__(self):
        return self.full_name

    @property
    def brand_primary(self):
        primary, separator, _secondary = self.brand_name.partition('.')
        return primary if separator else self.brand_name

    @property
    def brand_secondary(self):
        _primary, separator, secondary = self.brand_name.partition('.')
        return secondary if separator else 'tech'

    def get_signal_items(self):
        items = []
        for raw_signal in [item.strip() for item in self.hero_signals.split(',') if item.strip()]:
            items.append({
                'label': raw_signal,
                'icon': SIGNAL_VISUALS.get(raw_signal.lower(), 'fas fa-star'),
            })
        return items

    def get_tech_stack_items(self):
        return [item.strip() for item in self.tech_stack_marquee.split(',') if item.strip()]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete('site_profile')

    def delete(self, *args, **kwargs):
        result = super().delete(*args, **kwargs)
        cache.delete('site_profile')
        return result


class CertificationBadge(models.Model):
    site_profile = models.ForeignKey(
        SiteProfile,
        verbose_name=_('profil du site'),
        on_delete=models.CASCADE,
        related_name='certification_badges',
    )
    label = models.CharField(_('libellé'), max_length=120)
    url = models.URLField(_('URL certification'), blank=True, default='')
    badge_file = models.FileField(
        _('badge'),
        upload_to='profile/',
        blank=True,
        validators=[
            FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp', 'pdf']),
            FileSizeValidator(5),
        ],
        help_text=_('Image ou PDF du badge (jpg, png, pdf).'),
    )
    order = models.PositiveSmallIntegerField(_('ordre'), default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = _('badge de certification')
        verbose_name_plural = _('badges de certification')

    def __str__(self):
        return self.label

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete('site_profile')

    def delete(self, *args, **kwargs):
        result = super().delete(*args, **kwargs)
        cache.delete('site_profile')
        return result


class HeroSlide(models.Model):
    THEME_CHOICES = [
        ('burnt', _('Orange')), 
        ('teal', _('Teal')),
        ('light', _('Light')),
    ]

    eyebrow = models.CharField(_('sur-titre'), max_length=30, default='01')
    title = models.CharField(_('titre'), max_length=120)
    description = CKEditor5Field(_('description'))
    icon = models.CharField(_('icône'), max_length=60, default='fas fa-sparkles')
    theme = models.CharField(_('thème'), max_length=20, choices=THEME_CHOICES, default='burnt')
    order = models.PositiveSmallIntegerField(_('ordre'), default=0)
    is_active = models.BooleanField(_('actif'), default=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = _('slide hero')
        verbose_name_plural = _('slides hero')

    def __str__(self):
        return self.title


class Service(models.Model):
    icon = models.CharField(_('icône'), max_length=60, help_text=_("Classe Font Awesome ex: fas fa-brain"))
    title = models.CharField(_('titre'), max_length=100)
    description = CKEditor5Field(_('description'))
    slug = models.SlugField(_('slug'), max_length=140, unique=True, blank=True, null=True)
    summary = models.TextField(_('résumé'), blank=True)
    full_description = CKEditor5Field(_('description détaillée'), blank=True)
    detail_points = models.TextField(
        _('points clés'),
        blank=True,
        help_text=_('Un point par ligne pour affichage en liste.'),
    )
    cover_image = models.ImageField(_('image principale'), upload_to='services/', blank=True)
    secondary_image = models.ImageField(_('image secondaire'), upload_to='services/', blank=True)
    demo_video_file = models.FileField(
        _('vidéo démonstration'),
        upload_to='services/',
        blank=True,
        validators=[FileExtensionValidator(['mp4', 'webm', 'ogg'])],
    )
    order = models.PositiveSmallIntegerField(_('ordre'), default=0)

    class Meta:
        ordering = ['order']
        verbose_name = _('service')
        verbose_name_plural = _('services')

    def __str__(self):
        return self.title

    @property
    def has_video(self):
        return bool(self.demo_video_file)

    def get_detail_points(self):
        return [line.strip() for line in self.detail_points.splitlines() if line.strip()]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)[:130] or 'service'
            slug = base_slug
            index = 2
            while Service.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                suffix = f'-{index}'
                slug = f'{base_slug[:140 - len(suffix)]}{suffix}'
                index += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_video_mime_type(self):
        if not self.demo_video_file:
            return ''

        file_name = self.demo_video_file.name.lower()
        if file_name.endswith('.webm'):
            return 'video/webm'
        if file_name.endswith('.ogg'):
            return 'video/ogg'
        return 'video/mp4'


class Skill(models.Model):
    CATEGORY_CHOICES = [
        ('ia', 'IA & science des données'),
        ('web', 'Web & e-commerce'),
        ('mobile', 'Mobile'),
        ('automation', 'Automatisation'),
    ]
    category = models.CharField(_('catégorie'), max_length=20, choices=CATEGORY_CHOICES)
    icon = models.CharField(_('icône'), max_length=60)
    title = models.CharField(_('titre'), max_length=100)
    description = models.TextField(_('description'))
    level = models.PositiveSmallIntegerField(_('niveau'), default=80, help_text=_("Pourcentage 0-100"))
    order = models.PositiveSmallIntegerField(_('ordre'), default=0)

    class Meta:
        ordering = ['order']
        verbose_name = _('compétence')
        verbose_name_plural = _('compétences')

    def __str__(self):
        return self.title


class Tool(models.Model):
    icon = models.CharField(_('icône'), max_length=60)
    icon_class = models.CharField(_('classe CSS'), max_length=40, help_text=_('Couleur hexa ex: #3776ab'))
    title = models.CharField(_('titre'), max_length=80)
    description = CKEditor5Field(_('description'))
    order = models.PositiveSmallIntegerField(_('ordre'), default=0)

    class Meta:
        ordering = ['order']
        verbose_name = _('outil')
        verbose_name_plural = _('outils')

    def __str__(self):
        return self.title


class ProjectCategory(models.Model):
    name = models.CharField(_('nom'), max_length=120, unique=True)
    slug = models.SlugField(_('slug'), max_length=140, unique=True)
    order = models.PositiveSmallIntegerField(_('ordre'), default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = _('categorie de projet')
        verbose_name_plural = _('categories de projet')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)[:130] or 'categorie'
            slug = base_slug
            index = 2
            while ProjectCategory.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                suffix = f'-{index}'
                slug = f'{base_slug[:140 - len(suffix)]}{suffix}'
                index += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Project(models.Model):
    title = models.CharField(_('titre'), max_length=150)
    slug = models.SlugField(_('slug'), unique=True)
    category = models.ForeignKey(
        ProjectCategory,
        verbose_name=_('categorie'),
        on_delete=models.PROTECT,
        related_name='projects',
    )
    short_description = models.CharField(_('description courte'), max_length=200)
    full_description = CKEditor5Field(_('description complète'))
    challenge = CKEditor5Field(_('problème'), blank=True, help_text=_("Problème client résolu"))
    solution = CKEditor5Field(_('solution'), blank=True, help_text=_("Solution apportée"))
    result = CKEditor5Field(_('résultat'), blank=True, help_text=_("Résultat mesurable ex: +32% conversion"))
    thumbnail = models.ImageField(
        _('miniature'),
        upload_to='projects/thumbnails/',
        validators=[
            FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp']),
            FileSizeValidator(8),
            _validate_image_content,
        ],
        help_text=_("Image recommandée: 1600x1000 px minimum, ratio 16:10, cadrage horizontal propre."),
    )
    demo_video_file = models.FileField(
        _('fichier vidéo de démo'),
        upload_to='projects/videos/',
        blank=True,
        validators=[
            FileExtensionValidator(['mp4', 'webm', 'ogv', 'ogg']),
            FileSizeValidator(50),
        ],
        help_text=_("Vidéo démo uploadée directement (mp4, webm)")
    )
    live_url = models.URLField(_('URL live'), blank=True, help_text=_("Lien vers le projet en ligne"))
    github_url = models.URLField(_('URL GitHub'), blank=True, help_text=_("Lien GitHub du projet"))
    tags = models.CharField(_('tags'), max_length=300, help_text=_("Tags séparés par virgule ex: Python,Django,IA"))
    is_featured = models.BooleanField(_('mis en avant'), default=False, help_text=_("Afficher en avant dans le portfolio"))
    order = models.PositiveSmallIntegerField(_('ordre'), default=0)
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = _('projet')
        verbose_name_plural = _('projets')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('project_detail', args=[self.slug])

    def get_tags_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    def get_visual_tags(self):
        visual_tags = []
        for tag in self.get_tags_list():
            icon, tone = TECH_VISUALS.get(tag.strip().lower(), ('fas fa-cube', 'tech-badge--default'))
            visual_tags.append({
                'label': tag,
                'icon': icon,
                'tone': tone,
            })
        return visual_tags

    def get_primary_visual_tags(self):
        return self.get_visual_tags()[:3]

    @property
    def has_video(self):
        return bool(self.demo_video_file)

    def has_repository_url(self):
        if not self.github_url:
            return False

        host = urlparse(self.github_url).netloc.lower()
        return any(host.endswith(domain) for domain in ('github.com', 'gitlab.com', 'bitbucket.org'))

    def get_public_project_url(self):
        return self.live_url or (self.github_url if self.github_url and not self.has_repository_url() else '')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.thumbnail and hasattr(self.thumbnail, 'path'):
            target_size = (1600, 1000)
            resample = getattr(Image, 'Resampling', Image).LANCZOS
            try:
                with Image.open(self.thumbnail.path) as image:
                    if image.size != target_size:
                        resized = ImageOps.fit(image, target_size, method=resample)
                        format_name = (image.format or 'JPEG').upper()
                        save_kwargs = {}
                        if format_name in ('JPEG', 'JPG'):
                            if resized.mode in ('RGBA', 'P'):
                                resized = resized.convert('RGB')
                            save_kwargs = {'quality': 90, 'optimize': True}
                        elif format_name == 'WEBP':
                            save_kwargs = {'quality': 90}
                        resized.save(self.thumbnail.path, format=format_name, **save_kwargs)
            except (OSError, ValueError):
                pass
        cache.delete('site_profile')

    def delete(self, *args, **kwargs):
        result = super().delete(*args, **kwargs)
        cache.delete('site_profile')
        return result

    def get_video_mime_type(self):
        if not self.demo_video_file:
            return ''

        file_name = self.demo_video_file.name.lower()
        if file_name.endswith('.webm'):
            return 'video/webm'
        if file_name.endswith('.ogg') or file_name.endswith('.ogv'):
            return 'video/ogg'
        return 'video/mp4'


class Testimonial(models.Model):
    author_name = models.CharField(_('nom'), max_length=100)
    author_role = models.CharField(_('fonction'), max_length=150, help_text=_("ex: COO, RetailTech Paris"))
    author_email = models.EmailField(_('email'), blank=True)
    company_name = models.CharField(_('entreprise'), max_length=150, blank=True)
    author_photo = models.ImageField(
        _('photo'),
        upload_to='avatars/',
        blank=True,
        validators=[
            FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp']),
            FileSizeValidator(3),
            _validate_image_content,
        ],
    )
    content = models.TextField(_('contenu'))
    rating = models.PositiveSmallIntegerField(
        _('note'),
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    project = models.ForeignKey(Project, verbose_name=_('projet'), on_delete=models.SET_NULL, null=True, blank=True)
    is_visible = models.BooleanField(_('visible'), default=True)
    order = models.PositiveSmallIntegerField(_('ordre'), default=0)
    submitted_at = models.DateTimeField(_('soumis le'), auto_now_add=True)

    class Meta:
        ordering = ['order', '-submitted_at']
        verbose_name = _('témoignage')
        verbose_name_plural = _('témoignages')

    def __str__(self):
        return f"{self.author_name} — {self.author_role}"


class KPI(models.Model):
    value = models.CharField(_('valeur'), max_length=30, help_text=_("ex: +32%"))
    label = models.CharField(_('libellé'), max_length=150)
    order = models.PositiveSmallIntegerField(_('ordre'), default=0)

    class Meta:
        ordering = ['order']
        verbose_name = _('indicateur')
        verbose_name_plural = _('indicateurs')

    def __str__(self):
        return f"{self.value} — {self.label}"


class ContactMessage(models.Model):
    name = models.CharField(_('nom'), max_length=100)
    email = models.EmailField(_('email'))
    subject = models.CharField(_('sujet'), max_length=200)
    message = models.TextField(_('message'))
    budget = models.CharField(_('budget'), max_length=50, blank=True)
    received_at = models.DateTimeField(_('reçu le'), auto_now_add=True)
    is_read = models.BooleanField(_('lu'), default=False)

    class Meta:
        ordering = ['-received_at']
        verbose_name = _('message de contact')
        verbose_name_plural = _('messages de contact')

    def __str__(self):
        return f"{self.name} — {self.subject}"
