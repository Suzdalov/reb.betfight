from django.contrib import admin

# Register your models here.


from .models import Event, Player, Match, Bets, Team

admin.site.register(Event)
admin.site.register(Player)
admin.site.register(Match)
admin.site.register(Bets)
admin.site.register(Team)
