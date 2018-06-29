import csv
from .models import Team, Event, Match
import uuid
from datetime import datetime


def csv_dict_reader(file_obj):
    """
    Read a CSV file using csv.DictReader
    """
    ret = []
    reader = csv.DictReader(file_obj, delimiter=',')
    n = 0
    for line in reader:
        ret.append([])
        ret[n].append(line["name"])
        ret[n].append(line["shortname"])
        n=n+1
    return ret


def load1():
    ret = []
    with open("fifa2018/static/data.csv", encoding="utf-8") as f_obj:
        ret = csv_dict_reader(f_obj)
    return ret


def load_team():
    evRef = Event.objects.get(code='FIFA2018')
    # теперь почистим команды
    Team.objects.filter(event_ref=evRef).delete()
    with open("fifa2018/static/team.csv", encoding="utf-8") as f_obj:
        reader = csv.DictReader(f_obj, delimiter=';')
        for line in reader:
            t = Team.objects.create(groupLetter=(line["Group"]), event_ref=evRef, name=(line["Name"]),
                                    shortName=line["ShortName"], unique_id=uuid.uuid4())
    return


def load_match():
    evRef = Event.objects.get(code='FIFA2018')
    # теперь почистим команды
    Match.objects.filter(event_ref= evRef).delete()
    with open("fifa2018/static/match.csv", encoding="utf-8") as f_obj:
        reader = csv.DictReader(f_obj, delimiter=';')
        for line in reader:
            dateMatch = datetime.strptime((line["Date"]), '%d.%m.%Y, %H:%M')
            tmA = Team.objects.get(name=line["TeamA"])
            tmB = Team.objects.get(name=line["TeamB"])
            m = Match.objects.create(unique_id=uuid.uuid4(),
                                     dateStart=dateMatch,
                                     event_ref=evRef,
                                     teamHome=tmA,
                                     teamGuest=tmB,
                                     isOver=False,
                                     title="Группа "+tmA.groupLetter)
    return
#14.06.2018, 18:00

#    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
#    dateStart = models.DateTimeField(default=timezone.now)
#    event_ref = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='fromMatch')
#    teamHome = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='teamA')
#    teamGuest = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='teamB')