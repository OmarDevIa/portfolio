import xml.etree.ElementTree as ET

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_POST
from django.urls import reverse

from .models import HeroSlide, KPI, Project, Service, SiteProfile, Skill, Testimonial, Tool
from .forms import ContactForm, TestimonialForm

_CONTACT_RATE_LIMIT = 3  # max submissions per window
_CONTACT_RATE_WINDOW = 3600  # 1 hour in seconds
_TESTIMONIAL_RATE_LIMIT = 3
_TESTIMONIAL_RATE_WINDOW = 3600


def _get_site_profile():
    """
    name : get_site_profile
    description : Récupère le profil du site depuis le cache ou la base de données
    author : Ingénieur Omar Atta
    date : 2024-06-01
    
    """
    profile = cache.get('site_profile')
    if profile is None:
        profile = SiteProfile.objects.first() or SiteProfile()
        cache.set('site_profile', profile, timeout=3600)
    return profile


def _get_hero_slides():
    """
    name : get_hero_slides
    description : Retourne les slides hero actifs ou des valeurs par defaut.
    author : Ingenieur Omar Atta
    date : 2024-06-01

    """
    slides = list(HeroSlide.objects.filter(is_active=True))
    if slides:
        return slides
    return [
        HeroSlide(eyebrow='01', title='Produits logiciels', description='Des plateformes métier premium pensées pour la conversion et la vitesse d’exécution.', icon='fas fa-rocket', theme='burnt'),
        HeroSlide(eyebrow='02', title='IA & assistants virtuels', description='Des expériences intelligentes utiles, visibles et immédiatement différenciantes.', icon='fas fa-brain', theme='teal'),
        HeroSlide(eyebrow='03', title='Mobile & AWS', description='Une couche cloud et mobile robuste pour scaler proprement en Afrique et à l’international.', icon='fas fa-cloud-arrow-up', theme='light'),
    ]


def _build_seo_context(request, project=None):
    """
    name : build_seo_context
    description : Construit le contexte SEO pour les pages du site.
    author : Ingenieur Omar Atta
    date : 2024-06-01

    """
    canonical_url = request.build_absolute_uri()
    seo_context = {
        'canonical_url': canonical_url,
        'og_url': canonical_url,
        'site_url': getattr(settings, 'SITE_URL', '').rstrip('/') or request.build_absolute_uri('/').rstrip('/'),
        'github_profile_url': getattr(settings, 'GITHUB_PROFILE_URL', ''),
        'google_analytics_id': getattr(settings, 'GOOGLE_ANALYTICS_ID', ''),
        'google_analytics_dashboard_url': getattr(settings, 'GOOGLE_ANALYTICS_DASHBOARD_URL', ''),
        'google_site_verification': getattr(settings, 'GOOGLE_SITE_VERIFICATION', ''),
    }
    if project and getattr(project, 'thumbnail', None):
        seo_context['project_og_image_url'] = request.build_absolute_uri(project.thumbnail.url)
    return seo_context


def _wants_json(request):
    """
    name : wants_json
    description : Determine si la requete attend une reponse JSON.
    author : Ingenieur Omar Atta
    date : 2024-06-01

    """
    accept = request.headers.get('Accept', '')
    requested_with = request.headers.get('X-Requested-With', '')
    return 'application/json' in accept or requested_with == 'XMLHttpRequest'


def _build_home_context(request, contact_form=None, testimonial_form=None):
    """
    name : build_home_context
    description : Assemble toutes les donnees necessaires pour les pages publiques.
    author : Ingenieur Omar Atta
    date : 2024-06-01

    """
    site_profile = _get_site_profile()
    projects = Project.objects.all()
    category_groups = []
    for value, label in Project.CATEGORY_CHOICES:
        grouped_projects = projects.filter(category=value)
        if grouped_projects.exists():
            category_groups.append({
                'value': value,
                'label': label,
                'projects': grouped_projects,
                'count': grouped_projects.count(),
            })

    cert_total = site_profile.certification_badges.count()
    if site_profile.primary_certificate_label:
        cert_total += 1
    if site_profile.secondary_certificate_label:
        cert_total += 1

    context = {
        'projects': projects,
        'featured': projects.filter(is_featured=True),
        'skills': Skill.objects.all(),
        'services': Service.objects.all(),
        'tools': Tool.objects.all(),
        'testimonials': Testimonial.objects.filter(is_visible=True),
        'kpis': KPI.objects.all(),
        'form': contact_form or ContactForm(),
        'testimonial_form': testimonial_form or TestimonialForm(),
        'categories': Project.CATEGORY_CHOICES,
        'category_groups': category_groups,
        'site_profile': site_profile,
        'hero_slides': _get_hero_slides(),
        'cert_total': cert_total,
    }
    context.update(_build_seo_context(request))
    return context


