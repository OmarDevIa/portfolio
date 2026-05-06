from django import forms
from django.contrib import admin
from django.conf import settings
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.template.response import TemplateResponse
from django.urls import path
from types import MethodType
from django.utils import timezone

from .models import ContactMessage, HeroSlide, KPI, Project, ProjectCategory, Service, SiteProfile, Skill, Testimonial, Tool


class SiteProfileAdminForm(forms.ModelForm):
    class Meta:
        model = SiteProfile
        fields = '__all__'
        widgets = {
            'smtp_app_password': forms.PasswordInput(render_value=True),
        }


def admin_dashboard_view(request):
    site_profile = SiteProfile.objects.first()
    today = timezone.now()
    six_months_ago = today - timezone.timedelta(days=180)

    monthly_messages = list(
        ContactMessage.objects.filter(received_at__gte=six_months_ago)
        .annotate(month=TruncMonth('received_at'))
        .values('month')
        .annotate(total=Count('id'))
        .order_by('month')
    )
    monthly_testimonials = list(
        Testimonial.objects.filter(submitted_at__gte=six_months_ago)
        .annotate(month=TruncMonth('submitted_at'))
        .values('month')
        .annotate(total=Count('id'))
        .order_by('month')
    )
    project_by_category = list(
        Project.objects.values('category').annotate(total=Count('id')).order_by('category')
    )

    categories = list(ProjectCategory.objects.order_by('order', 'name'))
    category_totals_map = {item['category']: item['total'] for item in project_by_category}
    message_lookup = {
        item['month'].strftime('%Y-%m'): item['total']
        for item in monthly_messages
    }
    testimonial_lookup = {
        item['month'].strftime('%Y-%m'): item['total']
        for item in monthly_testimonials
    }

    def add_months(dt, offset):
        month = dt.month - 1 + offset
        year = dt.year + month // 12
        month = month % 12 + 1
        return dt.replace(year=year, month=month, day=1)

    month_anchor = today.replace(day=1)
    month_keys = [add_months(month_anchor, -i).strftime('%Y-%m') for i in range(5, -1, -1)]
    chart_month_labels = [add_months(month_anchor, -i).strftime('%b %Y') for i in range(5, -1, -1)]

    context = {
        **admin.site.each_context(request),
        'title': 'Tableau de bord',
        'admin_base_path': getattr(settings, 'ADMIN_BASE_PATH', '/admin/'),
        'project_count': Project.objects.count(),
        'featured_count': Project.objects.filter(is_featured=True).count(),
        'message_count': ContactMessage.objects.count(),
        'unread_message_count': ContactMessage.objects.filter(is_read=False).count(),
        'category_chart_labels': [category.name for category in categories],
        'category_chart_totals': [category_totals_map.get(category.id, 0) for category in categories],
        'recent_messages': ContactMessage.objects.order_by('-received_at')[:5],
        'recent_testimonials': Testimonial.objects.order_by('-submitted_at')[:5],
        'chart_month_labels': chart_month_labels,
        'chart_message_totals': [message_lookup.get(key, 0) for key in month_keys],
        'chart_testimonial_totals': [testimonial_lookup.get(key, 0) for key in month_keys],
        'google_analytics_dashboard_url': (
            getattr(site_profile, 'google_analytics_dashboard_url', '')
            or getattr(settings, 'GOOGLE_ANALYTICS_DASHBOARD_URL', '')
        ),
        'google_analytics_id': (
            getattr(site_profile, 'google_analytics_id', '')
            or getattr(settings, 'GOOGLE_ANALYTICS_ID', '')
        ),
        'google_site_verification': (
            getattr(site_profile, 'google_site_verification', '')
            or getattr(settings, 'GOOGLE_SITE_VERIFICATION', '')
        ),
        'site_url': getattr(settings, 'SITE_URL', ''),
    }
    return TemplateResponse(request, 'admin/dashboard.html', context)


_default_admin_get_urls = admin.site.get_urls


def _custom_admin_get_urls(self):
    custom_urls = [
        path('tableau-de-bord/', self.admin_view(admin_dashboard_view), name='portfolio_admin_dashboard'),
    ]
    return custom_urls + _default_admin_get_urls()


