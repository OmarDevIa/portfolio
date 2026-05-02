from django.core.management.base import BaseCommand

from portfolio.models import Tool

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


class Command(BaseCommand):
    help = 'Met a jour les outils pour la section Outils & Plateformes.'

    def handle(self, *args, **options):
        for icon, color, title, description, order in TOOLS:
            Tool.objects.update_or_create(
                title=title,
                defaults={
                    'icon': icon,
                    'icon_class': color,
                    'description': description,
                    'order': order,
                },
            )
        self.stdout.write(self.style.SUCCESS('Outils mis a jour.'))
