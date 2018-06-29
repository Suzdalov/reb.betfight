from django import forms
from .models import Bets, Match

class BetForm(forms.ModelForm):
    class Meta:
        model = Bets
        fields = ('betHomeScore', 'betGuestScore',)
