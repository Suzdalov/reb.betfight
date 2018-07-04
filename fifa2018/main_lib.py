from .models import Bets, Player, Match
import uuid
import datetime
from .etl import stDate



def ifnull(var, val):
  if var is None:
    return val
  return var


def player_rank():
    # запилим список участников
    # получаем всех игроков
    res1 = []
    n = 0
    all_players = Player.objects.all()
    for item in all_players:
        res1.append([])
        res1[n].append(0)
        # посчитаем очки
        sum1 = 0
        money1 = 0
        player_games = Bets.objects.filter(user=item)
        for i1 in player_games:
            sum1 = sum1 + ifnull(i1.points, 0)
            money1 = money1 + ifnull(i1.money, 0)
        res1[n].append(sum1)
        res1[n].append(money1)
        res1[n].append(item.NickName)
        res1[n].append(item)
        n = n + 1
    # сортанем по очкам
    res1.sort(reverse=True)
    m = 1
    for i1 in res1:
        i1[0] = m
        m = m + 1
    return res1

def calc_scores():
    dateFrom = stDate()
    v_games = Match.objects.filter(isOver=True, dateStart__gte=dateFrom)
    v_ret = "Пересчет:"
    for v_game in v_games:
        if v_game.baseHomeScore is None or v_game.baseGuestScore is None:
            v_ret = v_ret + "пустые результаты по игре "+ v_game.teamHome.name + v_game.teamGuest.name
            continue
        v_players = Player.objects.all()
        for v_player in v_players:
            cur_bet, created = Bets.objects.get_or_create(user=v_player, match=v_game,
                                                          defaults={'unique_id': uuid.uuid4, 'betHomeScore': 0,
                                                                    'betGuestScore': 0, 'points': 0, 'money': 0,
                                                                    'isEdited': False})
            v_scr1 = ifnull(cur_bet.betHomeScore, 0)
            v_scr2 = ifnull(cur_bet.betGuestScore, 0)
            v_point = 0
            v_money = 0.0
            #а теперь жаришка со сравнением
            if v_scr1 == v_game.baseHomeScore and v_scr2 == v_game.baseGuestScore:
                v_point = 4
            elif v_scr1-v_scr2 == v_game.baseHomeScore-v_game.baseGuestScore:
                v_point = 3
            elif (v_scr1 > v_scr2 and v_game.baseHomeScore > v_game.baseGuestScore) or (v_scr1 < v_scr2 and v_game.baseHomeScore < v_game.baseGuestScore) :
                v_point = 2
            else:
                v_point = 0

            if v_point != 0:
                if v_game.baseHomeScore > v_game.baseGuestScore:
                    v_money = 100 * ifnull(v_game.koeffHome, 1)
                elif v_game.baseHomeScore == v_game.baseGuestScore:
                    v_money = 100 * ifnull(v_game.koeffDraw, 1)
                else:
                    v_money = 100 * ifnull(v_game.koeffGuest, 1)
            cur_bet.points = v_point
            cur_bet.money = v_money-100
            cur_bet.save()
    v_ret = v_ret+" посчитано"
    return v_ret

def get_three_dates():
    all_games = Match.objects.order_by('dateStart')
    all_games = all_games.filter(isOver=False)
    cur_date = datetime.datetime.now().date()
    for v_game in all_games:
        cur_date = datetime.datetime.v_game.dateStart.date()



def fullrep2(dateFrom, dateTo):
    v_gamers = player_rank()
    games_arr = []
    v_games = Match.objects.filter(dateStart__gte=dateFrom, dateStart__lte=dateTo)
    v_games = v_games.order_by('dateStart')
    n = 0
    for v_gamer in v_gamers:
        games_arr.append([])
        games_arr[n].append(v_gamer[0])
        games_arr[n].append(v_gamer[1])
        games_arr[n].append(v_gamer[2])
        games_arr[n].append(v_gamer[3])
        # v_player = Player.objects.get(id=v_gamer[4])
        for v_game in v_games:
            v_cur_bet, created = Bets.objects.get_or_create(user=v_gamer[4], match=v_game,
                                                            defaults={'unique_id': uuid.uuid4, 'betHomeScore': 0,
                                                                      'betGuestScore': 0, 'points': 0, 'money': 0,
                                                                      'isEdited': False})
            if v_game.isOver:
                games_arr[n].append(str(v_cur_bet.betHomeScore) + ":" + str(v_cur_bet.betGuestScore))
            else:
                if v_cur_bet.isEdited is True:
                    games_arr[n].append("***")
                else:
                    games_arr[n].append("...")
        n = n + 1
    return games_arr


def getWinner(score1, score2):
    if score1 > score2:
        return "Home"
    elif score1 < score2:
        return "Guest"
    else:
        return "Draw"