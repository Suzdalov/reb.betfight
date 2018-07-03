from django.db import models
import uuid
from django.utils import timezone


# Create your models here.
class ResultModel(models.Model):
    teamHomeScore = models.IntegerField
    teamGuestScore = models.IntegerField

    class Meta:
        abstract = True


class Event(models.Model):
    code = models.CharField(max_length=36)
    short_name = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    descr = models.TextField()

    def __str__(self):
        return self.name


class Team(models.Model):
    event_ref = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='fromTeam')
    shortName = models.CharField(max_length=3)
    name = models.CharField(max_length=150)
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    groupLetter = models.CharField(max_length=1, blank=True)

    def __str__(self):
        return self.shortName


class Match(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    dateStart = models.DateTimeField(default=timezone.now)
    event_ref = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='fromMatch')
    title = models.CharField(null=True,blank=True,max_length=60)
    teamHome = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='teamA')
    teamGuest = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='teamB')
    baseHomeScore = models.PositiveIntegerField(null=True, blank=True)
    baseGuestScore = models.PositiveIntegerField(null=True, blank=True)
    totalHomeScore = models.PositiveIntegerField(null=True, blank=True)
    totalGuestScore = models.PositiveIntegerField(null=True, blank=True)
    koeffHome = models.FloatField(null=True, blank=True)
    koeffDraw = models.FloatField(null=True, blank=True)
    koeffGuest = models.FloatField(null=True, blank=True)
    isOver = models.BooleanField(default=False)

    def __str__(self):
        return self.teamHome.name + ' vs ' + self.teamGuest.name


class Player(models.Model):
    NickName = models.CharField(max_length=40, blank=True)
    UsrRef = models.ForeignKey('auth.User', on_delete=models.CASCADE)


class Party (models.Model):
    Name = models.CharField(max_length=40, blank=True)


class PartyMembers(models.Model):
    partyRef = models.ForeignKey('Party', on_delete=models.CASCADE, related_name='fromPartyArray')
    Participant = models.ForeignKey('Player', on_delete=models.CASCADE, related_name='fromPartyArray')


class Bets(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey('Player', on_delete=models.CASCADE, related_name="formBets")
    match = models.ForeignKey('Match', on_delete=models.CASCADE, related_name="formBets")
    betHomeScore = models.PositiveIntegerField(null=True, blank=True)
    betGuestScore = models.PositiveIntegerField(null=True, blank=True)
    points = models.IntegerField(null=True, blank=True)
    money = models.FloatField(null=True, blank=True)
    isEdited = models.BooleanField(default=False)

    def __str__(self):
        return self.user.NickName + '/' + self.match.teamHome.name + ' vs ' + self.match.teamGuest.name