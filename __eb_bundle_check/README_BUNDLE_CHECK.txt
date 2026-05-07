# Instructions pour vérifier le contenu du bundle déployé sur Elastic Beanstalk

1. Décompressez le dernier fichier ZIP du dossier .elasticbeanstalk/app_versions/ (le plus récent, par exemple : app-1932-260507_015636821529-stage-260507_015636821571.zip).
2. Vérifiez que les fichiers suivants sont bien présents à la racine du ZIP :
   - application.py
   - Procfile
   - manage.py
   - portfolio_site/
   - portfolio/
3. Ouvrez application.py dans le ZIP et vérifiez qu’il contient bien :
   from portfolio_site.wsgi import application
4. Ouvrez le Procfile et vérifiez qu’il contient bien :
   web: gunicorn portfolio_site.wsgi:application --bind 0.0.0.0:8000

Si application.py n’est pas à la racine du ZIP, Elastic Beanstalk ne pourra pas le trouver et utilisera la config par défaut, causant l’erreur.

Si tout est correct dans le ZIP, mais l’erreur persiste, il faudra forcer EB à utiliser le Procfile (et non la config par défaut) ou vérifier la plateforme EB (Python 3.11, etc.).

Pour toute question, envoyez-moi le contenu du ZIP ou la liste des fichiers à la racine.