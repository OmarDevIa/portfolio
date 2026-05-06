# Cahier des charges

## 1. Objet

Realiser et maintenir un site portfolio professionnel sous Django pour presenter les services, projets, competences et references de l'activite `Omar.tech`, avec administration complete, experience mobile, SEO fort et niveau de securite adapte a une mise en production.

## 2. Objectifs

- valoriser l'image professionnelle et les expertises IA, logiciel, mobile et cloud
- convertir les visiteurs en prises de contact qualifiees
- permettre une administration simple sans intervention technique quotidienne
- assurer de bonnes performances sur mobile
- garantir un socle SEO et securite solide

## 3. Perimetre fonctionnel

### 3.1 Front office

Le site doit proposer :

- une page d'accueil premium et orientee conversion
- une page `A propos`
- une page `References`
- une page `Processus`
- une page `Contact`
- une page offline pour la PWA
- des pages detail pour chaque projet
- des pages detail pour chaque service
- un formulaire de temoignage

### 3.2 Back office

Le back office doit permettre :

- la gestion du profil principal
- la gestion des slides hero
- la gestion des projets
- la gestion des services
- la gestion des competences
- la gestion des outils
- la gestion des KPI
- la gestion des messages de contact
- la moderation des temoignages
- l'acces a un tableau de bord admin personnalise

### 3.3 Securite et supervision

Le systeme doit inclure :

- une URL admin personnalisee
- une protection CSRF
- des cookies securises en production
- des en-tetes HTTP de securite
- une integration HoneyGuard optionnelle
- une integration Sentry optionnelle
- un endpoint de rapport CSP
- une limitation simple des abus sur les formulaires

## 4. Utilisateurs cibles

- visiteurs prospects
- partenaires
- recruteurs et clients B2B
- administrateur du site

## 5. Exigences fonctionnelles detaillees

### Contenu

- tous les contenus principaux doivent etre administrables depuis Django Admin
- les descriptions riches doivent supporter un editeur WYSIWYG
- les medias doivent accepter images et certains fichiers selon les modeles

### Contact

- le formulaire de contact doit enregistrer les demandes
- le formulaire doit renvoyer des reponses exploitables cote interface
- les soumissions abusives doivent etre limitees

### Temoignages

- un visiteur peut soumettre un temoignage
- la publication doit rester soumise a moderation

### SEO

- chaque page doit exposer des balises meta pertinentes
- le site doit fournir un sitemap XML
- le site doit exposer `robots.txt`
- les pages projet doivent remonter leurs donnees SEO propres

### PWA

- le site doit etre installable
- une page offline doit etre disponible
- les ressources statiques doivent etre compatibles avec un service worker

## 6. Exigences non fonctionnelles

### Performance

- navigation fluide sur mobile
- poids front limite autant que possible
- chargement propre des images

### Responsive design

- le front office doit etre utilisable sur mobile, tablette et desktop
- l'admin doit rester utilisable sur mobile pour les consultations rapides

### Maintenabilite

- code organise par application Django
- documentation de deploiement et d'exploitation disponible
- variables sensibles externalisees dans l'environnement

### Securite

- ne jamais exposer de secret en dur pour la production
- servir le site en HTTPS en production
- durcir la configuration quand `DEBUG=False`

## 7. Architecture technique cible

- framework principal : Django
- base par defaut : SQLite
- serveur WSGI : Gunicorn
- static files : WhiteNoise
- hebergement cible : Render
- administration : Django Admin + Jazzmin
- edition riche : django-ckeditor-5

## 8. Livrables

- code source du projet
- fichier `README.md`
- fichier `.env.example`
- documentation de deploiement
- cahier des charges
- configuration Render

## 9. Criteres d'acceptation

- `python manage.py check` retourne sans erreur
- les migrations s'appliquent correctement
- les pages publiques principales repondent
- le formulaire de contact fonctionne
- l'admin est accessible via l'URL personnalisee
- HoneyGuard apparait dans l'admin si le package est installe et migre
- le site reste exploitable sur mobile

## 10. Evolutions envisageables

- passage a PostgreSQL en production
- ajout d'une API ou d'un headless CMS
- tableau de bord analytics plus avance
- tests frontend automatisees
- pipeline CI/CD GitHub Actions
