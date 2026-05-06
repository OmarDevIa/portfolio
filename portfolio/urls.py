from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('a-propos/', views.about, name='about'),
    path('references/', views.references, name='references'),
    path('processus/', views.process, name='process'),
    path('offline/', views.offline, name='offline'),
    path('service/<slug:slug>/', views.service_detail, name='service_detail'),
    path('projet/<slug:slug>/', views.project_detail, name='project_detail'),
    path('contact/', views.contact, name='contact'),
    path('avis-client/', views.submit_testimonial, name='submit_testimonial'),
]
