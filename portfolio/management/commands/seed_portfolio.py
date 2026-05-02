from io import BytesIO

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from PIL import Image

from portfolio.models import KPI, Project, Service, Skill, Testimonial, Tool


SHOWCASE_PROJECTS = [
    {
        'title': 'Plateforme IA pour service client panafricain',
        'slug': 'plateforme-ia-service-client-panafricain',
        'category': 'ia',
        'short_description': 'Assistant virtuel multilingue connecté au CRM pour réduire les temps de réponse et augmenter la conversion.',
        'full_description': 'Conception d’un assistant virtuel intelligent branché à une base documentaire, CRM et tableaux de bord métier afin de traiter les demandes clients 24/7.',
        'challenge': 'Des équipes support saturées, des réponses incohérentes et une perte de prospects hors horaires ouvrés.',
        'solution': 'Architecture Django + APIs + orchestration IA avec routage omnicanal, supervision et fallback humain.',
        'result': '+38% de leads qualifiés et -62% de temps moyen de réponse.',
        'tags': 'Python,Django,LLM,RAG,AWS,API',
        'live_url': 'https://omaratta.dev/case-studies/assistant-ia',
        'github_url': '',
        'is_featured': True,
        'order': 1,
        'color': (19, 86, 125),
    },
    {
        'title': 'Application mobile de logistique terrain',
        'slug': 'application-mobile-logistique-terrain',
        'category': 'mobile',
        'short_description': 'App Flutter offline-first pour équipes terrain, collecte de preuves et synchronisation cloud sécurisée.',
        'full_description': 'Développement d’une application mobile conçue pour des opérations terrain avec remontée de photos, signatures et données métier, même avec connectivité faible.',
        'challenge': 'Des opérations dispersées sur plusieurs pays avec une couverture réseau inégale et peu de visibilité en temps réel.',
        'solution': 'Application mobile Flutter, API sécurisée, synchro différée et tableau de bord opérationnel centralisé.',
        'result': '-47% d’erreurs de remontée et +31% de productivité des superviseurs.',
        'tags': 'Flutter,Mobile,API,Offline,Sync',
        'live_url': 'https://omaratta.dev/case-studies/mobile-logistique',
        'github_url': '',
        'is_featured': True,
        'order': 2,
        'color': (225, 110, 48),
    },
    {
        'title': 'Suite e-commerce et automatisation commerciale',
        'slug': 'suite-ecommerce-automatisation-commerciale',
        'category': 'web',
        'short_description': 'Plateforme web avec tunnel de vente, scoring de leads et automatisation marketing pour accélérer les signatures.',
        'full_description': 'Refonte complète du dispositif digital commercial avec expérience e-commerce fluide, relances automatisées et suivi des performances par segment.',
        'challenge': 'Des prospects perdus entre WhatsApp, email et formulaires sans suivi unifié.',
        'solution': 'Portail Django, intégration paiement, workflows automatisés et tableaux de conversion pour piloter les campagnes.',
        'result': '+29% de conversion et +52% de vitesse de traitement des leads.',
        'tags': 'Django,E-commerce,Automation,CRM,Payments',
        'live_url': 'https://omaratta.dev/case-studies/ecommerce-suite',
        'github_url': '',
        'is_featured': True,
        'order': 3,
        'color': (31, 129, 106),
    },
    {
        'title': 'Infrastructure cloud AWS pour produit SaaS',
        'slug': 'infrastructure-cloud-aws-produit-saas',
        'category': 'automation',
        'short_description': 'Architecture AWS, CI/CD, observabilité et sécurité pour faire passer un SaaS de MVP à scale-up.',
        'full_description': 'Industrialisation de l’infrastructure d’une plateforme SaaS avec déploiement automatisé, monitoring, haute disponibilité et réduction du risque opérationnel.',
        'challenge': 'Une base technique fragile, des déploiements manuels et une disponibilité insuffisante pour des clients B2B.',
        'solution': 'Stack AWS sécurisée, pipelines CI/CD, logs centralisés et stratégie de reprise.',
        'result': '99,9% de disponibilité et -41% de coût opérationnel cloud optimisé.',
        'tags': 'AWS,Docker,CI/CD,Cloud,Monitoring',
        'live_url': 'https://omaratta.dev/case-studies/aws-saas',
        'github_url': '',
        'is_featured': False,
        'order': 4,
        'color': (64, 57, 153),
    },
    {
        'title': 'ERP léger pour réseau de distribution',
        'slug': 'erp-leger-reseau-distribution',
        'category': 'erp',
        'short_description': 'Solution métier sur mesure pour centraliser stocks, commandes, équipes et reporting de direction.',
        'full_description': 'Création d’un logiciel de gestion dédié à un réseau de distribution avec tableaux de bord temps réel et automatisation des processus critiques.',
        'challenge': 'Des opérations pilotées sur tableurs, sans vue consolidée sur les stocks et la performance commerciale.',
        'solution': 'ERP web sur mesure avec rôles, workflows, reporting multi-sites et exports décisionnels.',
        'result': '-55% de temps administratif et meilleure fiabilité des décisions commerciales.',
        'tags': 'ERP,CRM,Django,Analytics,Operations',
        'live_url': 'https://omaratta.dev/case-studies/erp-distribution',
        'github_url': '',
        'is_featured': False,
        'order': 5,
        'color': (148, 74, 44),
    },
]


