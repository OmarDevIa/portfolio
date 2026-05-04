"""
Command pour optimiser les images du portfolio (conversion WebP, compression)
"""
import os
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from PIL import Image
import io


class Command(BaseCommand):
    help = 'Optimise les images du portfolio en convertissant en WebP et en compressant'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche les images qui seraient optimisées sans les modifier',
        )
        parser.add_argument(
            '--quality',
            type=int,
            default=85,
            help='Qualité de compression WebP (1-100, défaut: 85)',
        )
        parser.add_argument(
            '--max-width',
            type=int,
            default=1920,
            help='Largeur maximale des images (défaut: 1920)',
        )
        parser.add_argument(
            '--max-height',
            type=int,
            default=1080,
            help='Hauteur maximale des images (défaut: 1080)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        quality = options['quality']
        max_width = options['max_width']
        max_height = options['max_height']

        media_root = Path(settings.MEDIA_ROOT)
        
        if not media_root.exists():
            raise CommandError(f'Le dossier media n\'existe pas: {media_root}')

        # Extensions à traiter
        image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
        
        optimized_count = 0
        converted_count = 0
        total_savings = 0

        self.stdout.write(f'Recherche d\'images dans {media_root}...')

        for ext in image_extensions:
            for img_path in media_root.rglob(f'*{ext}'):
                if 'optimized' in str(img_path).lower():
                    continue
                    
                original_size = img_path.stat().st_size
                
                try:
                    with Image.open(img_path) as img:
                        # Vérifier si redimensionnement nécessaire
                        needs_resize = img.width > max_width or img.height > max_height
                        
                        if needs_resize:
                            # Calculer le ratio pour garder les proportions
                            ratio = min(max_width / img.width, max_height / img.height)
                            new_size = (int(img.width * ratio), int(img.height * ratio))
                            img = img.resize(new_size, Image.Resampling.LANCZOS)
                        
                        # Convertir en WebP
                        webp_path = img_path.with_suffix('.webp')
                        
                        # Skip if webp already exists and is newer
                        if webp_path.exists():
                            continue
                        
                        if dry_run:
                            self.stdout.write(
                                self.style.WARNING(f'[DRY RUN] {img_path.name} -> {webp_path.name}')
                            )
                            optimized_count += 1
                            continue
                        
                        # Sauvegarder en WebP
                        img.save(webp_path, 'WEBP', quality=quality)
                        
                        new_size = webp_path.stat().st_size
                        savings = original_size - new_size
                        savings_percent = (savings / original_size) * 100
                        total_savings += savings
                        
                        converted_count += 1
                        
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'{img_path.name} -> {webp_path.name} '
                                f'({self._format_size(original_size)} -> {self._format_size(new_size)} '
                                f'-{savings_percent:.1f}%)'
                            )
                        )
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Erreur avec {img_path.name}: {e}')
                    )

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'\nMode simulation: {optimized_count} images auraient été optimisées.'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n{converted_count} images converties en WebP. '
                    f'Économie totale: {self._format_size(total_savings)}'
                )
            )

    def _format_size(self, size_bytes):
        """Formate une taille en octets en unité lisible"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f'{size_bytes:.1f}{unit}'
            size_bytes /= 1024.0
        return f'{size_bytes:.1f}TB'