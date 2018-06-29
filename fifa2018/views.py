from django.shortcuts import render, redirect, get_object_or_404
from .models import Event, Player, Bets, Match
from django.db.models import Q
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .etl import load1, load_team, load_match, load_match2
from .forms import BetForm
from .main_lib import player_rank, calc_scores, fullrep2
import uuid
import datetime
from datetime import timedelta
from django.views.generic.edit import FormView
from django.contrib.auth.forms import UserCreationForm


def ifnull(var, val):
  if var is None:
    return val
  return var


class RegisterFormView(FormView):
    form_class = UserCreationForm

    # Ссылка, на которую будет перенаправляться пользователь в случае успешной регистрации.
    # В данном случае указана ссылка на страницу входа для зарегистрированных пользователей.
    success_url = "/fifa2018/"

    # Шаблон, который будет использоваться при отображении представления.
    template_name = "register.html"

    def form_valid(self, form):
        # Создаём пользователя, если данные в форму были введены корректно.
        form.save()

        # Вызываем метод базового класса
        return super(RegisterFormView, self).form_valid(form)



# Create your views here.


def home1(request):
    return redirect('cockpit')
    # return render(request, 'home.html', {})


def schedule(request):
    return render(request, 'schedule.html', {})

@login_required
def admin(request):
    return render(request, 'admin.html', {})

@login_required
def setdata1(request):
    if 'q' in request.GET:
        if request.GET['q'] == "Event":
            message = 'попросили обновить Event'
        elif request.GET['q'] == "LoadTeam":
            load_team()
            message = 'команды подгружены'
        elif request.GET['q'] == "LoadMatch":
            load_match()
            message = 'матчи подгружены'
        elif request.GET['q'] == "LoadMatch2":
            load_match2()
            message = 'матчи2 подгружены'
        elif request.GET['q'] == "Calc":
            message = calc_scores()
        else:
            message = 'попросили обновить хезе %r' % request.GET['q']
    else:
        message = 'You submitted an empty form.'
    # Create a new record using the model's constructor.
    a_record = Event(code="FIFA2018")
    # Save the object into the database.
    a_record.short_name = "ЧМФ 2018"
    a_record.descr = "Чемпионат мира по футболу 2018 в России"
    a_record.name = "Чемпионат мира по футболу 2018 в России"
#    a_record.save()
#    message = "все в порядке"
    return HttpResponse(message)
#    return render(request, 'home.html', {})

#@login_required(redirect_field_name='ref_url')
@login_required
def cockpit(request):
    # запилим список участников
    # получаем всех игроков
    res1 = player_rank()
    # теперь ближайшие игры
    dt = datetime.date.today()
    all_games = Match.objects.order_by('dateStart')
    all_games = all_games.filter(dateStart__gte=dt, dateStart__lte=dt + timedelta(days=2))
    #all_games = all_games.filter(isOver=False)[:6]
    res2 = []
    n = 0
    for gm1 in all_games:
        res2.append([])
        res2[n].append(gm1.dateStart)
        res2[n].append(gm1.teamHome.name)
        res2[n].append(gm1.teamGuest.name)
        n = n+1
    # покажем список команд
    dt = datetime.date.today()
    #dt = datetime.datetime(dt.year, dt.month, dt.day)
    dateFrom = dt - timedelta(days=1)
    dateTo = dt + timedelta(days=1)
    res3 = fullrep2(dateFrom, dateTo)
    v_games = Match.objects.filter(dateStart__gte=dateFrom, dateStart__lte=dateTo)
    v_games = v_games.order_by('dateStart')
    return render(request, 'cockpit.html', {'res1': res1, 'res2': res2, 'res3' : res3, 'v_games' : v_games, 'all_games' : all_games})


def auth(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        # Redirect to a success page.
    else:
        return render(request, 'auth.html', {})
        # Return an 'invalid login' error message.


@login_required
def betlist(request):
    all_games = Match.objects.order_by('dateStart')
    all_games = all_games.filter(isOver=False)[:12]
    res2 = []
    n = 0
    v_gamer = get_object_or_404(Player, UsrRef=request.user)
    #v_gamer = Player.objects.get(UsrRef=request.user)
    for gm1 in all_games:
        # создадим список ставок, если их нет
        cur_bet, created = Bets.objects.get_or_create(user=v_gamer, match=gm1,
                                                  defaults={'unique_id': uuid.uuid4, 'betHomeScore':0, 'betGuestScore':0,'points':0, 'money':0, 'isEdited':False})
        res2.append([])
        res2[n].append(gm1.dateStart)
        res2[n].append(gm1.teamHome.name)
        res2[n].append(gm1.teamGuest.name)
        res2[n].append(cur_bet.unique_id)
        res2[n].append(str(cur_bet.betHomeScore)+' : '+str(cur_bet.betGuestScore))
        n = n + 1
    return render(request, 'bet_list.html', {'res2': res2})
#    return redirect('../')


@login_required
def bet(request, betid):
    bet = get_object_or_404(Bets, unique_id=betid)
    if request.method == "POST":
        form = BetForm(request.POST, instance=bet)
        if form.is_valid():
            if bet.match.isOver == True:
                return redirect('betList')
                # ничего не сохраняем - время вышло
            v_gamer = get_object_or_404(Player, UsrRef=request.user)
            if bet.user != v_gamer:
                return redirect('betList')
#            bet = form.save(commit=False)
#            bet.betHomeScore = request.user
#            post.published_date = timezone.now()
            bet.isEdited = True
            bet.save()
            return redirect('betList')
    else:
        form = BetForm(instance=bet)
        #найдем игры соперников
        v_games_home = Match.objects.filter(teamHome=bet.match.teamHome) | Match.objects.filter(teamGuest=bet.match.teamHome)
        v_games_home = v_games_home.filter(isOver=True)
        v_games_home = v_games_home.order_by('dateStart')
        v_games_guest = Match.objects.filter(teamHome=bet.match.teamGuest) | Match.objects.filter(
            teamGuest=bet.match.teamGuest)
        v_games_guest = v_games_guest.filter(isOver=True)
        v_games_guest = v_games_guest.order_by('dateStart')
    return render(request, 'bet_edit.html', {'form': form, 'bet':bet, 'v_games_home': v_games_home, 'v_games_guest':v_games_guest})
#    return redirect('../')

@login_required
def fullreport(request):
    # соберем всю жару
    # сначала наших чемпионов
    v_gamers = player_rank()
    games_arr = []
    v_games = Match.objects.order_by('dateStart')
    # сохраним в массив
    n = 0
    for v_gamer in v_gamers:
        games_arr.append([])
        games_arr[n].append(v_gamer[0])
        games_arr[n].append(v_gamer[1])
        games_arr[n].append(v_gamer[2])
        games_arr[n].append(v_gamer[3])
        #v_player = Player.objects.get(id=v_gamer[4])
        for v_game in v_games:
            v_cur_bet, created = Bets.objects.get_or_create(user=v_gamer[4], match=v_game,
                                                          defaults={'unique_id': uuid.uuid4, 'betHomeScore': 0,
                                                                    'betGuestScore': 0, 'points': 0, 'money': 0,
                                                                    'isEdited': False})
            if v_game.isOver:
                games_arr[n].append(str(v_cur_bet.betHomeScore)+":"+str(v_cur_bet.betGuestScore))
            else:
                if v_cur_bet.isEdited is True:
                    games_arr[n].append("***")
                else:
                    games_arr[n].append("...")
        n = n + 1
    return render(request, 'fullreport.html', {'v_games': v_games, 'v_bets': games_arr})




