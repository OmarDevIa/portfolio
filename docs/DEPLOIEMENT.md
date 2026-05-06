# Guide de deploiement

## Cible actuelle

Le projet est prepare pour un deploiement simple sur Render avec :

- application web Python
- Gunicorn
- WhiteNoise pour les static files
- stockage `media/` sur disque monte

## Sequence recommandee

1. Creer le service web Render.
2. Connecter le depot GitHub `OmarDevIa/portfolio`.
3. Verifier les commandes du fichier `render.yaml`.
4. Declarer les variables d'environnement.
5. Lancer le premier build.
6. Creer ou verifier le superutilisateur.

## Variables d'environnement minimales

- `SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS`
- `SITE_URL`
- `ADMIN_URL`
- `CSRF_TRUSTED_ORIGINS`

## Variables recommandees

- `CONTACT_RECIPIENT_EMAIL`
- `DEFAULT_FROM_EMAIL`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `SENTRY_DSN`
- `GOOGLE_ANALYTICS_ID`
- `GOOGLE_ANALYTICS_DASHBOARD_URL`
- `GOOGLE_SITE_VERIFICATION`

## Commandes

### Build

```bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
```

### Post-deploiement

```bash
python manage.py migrate
python manage.py check
```

### Start

```bash
gunicorn portfolio_site.wsgi:application --bind 0.0.0.0:$PORT
```

## Points d'attention

- l'URL admin n'est pas `/admin/` mais l'URL personnalisee definie dans `portfolio_site/urls.py`
- `/admin/` est reserve comme leurre HoneyGuard quand `django_honeyguard` est installe
- `/login.php` et `/django-admin/` peuvent aussi etre exposes comme routes pieges selon la configuration
- `django_honeyguard` doit etre installe si l'on veut les pages pieges et le modele admin associe
- `csp` et `sentry_sdk` ne sont actifs que s'ils sont installes et configures
- `DEBUG` doit rester a `False` en production
- `SITE_URL` doit etre defini en HTTPS

## Verification finale

- page d'accueil charge correctement
- pages `a-propos`, `references`, `processus` et `contact` repondent
- admin accessible
- `python manage.py check` sans erreur
- static files servis correctement
- uploads `media/` persistants
