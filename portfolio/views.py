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


def _get_site_profile():
    profile = cache.get('site_profile')
    if profile is None:
        profile = SiteProfile.objects.first() or SiteProfile()
        cache.set('site_profile', profile, timeout=3600)
    return profile


def _get_hero_slides():
    slides = list(HeroSlide.objects.filter(is_active=True))
    if slides:
        return slides
    return [
        HeroSlide(eyebrow='01', title='Produits logiciels', description='Des plateformes métier premium pensées pour la conversion et la vitesse d’exécution.', icon='fas fa-rocket', theme='burnt'),
        HeroSlide(eyebrow='02', title='IA & assistants virtuels', description='Des expériences intelligentes utiles, visibles et immédiatement différenciantes.', icon='fas fa-brain', theme='teal'),
        HeroSlide(eyebrow='03', title='Mobile & AWS', description='Une couche cloud et mobile robuste pour scaler proprement en Afrique et à l’international.', icon='fas fa-cloud-arrow-up', theme='light'),
    ]


def _build_seo_context(request, project=None):
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
    accept = request.headers.get('Accept', '')
    requested_with = request.headers.get('X-Requested-With', '')
    return 'application/json' in accept or requested_with == 'XMLHttpRequest'


def _build_home_context(request, contact_form=None, testimonial_form=None):
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
    context = _build_home_context(request)
    return render(request, 'portfolio/home.html', context)


def about(request):
    context = _build_home_context(request)
    return render(request, 'portfolio/about.html', context)


def references(request):
    context = _build_home_context(request)
    return render(request, 'portfolio/references.html', context)


def process(request):
    context = _build_home_context(request)
    return render(request, 'portfolio/process.html', context)


def project_detail(request, slug):
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
    form = TestimonialForm(request.POST, request.FILES)
    if form.is_valid():
        form.save()
        response_message = 'Merci. Votre avis a bien été reçu et sera publié après validation par l’administrateur.'
        if _wants_json(request):
            return JsonResponse({
                'status': 'ok',
                'message': response_message
            })
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
    lines = [
        'User-agent: *',
        'Allow: /',
        'Disallow: /admin/',
        'Disallow: /media/',
        f'Sitemap: {request.build_absolute_uri(reverse("sitemap"))}',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain')
