# Contribution Guide

## Workflow

1. Create a feature branch from `main`.
2. Keep changes focused and documented.
3. Run checks before opening a pull request.
4. Open a PR with context, screenshots if UI changed, and validation notes.

## Local checks

```bash
python manage.py check
python manage.py test
```

## Documentation

Any change affecting setup, deployment, admin behavior, URLs or environment variables should update:

- `README.md`
- `docs/DEPLOIEMENT.md` if deployment is affected
- `docs/CAHIER_DES_CHARGES.md` if scope changes

## Pull request expectations

- short summary
- affected areas
- migration note if applicable
- rollback note if risk exists
