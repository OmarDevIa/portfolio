from django import template

from portfolio.models import TECH_VISUALS


register = template.Library()


def _normalize_tag(tag):
    return tag.strip().lower()


@register.filter
def tech_icon(tag):
    return TECH_VISUALS.get(_normalize_tag(tag), ('fas fa-cube', 'tech-badge--default'))[0]


@register.filter
def tech_tone(tag):
    return TECH_VISUALS.get(_normalize_tag(tag), ('fas fa-cube', 'tech-badge--default'))[1]