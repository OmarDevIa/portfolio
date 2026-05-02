from django import forms
from .models import ContactMessage, Testimonial


class ContactForm(forms.ModelForm):
    BUDGET_CHOICES = [
        ('', '-- Budget estimé --'),
        ('< 500€', 'Moins de 500€'),
        ('500€ - 1500€', '500€ – 1 500€'),
        ('1500€ - 5000€', '1 500€ – 5 000€'),
        ('> 5000€', 'Plus de 5 000€'),
        ('A définir', 'À définir ensemble'),
    ]
    budget = forms.ChoiceField(choices=BUDGET_CHOICES, required=False,
                               widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'budget', 'message']
        labels = {
            'name': 'Nom',
            'email': 'Adresse email',
            'subject': 'Sujet',
            'message': 'Message',
        }
        widgets = {
            'name':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom'}),
            'email':   forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'votre@email.com'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Objet de votre demande'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5,
                                             'placeholder': 'Décrivez votre projet...'}),
        }


class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ['author_name', 'author_email', 'company_name', 'author_role', 'project', 'rating', 'content']
        labels = {
            'author_name': 'Nom',
            'author_email': 'Email professionnel',
            'company_name': 'Entreprise',
            'author_role': 'Fonction',
            'project': 'Projet concerné',
            'rating': 'Note',
            'content': 'Retour d’expérience',
        }
        help_texts = {
            'author_role': 'Exemple : CEO, CTO, Responsable produit',
        }
        widgets = {
            'author_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom'}),
            'author_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@entreprise.com'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entreprise / organisation'}),
            'author_role': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CEO, CTO, Responsable produit...'}),
            'project': forms.Select(attrs={'class': 'form-select'}),
            'rating': forms.Select(
                choices=[(5, '5/5'), (4, '4/5'), (3, '3/5'), (2, '2/5'), (1, '1/5')],
                attrs={'class': 'form-select'}
            ),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Décrivez les résultats, la qualité de livraison et l’impact business obtenu.'
            }),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.is_visible = False
        if commit:
            instance.save()
        return instance