def home(request):
    """
    name : home
    description : Affiche la page d'accueil.
    author : Ingenieur Omar Atta
    date : 2024-06-01

    """
    context = _build_home_context(request)
    return render(request, 'portfolio/home.html', context)


def about(request):
    """
    name : about
    description : Affiche la page a propos.
    author : Ingenieur Omar Atta
    date : 2024-06-01

    """
    context = _build_home_context(request)
    return render(request, 'portfolio/about.html', context)


def references(request):
    """
    name : references
    description : Affiche la page des references.
    author : Ingenieur Omar Atta
    date : 2024-06-01

    """
    context = _build_home_context(request)
    return render(request, 'portfolio/references.html', context)


def process(request):
    """
    name : process
    description : Affiche la page du processus.
    author : Ingenieur Omar Atta
    date : 2024-06-01

    """
    context = _build_home_context(request)
    return render(request, 'portfolio/process.html', context)


def project_detail(request, slug):
    """
    name : project_detail
    description : Affiche le detail d'un projet.
    author : Ingenieur Omar Atta
    date : 2024-06-01

    """
    project = get_object_or_404(Project, slug=slug)
    related = Project.objects.filter(category=project.category).exclude(pk=project.pk)[:3]
    context = {
        'project': project,
        'related': related,
        'form':    ContactForm(),
        'site_profile': _get_site_profile(),
    }
    context.update(_build_seo_context(request, project=project))
    return render(request, 'portfolio/project_detail.html', context)


@require_POST
def contact(request):
    """
    name : contact
    description : Traite l'envoi du formulaire de contact.
    author : Ingenieur Omar Atta
    date : 2024-06-01

    """
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '')).split(',')[0].strip()
    rate_key = f'contact_rate_{ip}'
    try:
        submissions = cache.get_or_set(rate_key, 0, timeout=_CONTACT_RATE_WINDOW)
        if submissions >= _CONTACT_RATE_LIMIT:
            msg = 'Trop de tentatives. Réessayez dans une heure.'
            if _wants_json(request):
                return JsonResponse({'status': 'error', 'message': msg}, status=429)
            context = _build_home_context(request)
            context['contact_error_message'] = msg
            return render(request, 'portfolio/home.html', context, status=429)
    except Exception:
        submissions = 0
        rate_key = None

    form = ContactForm(request.POST)
    if form.is_valid():
        msg = form.save()
        email_sent = bool(settings.DEFAULT_FROM_EMAIL and settings.CONTACT_RECIPIENT_EMAIL)
        try:
            if email_sent:
                send_mail(
                    subject=f"[Portfolio] {msg.subject}",
                    message=(
                        f"De : {msg.name} <{msg.email}>\n"
                        f"Budget : {msg.budget or 'Non précisé'}\n\n"
                        f"{msg.message}"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.CONTACT_RECIPIENT_EMAIL],
                    fail_silently=False,
                )
        except Exception:
            email_sent = False
        response_message = 'Message enregistré avec succès !'
        if email_sent:
            response_message = 'Message envoyé avec succès !'
        elif not (settings.DEFAULT_FROM_EMAIL and settings.CONTACT_RECIPIENT_EMAIL):
            response_message = 'Message enregistré. Configurez l’email serveur pour recevoir les notifications.'
        if _wants_json(request):
            return JsonResponse({'status': 'ok', 'message': response_message})
        if rate_key:
            cache.set(rate_key, submissions + 1, timeout=_CONTACT_RATE_WINDOW)
        cache.set(rate_key, submissions + 1, timeout=_CONTACT_RATE_WINDOW)
        context = _build_home_context(request)
        context['contact_success_message'] = response_message
        return render(request, 'portfolio/home.html', context)
    if _wants_json(request):
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    context = _build_home_context(request, contact_form=form)
    return render(request, 'portfolio/home.html', context, status=400)


