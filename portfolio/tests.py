import json
import tempfile

from django.core.cache import cache
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse

from .forms import ContactForm
from .models import ContactMessage, HeroSlide, KPI, Project, Service, SiteProfile, Skill, Testimonial, Tool


PNG_BYTES = (
	b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
	b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01'
	b'\x0b\xe7\x02\x9d\x00\x00\x00\x00IEND\xaeB`\x82'
)

VIDEO_BYTES = b'RIFF\x24\x00\x00\x00WEBMdemo-video-bytes'


class PortfolioFlowTests(TestCase):
	def setUp(self):
		self.site_profile = SiteProfile.objects.create(
			full_name='Omar Atta Dynamic',
			brand_name='Omar.studio',
			hero_badge_text='Open for premium missions',
			hero_role='Architecte produit',
			hero_highlight='IA, Apps & Cloud',
			hero_description='Un profil entièrement piloté depuis l’admin.',
			email='dynamic@example.com',
			linkedin_url='https://www.linkedin.com/in/dynamic-omar',
			whatsapp_url='https://wa.me/221000000000',
		)
		HeroSlide.objects.create(
			eyebrow='09',
			title='Slide administrable',
			description='Ce contenu vient du back-office.',
			icon='fas fa-sliders',
			theme='teal',
			order=1,
		)
		self.project = Project.objects.create(
			title='Assistant virtuel bancaire',
			slug='assistant-virtuel-bancaire',
			category='ia',
			short_description='Assistant IA multicanal pour support client.',
			full_description='Une plateforme omnicanale pour automatiser le support.',
			thumbnail=SimpleUploadedFile('thumb.png', PNG_BYTES, content_type='image/png'),
			tags='Python,Django,AWS'
		)

	def test_home_page_loads(self):
		response = self.client.get(reverse('home'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Projets')
		self.assertContains(response, 'Réalisations')
		self.assertIn('category_groups', response.context)
		self.assertContains(response, 'data-filter="ia"', html=False)
		self.assertContains(response, 'project-item-card', html=False)
		self.assertContains(response, 'project-tags-row', html=False)
		self.assertContains(response, 'project-tag-pill', html=False)
		self.assertContains(response, 'Omar Atta Dynamic')
		self.assertContains(response, 'Slide administrable')
		self.assertContains(response, 'dynamic@example.com')

	def test_about_page_loads(self):
		response = self.client.get(reverse('about'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'À propos')
		self.assertContains(response, 'Omar Atta Dynamic')

	def test_references_page_loads(self):
		response = self.client.get(reverse('references'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Références clients & résultats IA')
		self.assertContains(response, 'Impact mesurable')

	def test_process_page_loads(self):
		response = self.client.get(reverse('process'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Processus de livraison IA & logiciel')

	def test_project_detail_page_uses_visual_showcase(self):
		response = self.client.get(reverse('project_detail', args=[self.project.slug]))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'pd-hero', html=False)
		self.assertContains(response, 'À propos du projet')
		self.assertContains(response, 'pd-img-wrap', html=False)

	def test_project_detail_prefers_uploaded_video_file(self):
		self.project.demo_video_file = SimpleUploadedFile('demo.webm', VIDEO_BYTES, content_type='video/webm')
		self.project.save(update_fields=['demo_video_file'])

		response = self.client.get(reverse('project_detail', args=[self.project.slug]))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '<video', html=False)
		self.assertContains(response, '.webm')
		self.assertNotContains(response, '<iframe', html=False)

	def test_contact_form_persists_message(self):
		response = self.client.post(
			reverse('contact'),
			{
				'name': 'Client Afrique',
				'email': 'client@example.com',
				'subject': 'Mission IA',
				'budget': '1500€ - 5000€',
				'message': 'Nous voulons un assistant virtuel.'
			},
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
			HTTP_ACCEPT='application/json'
		)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(ContactMessage.objects.count(), 1)

	@override_settings(
		EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
		DEFAULT_FROM_EMAIL='fallback@example.com',
		CONTACT_RECIPIENT_EMAIL='fallback-recipient@example.com',
	)
	def test_contact_form_uses_dynamic_admin_email_settings(self):
		self.site_profile.mail_from_email = 'admin-sender@example.com'
		self.site_profile.contact_recipient_email = 'admin-recipient@example.com'
		self.site_profile.smtp_username = 'admin-sender@example.com'
		self.site_profile.smtp_app_password = 'demo-app-password'
		self.site_profile.save()

		response = self.client.post(
			reverse('contact'),
			{
				'name': 'Client Afrique',
				'email': 'client@example.com',
				'subject': 'Mission IA',
				'budget': ContactForm.BUDGET_CHOICES[3][0],
				'message': 'Nous voulons un assistant virtuel.'
			},
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
			HTTP_ACCEPT='application/json'
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(mail.outbox), 1)
		self.assertEqual(mail.outbox[0].from_email, 'admin-sender@example.com')
		self.assertEqual(mail.outbox[0].to, ['admin-recipient@example.com'])

	def test_sitemap_lists_projects(self):
		response = self.client.get(reverse('sitemap'))
		self.assertEqual(response.status_code, 200)
		self.assertIn('application/xml', response['Content-Type'])
		self.assertContains(response, 'assistant-virtuel-bancaire')

	def test_robots_txt_blocks_admin_and_media(self):
		response = self.client.get(reverse('robots_txt'))
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response['Content-Type'], 'text/plain')
		content = response.content.decode()
		self.assertIn('Disallow: /admin/', content)
		self.assertIn('Disallow: /media/', content)
		self.assertIn('Sitemap:', content)

	def test_home_seo_meta_tags_present(self):
		response = self.client.get(reverse('home'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '<meta name="description"', html=False)
		self.assertContains(response, 'og:title', html=False)
		self.assertContains(response, 'og:image', html=False)
		self.assertContains(response, 'application/ld+json', html=False)
		self.assertContains(response, 'rel="canonical"', html=False)

	def test_home_uses_google_settings_from_site_profile(self):
		self.site_profile.google_analytics_id = 'G-TEST123456'
		self.site_profile.google_site_verification = 'google-site-code'
		self.site_profile.save()

		response = self.client.get(reverse('home'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'G-TEST123456')
		self.assertContains(response, 'google-site-code')

	def test_project_detail_seo_uses_project_data(self):
		response = self.client.get(reverse('project_detail', args=[self.project.slug]))
		self.assertContains(response, 'Assistant virtuel bancaire')
		self.assertContains(response, 'Assistant IA multicanal pour support client.')
		self.assertContains(response, 'og:image', html=False)

	def test_contact_form_invalid_returns_400(self):
		response = self.client.post(
			reverse('contact'),
			{'name': '', 'email': 'pas-un-email', 'subject': '', 'message': ''},
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
			HTTP_ACCEPT='application/json',
		)
		self.assertEqual(response.status_code, 400)
		payload = json.loads(response.content)
		self.assertEqual(payload['status'], 'error')
		self.assertIn('email', payload['errors'])
		self.assertEqual(ContactMessage.objects.count(), 0)

	def test_contact_rate_limit_blocks_after_threshold(self):
		cache.clear()
		rate_key = 'contact_rate_1.2.3.4'
		cache.set(rate_key, 3, timeout=3600)  # simuler 3 soumissions déjà faites
		response = self.client.post(
			reverse('contact'),
			{'name': 'Test', 'email': 'test@example.com', 'subject': 'Sujet', 'message': 'Message.'},
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
			HTTP_ACCEPT='application/json',
			REMOTE_ADDR='1.2.3.4',
		)
		self.assertEqual(response.status_code, 429)
		payload = json.loads(response.content)
		self.assertEqual(payload['status'], 'error')

	def test_testimonial_rating_out_of_range_rejected(self):
		response = self.client.post(
			reverse('submit_testimonial'),
			{
				'author_name': 'Test',
				'author_email': 'test@example.com',
				'author_role': 'CEO',
				'rating': 99,
				'content': 'Super mission.',
			},
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
			HTTP_ACCEPT='application/json',
		)
		self.assertEqual(response.status_code, 400)
		self.assertEqual(Testimonial.objects.count(), 0)

	def test_project_detail_404_on_unknown_slug(self):
		response = self.client.get(reverse('project_detail', args=['slug-inexistant']))
		self.assertEqual(response.status_code, 404)

	def test_site_profile_cache_invalidated_on_save(self):
		cache.clear()
		self.site_profile.full_name = 'Omar Atta Updated'
		self.site_profile.save()
		response = self.client.get(reverse('home'))
		self.assertContains(response, 'Omar Atta Updated')


class PortfolioRegressionTests(TestCase):
	def setUp(self):
		self.site_profile = SiteProfile.objects.create(
			full_name='Omar Atta Dynamic',
			brand_name='Omar.studio',
			hero_role='Architecte produit',
			hero_highlight='IA, Apps & Cloud',
			hero_description='Un profil pilote depuis l admin.',
			email='dynamic@example.com',
		)

	def test_offline_page_loads(self):
		response = self.client.get(reverse('offline'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Mode hors ligne')

	def test_contact_form_increments_rate_limit_for_ajax(self):
		response = self.client.post(
			reverse('contact'),
			{
				'name': 'Client Afrique',
				'email': 'client@example.com',
				'subject': 'Mission IA',
				'budget': '',
				'message': 'Nous voulons un assistant virtuel.'
			},
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
			HTTP_ACCEPT='application/json'
		)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(cache.get('contact_rate_127.0.0.1'), 1)

	def test_testimonial_form_increments_rate_limit_for_ajax(self):
		response = self.client.post(
			reverse('submit_testimonial'),
			{
				'author_name': 'Client Test',
				'author_email': 'client@example.com',
				'author_role': 'CEO',
				'rating': 5,
				'content': 'Super mission.',
			},
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
			HTTP_ACCEPT='application/json',
		)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(cache.get('testimonial_rate_127.0.0.1'), 1)

	def test_service_slug_is_generated_when_missing(self):
		service = Service.objects.create(
			title='Conseil IA Sur Mesure',
			description='Une offre de conseil claire.',
		)
		self.assertEqual(service.slug, 'conseil-ia-sur-mesure')

	def test_service_detail_uses_uploaded_video_mime_type(self):
		service = Service.objects.create(
			title='Audit Cloud',
			description='Optimisation et migration cloud.',
			demo_video_file=SimpleUploadedFile('demo.webm', VIDEO_BYTES, content_type='video/webm'),
		)
		response = self.client.get(reverse('service_detail', args=[service.slug]))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'video/webm')


class SeedPortfolioCommandTests(TestCase):
	def test_seed_portfolio_creates_showcase_data(self):
		with tempfile.TemporaryDirectory() as media_root:
			with override_settings(MEDIA_ROOT=media_root):
				call_command('seed_portfolio')

		self.assertGreaterEqual(Project.objects.count(), 5)
		self.assertGreaterEqual(Service.objects.count(), 4)
		self.assertGreaterEqual(Skill.objects.count(), 4)
		self.assertGreaterEqual(Tool.objects.count(), 4)
		self.assertGreaterEqual(KPI.objects.count(), 4)
		self.assertGreaterEqual(Testimonial.objects.filter(is_visible=True).count(), 3)


class PWATests(TestCase):
	"""Tests pour la Progressive Web App"""
	
	def test_manifest_json_file_exists(self):
		"""Le fichier manifest.json existe dans le système de fichiers"""
		import os
		from django.conf import settings
		manifest_path = os.path.join(settings.STATICFILES_DIRS[0], 'manifest.json')
		self.assertTrue(os.path.exists(manifest_path))
		
	def test_manifest_json_content(self):
		"""Le manifest contient les champs obligatoires"""
		import os
		import json
		from django.conf import settings
		manifest_path = os.path.join(settings.STATICFILES_DIRS[0], 'manifest.json')
		
		with open(manifest_path, 'r') as f:
			manifest = json.load(f)
		
		self.assertIn('name', manifest)
		self.assertIn('short_name', manifest)
		self.assertIn('start_url', manifest)
		self.assertIn('display', manifest)
		self.assertIn('icons', manifest)
		
	def test_service_worker_file_exists(self):
		"""Le fichier service worker existe dans le système de fichiers"""
		import os
		from django.conf import settings
		sw_path = os.path.join(settings.STATICFILES_DIRS[0], 'js', 'sw.js')
		self.assertTrue(os.path.exists(sw_path))
		
	def test_service_worker_content(self):
		"""Le service worker contient le code nécessaire"""
		import os
		from django.conf import settings
		sw_path = os.path.join(settings.STATICFILES_DIRS[0], 'js', 'sw.js')
		
		with open(sw_path, 'r', encoding='utf-8') as f:
			content = f.read()
		
		# Vérifier les fonctionnalités clés du service worker
		self.assertIn('addEventListener', content)
		self.assertIn('fetch', content)
		self.assertIn('caches', content)
		
	def test_home_page_template_includes_pwa_setup(self):
		"""Le template de base inclut la configuration PWA"""
		from django.template import Template, Context
		from django.template.loader import get_template
		
		template = get_template('portfolio/base.html')
		content = template.template.source
		
		# Vérifier que le manifest est référencé
		self.assertIn('manifest.json', content)
		# Vérifier que le service worker est enregistré
		self.assertIn('serviceWorker', content)
		# Vérifier les meta tags Apple
		self.assertIn('apple-mobile-web-app', content)


class CSPReportTests(TestCase):
	"""Tests pour le endpoint CSP report"""
	
	def test_csp_report_accepts_post(self):
		"""Le endpoint CSP report accepte les POST"""
		csp_data = {
			'csp-report': {
				'document-uri': 'https://example.com/',
				'violated-directive': "script-src 'self'",
				'blocked-uri': 'https://malicious.com/script.js',
			}
		}
		response = self.client.post(
			reverse('csp_report'),
			data=json.dumps(csp_data),
			content_type='application/csp-report'
		)
		self.assertEqual(response.status_code, 204)
		
	def test_csp_report_rejects_get(self):
		"""Le endpoint CSP report rejette les GET"""
		response = self.client.get(reverse('csp_report'))
		self.assertEqual(response.status_code, 405)
		
	def test_csp_report_handles_invalid_json(self):
		"""Le endpoint gère les JSON invalides"""
		response = self.client.post(
			reverse('csp_report'),
			data='invalid json',
			content_type='application/csp-report'
		)
		self.assertEqual(response.status_code, 400)