admin.site.get_urls = MethodType(_custom_admin_get_urls, admin.site)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display  = ('title', 'category', 'is_featured', 'order', 'has_video')
    list_editable = ('is_featured', 'order')
    list_filter   = ('category', 'is_featured')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'tags')
    fieldsets = (
        ('Informations générales', {
            'fields': ('title', 'slug', 'category', 'is_featured', 'order')
        }),
        ('Contenu', {
            'fields': ('short_description', 'full_description', 'challenge', 'solution', 'result')
        }),
        ('Médias', {
            'description': 'Miniature recommandée: 1600x1000 px minimum, ratio 16:10 pour un rendu propre sur cartes et détail projet.',
            'fields': ('thumbnail', 'demo_video_file')
        }),
        ('Liens & Tags', {
            'fields': ('live_url', 'github_url', 'tags')
        }),
    )
@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order')
    list_editable = ('order',)
    prepopulated_fields = {'slug': ('name',)}

    def has_video(self, obj):
        return obj.has_video
    has_video.boolean = True
    has_video.short_description = 'Vidéo démo'


@admin.register(SiteProfile)
class SiteProfileAdmin(admin.ModelAdmin):
    form = SiteProfileAdminForm
    list_display = ('full_name', 'brand_name', 'email')

    fieldsets = (
        ('Identité', {
            'description': 'Photo de profil recommandee: 1200x1500 px minimum, ratio 4:5, cadrage vertical propre avec le visage visible.',
            'fields': ('full_name', 'brand_name', 'profile_photo', 'about_photo', 'cv_file')
        }),
        ('Hero', {
            'fields': ('hero_badge_text', 'hero_role', 'hero_highlight', 'hero_description', 'hero_signals')
        }),
        ('Positionnement', {
            'fields': ('years_experience', 'experience_label', 'impact_value', 'impact_label', 'availability_text')
        }),
        ('À propos', {
            'fields': ('about_title', 'about_intro', 'about_body', 'tech_stack_marquee')
        }),
        ('Preuves & badges', {
            'fields': (
                'primary_badge_text', 'secondary_badge_text', 'secondary_badge_icon',
                'cert_section_title', 'cert_section_desc', 'cert_section_note',
                'primary_certificate_label', 'primary_certificate_url', 'primary_certificate_badge',
                'secondary_certificate_label', 'secondary_certificate_url', 'secondary_certificate_badge',
            )
        }),
        ('Sections home', {
            'fields': (
                'services_section_subtitle', 'services_section_title',
                'skills_section_subtitle', 'skills_section_title',
                'tools_section_subtitle', 'tools_section_title', 'tools_section_desc', 'tools_section_intro',
                'portfolio_section_title', 'portfolio_section_desc',
                'testimonials_section_subtitle', 'testimonials_section_title',
                'contact_section_subtitle', 'contact_section_title',
            )
        }),
        ('Contacts', {
            'fields': ('email', 'whatsapp_url', 'linkedin_url', 'github_url', 'footer_tagline')
        }),
        ('Email & notifications', {
            'fields': (
                'contact_recipient_email',
                'mail_from_email',
                'smtp_username',
                'smtp_app_password',
            )
        }),
        ('SEO & Google', {
            'fields': ('google_analytics_id', 'google_analytics_dashboard_url', 'google_site_verification')
        }),
    )


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ('eyebrow', 'title', 'theme', 'is_active', 'order')
    list_editable = ('theme', 'is_active', 'order')
    list_filter = ('theme', 'is_active')
    search_fields = ('title', 'description')


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display  = ('title', 'category', 'level', 'order')
    list_editable = ('level', 'order')
    list_filter   = ('category',)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display  = ('title', 'slug', 'order')
    list_editable = ('order',)
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        ('Identité', {
            'fields': ('title', 'slug', 'icon', 'order')
        }),
        ('Contenu', {
            'fields': ('description', 'summary', 'full_description', 'detail_points')
        }),
        ('Médias', {
            'fields': ('cover_image', 'secondary_image', 'demo_video_file')
        }),
    )


@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display  = ('title', 'icon_class', 'order')
    list_editable = ('order',)


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display  = ('author_name', 'company_name', 'author_role', 'rating', 'project', 'is_visible', 'order')
    list_editable = ('is_visible', 'order')
    list_filter   = ('is_visible', 'rating', 'project')
    search_fields = ('author_name', 'company_name', 'author_role', 'content')


@admin.register(KPI)
class KPIAdmin(admin.ModelAdmin):
    list_display  = ('value', 'label', 'order')
    list_editable = ('order',)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display  = ('name', 'email', 'subject', 'budget', 'received_at', 'is_read')
    list_editable = ('is_read',)
    list_filter   = ('is_read',)
    readonly_fields = ('name', 'email', 'subject', 'budget', 'message', 'received_at')