@require_POST
def submit_testimonial(request):
    """
    name : submit_testimonial
    description : Enregistre un avis client et applique un rate limit.
    author : Ingenieur Omar Atta
    date : 2024-06-01

    """
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '')).split(',')[0].strip()
    rate_key = f'testimonial_rate_{ip}'
    try:
        submissions = cache.get_or_set(rate_key, 0, timeout=_TESTIMONIAL_RATE_WINDOW)
        if submissions >= _TESTIMONIAL_RATE_LIMIT:
            msg = 'Trop de tentatives. Réessayez dans une heure.'
            if _wants_json(request):
                return JsonResponse({'status': 'error', 'message': msg}, status=429)
            context = _build_home_context(request)
            context['testimonial_error_message'] = msg
            return render(request, 'portfolio/home.html', context, status=429)
    except Exception:
        submissions = 0
        rate_key = None

    form = TestimonialForm(request.POST, request.FILES)
    if form.is_valid():
        form.save()
        response_message = 'Merci. Votre avis a bien été reçu et sera publié après validation par l’administrateur.'
        if _wants_json(request):
            return JsonResponse({
                'status': 'ok',
                'message': response_message
            })
        if rate_key:
            cache.set(rate_key, submissions + 1, timeout=_TESTIMONIAL_RATE_WINDOW)
        context = _build_home_context(request, testimonial_form=TestimonialForm())
        context['testimonial_success_message'] = response_message
        return render(request, 'portfolio/home.html', context)
    if _wants_json(request):
        return JsonResponse({
            'status': 'error',
            'errors': form.errors
        }, status=400)
    context = _build_home_context(request, testimonial_form=form)
    return render(request, 'portfolio/home.html', context, status=400)


def robots_txt(request):
    """
    name : robots_txt
    description : Fournit le fichier robots.txt du site.
    author : Ingenieur Omar Atta
    date : 2024-06-01

    """
    lines = [
        'User-agent: *',
        'Allow: /',
        'Disallow: /admin/',
        'Disallow: /media/',
        f'Sitemap: {request.build_absolute_uri(reverse("sitemap"))}',
        f'Sitemap: {request.build_absolute_uri(reverse("sitemap_images"))}',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain')


def sitemap_images(request):
    """
    name : sitemap_images
    description : Genere le sitemap XML des images de projets.
    author : Ingenieur Omar Atta
    date : 2024-06-01

    """
    urlset = ET.Element(
        'urlset',
        {
            'xmlns': 'http://www.sitemaps.org/schemas/sitemap/0.9',
            'xmlns:image': 'http://www.google.com/schemas/sitemap-image/1.1',
        },
    )
    for project in Project.objects.exclude(thumbnail=''):
        url = ET.SubElement(urlset, 'url')
        loc = ET.SubElement(url, 'loc')
        loc.text = request.build_absolute_uri(project.get_absolute_url())
        image = ET.SubElement(url, 'image:image')
        image_loc = ET.SubElement(image, 'image:loc')
        image_loc.text = request.build_absolute_uri(project.thumbnail.url)
        image_title = ET.SubElement(image, 'image:title')
        image_title.text = project.title

    xml_bytes = ET.tostring(urlset, encoding='utf-8', xml_declaration=True)
    return HttpResponse(xml_bytes, content_type='application/xml')


def _build_error_context(request, code, title, message):
    """
    name : build_error_context
    description : Prepare le contexte pour les pages d'erreur.
    author : Ingenieur Omar Atta
    date : 2024-06-01

    """
    return {
        'error_code': code,
        'error_title': title,
        'error_message': message,
        'error_path': getattr(request, 'path', ''),
    }


def bad_request(request, exception=None):
    """
    name : bad_request
    description : Affiche la page 400 (requete invalide).
    author : Ingenieur Omar Atta
    date : 2024-06-01

    """
    context = _build_error_context(
        request,
        400,
        'Requete invalide',
        "La requete n'a pas pu etre traitee.",
    )
    return render(request, '400.html', context, status=400)


def permission_denied(request, exception=None):
    """
    name : permission_denied
    description : Affiche la page 403 (acces refuse).
    author : Ingenieur Omar Atta
    date : 2024-06-01

    """
    context = _build_error_context(
        request,
        403,
        'Acces refuse',
        "Vous n'avez pas les droits pour acceder a cette page.",
    )
    return render(request, '403.html', context, status=403)


def page_not_found(request, exception=None):
    """
    name : page_not_found
    description : Affiche la page 404 (page introuvable).
    author : Ingenieur Omar Atta
    date : 2024-06-01

    """
    context = _build_error_context(
        request,
        404,
        'Page introuvable',
        "La page demandee n'existe pas ou a ete deplacee.",
    )
    return render(request, '404.html', context, status=404)


def server_error(request):
    """
    name : server_error
    description : Affiche la page 500 (erreur serveur).
    author : Ingenieur Omar Atta
    date : 2024-06-01

    """
    context = _build_error_context(
        request,
        500,
        'Erreur serveur',
        "Une erreur interne est survenue. Reessayez plus tard.",
    )
    return render(request, '500.html', context, status=500)