SERVICES = [
    ('fas fa-brain', 'Solutions IA & assistants virtuels', 'Conception de copilotes, chatbots, RAG, automatisation documentaire et agents métier.', 1),
    ('fas fa-laptop-code', 'Ingénierie logicielle sur mesure', 'Applications web robustes, ERP, CRM et plateformes métier centrées sur la performance.', 2),
    ('fas fa-mobile-screen-button', 'Applications mobiles business', 'Apps Android/iOS orientées terrain, opérations, ventes et expérience client.', 3),
    ('fab fa-aws', 'Cloud AWS & industrialisation', 'Architecture, déploiement, observabilité, sécurité et montée en charge de produits digitaux.', 4),
]

SKILLS = [
    ('ia', 'fas fa-robot', 'Intelligence artificielle appliquée', 'LLM, RAG, agents, NLP, automatisation et intégration métier.', 95, 1),
    ('web', 'fas fa-layer-group', 'Django & plateformes web', 'Backends métiers, APIs, e-commerce, tableaux de bord et architecture produit.', 93, 2),
    ('mobile', 'fas fa-mobile-alt', 'Mobile cross-platform', 'Flutter, expérience offline-first et intégration services cloud.', 88, 3),
    ('automation', 'fas fa-cloud', 'Cloud AWS & DevOps', 'Déploiement, CI/CD, monitoring, sécurité et optimisation des coûts.', 90, 4),
]

TOOLS = [
    ('fa-brands fa-python', '#3776ab', 'Python & IA', 'Flask, Django, FastAPI, TensorFlow, PyTorch', 1),
    ('fa-brands fa-js', '#f7df1e', 'Front-End JS', 'TypeScript, React, Next.js, Angular, Vite', 2),
    ('fa-solid fa-server', '#6b7280', 'Back-End & APIs', 'Laravel, Symfony, Node.js, Express, REST', 3),
    ('fa-solid fa-mobile-screen-button', '#6366f1', 'Mobile & Cross-Platform', 'Flutter, Dart, Kotlin, Swift, Firebase', 4),
    ('fa-solid fa-store', '#0ea5e9', 'CMS & E-commerce', 'WordPress, Shopify, Strapi, Webflow', 5),
    ('fa-solid fa-database', '#14b8a6', 'Donnees & Bases', 'PostgreSQL, MySQL, SQLite, Prisma ORM', 6),
    ('fa-brands fa-docker', '#2496ed', 'DevOps & Containers', 'Docker, Kubernetes, CI/CD, Nginx', 7),
    ('fa-solid fa-cloud', '#0f766e', 'Cloud & Collaboration', 'IBM Cloud, AWS, Render, Git & GitHub', 8),
]

KPIS = [
    ('+38%', 'Leads qualifiés générés sur un dispositif IA', 1),
    ('99,9%', 'Disponibilité obtenue sur une infra cloud AWS', 2),
    ('-62%', 'Temps moyen de réponse support automatisé', 3),
    ('+31%', 'Productivité terrain sur application mobile', 4),
]

TESTIMONIALS = [
    ('Mariam Fofana', 'Directrice générale', 'Nova Retail', 'Omar a structuré notre plateforme IA et notre tunnel digital avec un vrai sens du résultat. Nous avons signé plus vite et mieux.', 5, 1),
    ('Jean-Baptiste K.', 'CTO', 'Fintech Growth', 'Très solide sur l’architecture, l’exécution et la qualité des livrables. Rare de trouver ce niveau de polyvalence IA, backend et cloud.', 5, 2),
    ('Awa Sarr', 'Responsable opérations', 'LogiMove Africa', 'L’application mobile et les automatisations ont transformé nos opérations terrain en quelques semaines.', 5, 3),
]


def create_png(name, color):
    image = Image.new('RGB', (1400, 900), color)
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    return ContentFile(buffer.getvalue(), name=name)


class Command(BaseCommand):
    help = 'Crée un portfolio de démonstration premium avec projets, services, KPIs et avis clients.'

    @transaction.atomic
    def handle(self, *args, **options):
        projects = []
        for item in SHOWCASE_PROJECTS:
            data = item.copy()
            color = data.pop('color')
            project, created = Project.objects.update_or_create(
                slug=data['slug'],
                defaults=data,
            )
            if not project.thumbnail:
                project.thumbnail.save(f"{project.slug}.png", create_png(f"{project.slug}.png", color), save=False)
                project.save(update_fields=['thumbnail'])
            projects.append(project)
            self.stdout.write(self.style.SUCCESS(f"Projet prêt: {project.title}"))

        for icon, title, description, order in SERVICES:
            Service.objects.update_or_create(
                title=title,
                defaults={'icon': icon, 'description': description, 'order': order},
            )

        for category, icon, title, description, level, order in SKILLS:
            Skill.objects.update_or_create(
                title=title,
                defaults={
                    'category': category,
                    'icon': icon,
                    'description': description,
                    'level': level,
                    'order': order,
                },
            )

        for icon, icon_class, title, description, order in TOOLS:
            Tool.objects.update_or_create(
                title=title,
                defaults={
                    'icon': icon,
                    'icon_class': icon_class,
                    'description': description,
                    'order': order,
                },
            )

        for value, label, order in KPIS:
            KPI.objects.update_or_create(
                label=label,
                defaults={'value': value, 'order': order},
            )

        for author_name, author_role, company_name, content, rating, order in TESTIMONIALS:
            Testimonial.objects.update_or_create(
                author_name=author_name,
                content=content,
                defaults={
                    'author_role': author_role,
                    'company_name': company_name,
                    'rating': rating,
                    'order': order,
                    'is_visible': True,
                    'project': projects[min(order - 1, len(projects) - 1)],
                },
            )

        self.stdout.write(self.style.SUCCESS('Portfolio premium généré avec succès.'))